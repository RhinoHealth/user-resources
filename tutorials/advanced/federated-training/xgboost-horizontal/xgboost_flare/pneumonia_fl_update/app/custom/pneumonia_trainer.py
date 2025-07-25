from nvflare.client.api import fl_client
from custom.pneumonia_trainer_class import PneumoniaTrainer

if __name__ == "__main__":
    fl_client.run(client=PneumoniaTrainer())