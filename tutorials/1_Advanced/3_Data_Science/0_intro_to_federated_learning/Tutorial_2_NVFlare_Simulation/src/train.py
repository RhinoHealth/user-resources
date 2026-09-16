# (1) Import the NVFlare client
import nvflare.client as flare
import time



from utils.train_util import get_datasets, SimpleClassifier, ClassificationTrainer, get_logger


def train():
    # (2) Initialize NVFlare client
    flare.init()
    
    logger = get_logger()
    site_name = flare.get_site_name()
    # Load local data
    train_loader, test_loader = get_datasets(site_name)
    # Initialize local model
    trainer = ClassificationTrainer(SimpleClassifier())

    # (3) Federated learning loop
    while flare.is_running():
        # (4) Receive global model from server
        global_model = flare.receive()
        
        # Additional code for logging added here to make simulated output look prettier
        if site_name == "site-1":
            if global_model.__dict__['metrics'] is not None:
                logger.info(f"Cross-Site Global Accuracy: {global_model.__dict__['metrics']['global_accuracy']:.3f}\n")
            logger.info(f"Round {global_model.current_round+1}/{global_model.total_rounds} Start")
        else:
            time.sleep(1)
        
        # (5) Update local model with global weights
        trainer.model.load_state_dict(global_model.params)

        # (6) Evaluate global model on local data
        global_model_local_accuracy = trainer.evaluate(test_loader)

        logger.info(f"{site_name.title()} Global Model Local Accuracy: {global_model_local_accuracy:.3f}")
        
        # (7) Train for one epoch on local data
        trainer.train(dataloader=train_loader, epochs=1)
        
        # (8) Package updated model and metrics
        output_model = flare.FLModel(
            params=trainer.model.state_dict(),
            metrics = {"global_accuracy": global_model_local_accuracy}
        )
        
        # (9) Send updated model back to server
        flare.send(output_model)
    

if __name__ == "__main__":
    train()