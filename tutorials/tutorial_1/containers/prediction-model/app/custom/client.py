from rhino_health.client import Client
from app.custom.pneumonia_trainer import PneumoniaTrainer

with Client() as client:
    trainer = PneumoniaTrainer(lr=0.01, epochs=5, test_split=0.2)
    trainer.prepare_data()
    client.set_dataset_summary(
        name="training",
        num_examples=len(trainer.train_loader.dataset),
    )
    client.set_dataset_summary(
        name="validation",
        num_examples=len(trainer.test_loader.dataset),
    )

    # Training
    trainer.set_weights(client.get_weights())
    trainer.train()
    client.log_metrics(
        name="local_train",
        metrics={},  # add per-epoch metrics here if you wish
        round=client.current_round,
    )
    client.set_weights(trainer.get_weights())

    # Evaluation
    val_loss = trainer.evaluate()
    client.log_metrics(
        name="eval",
        metrics={"loss": val_loss},
        round=client.current_round,
    )
