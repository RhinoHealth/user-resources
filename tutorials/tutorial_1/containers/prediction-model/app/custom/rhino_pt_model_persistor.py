import datetime
import pandas as pd
from pathlib import Path

from nvflare.apis.fl_context import FLContext
from nvflare.app_common.abstract.model import ModelLearnable
from nvflare.app_opt.pt.file_model_persistor import PTFileModelPersistor


class PTFileModelPersistorAllCheckpoints(PTFileModelPersistor):
    # Used for creating multiple model params files
    def save_model(self, ml: ModelLearnable, fl_ctx: FLContext):
        super().save_model(ml, fl_ctx)
        
        # Create output directory structure
        dest_dir = Path("/output")
        file_data_dir = dest_dir / "file_data"
        dest_dir.mkdir(parents=False, exist_ok=True)
        file_data_dir.mkdir(parents=True, exist_ok=True)
        
        timestr = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")
        
        # Save model files in BOTH locations for compatibility
        model_filename = f"model_parameters_{timestr}.pt"
        checkpoint_filename = f"checkpoint_{timestr}.pt"
        
        # Save in file_data subdirectory (for dataset registration)
        self.save_model_file(f"{file_data_dir}/{model_filename}")
        self.save_model_file(f"{file_data_dir}/{checkpoint_filename}")
        
        # ALSO save in root output directory (for inference compatibility)
        self.save_model_file(f"{dest_dir}/{checkpoint_filename}")
        self.save_model_file(f"{dest_dir}/model_parameters.pt")  # Standard name
        
        self.logger.info(f"Saved model files to both {file_data_dir}/ and {dest_dir}/")
        
        # Create the required dataset.csv file (for output dataset registration)
        self._create_output_dataset_csv(dest_dir, model_filename, checkpoint_filename, timestr)
    
    def _create_output_dataset_csv(self, output_dir: Path, model_filename: str, checkpoint_filename: str, timestr: str):
        """Create the required dataset.csv file that Rhino platform looks for"""
        try:
            # Create a simple CSV with model information
            model_info = {
                "Filename": [
                    f"file_data/{model_filename}",
                    f"file_data/{checkpoint_filename}",
                    checkpoint_filename,  # Also list the root files
                    "model_parameters.pt"
                ],
                "Type": ["model_parameters", "checkpoint", "checkpoint_root", "model_root"],
                "Created": [timestr, timestr, timestr, timestr],
                "Description": [
                    "Trained pneumonia model parameters", 
                    "Trained pneumonia model checkpoint",
                    "Checkpoint file in root (for inference)",
                    "Standard model file (for inference)"
                ]
            }
            
            # Create DataFrame and save as CSV in root output directory
            df = pd.DataFrame(model_info)
            csv_path = output_dir / "dataset.csv"
            df.to_csv(csv_path, index=False)
            
            self.logger.info(f"Created output dataset.csv at {csv_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to create output dataset.csv: {e}")
            # Don't fail the training if dataset creation fails
            pass