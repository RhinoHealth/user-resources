import pandas as pd
import logging
import time
import re
import requests
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DiagnosisExtractor:
    def __init__(self, model_name: str = 'gemma3'):
        self.model_name = model_name
        self.base_url = 'http://localhost:11434/api/generate'
        self._verify_local_ollama()

    def _verify_local_ollama(self):
        """Verify local Ollama is running and model is available."""
        try:
            # First check if Ollama is running locally
            response = requests.get('http://localhost:11434/api/version')
            response.raise_for_status()
            
            # Then check if the model is available
            response = requests.post('http://localhost:11434/api/show', 
                                  json={'name': self.model_name})
            if response.status_code == 404:
                raise Exception(f"Model {self.model_name} not found. Please run 'ollama pull {self.model_name}' first.")
            response.raise_for_status()
            
            logging.info(f"Successfully connected to local Ollama with model {self.model_name}")
        except requests.exceptions.ConnectionError:
            raise Exception("Could not connect to Ollama. Is it running locally? Start with 'ollama serve'")
        except Exception as e:
            logging.error(f"Error verifying local Ollama: {e}")
            raise

    def _create_prompt(self, clinical_text: str) -> str:
        """Create the prompt for diagnosis extraction."""
        return f"""Objective: Identify all diagnosis names mentioned in the following clinical text.
Guidelines:
1. Extract only diagnosis names.
2. Extract the entity exactly as written in the note without modification.
3. Only extract diagnoses explicitly listed in the text. Do not infer or add conditions not present.
4. Ignore numeric values unless they are part of a specific diagnosis name (e.g., 'Type 2 Diabetes', 'stage 3').
5. Focus on conditions, diseases, syndromes, and specific medical problems mentioned.
6. Output Format: List the extracted diagnosis names separated by commas. If no diagnoses are found, output "None".

Clinical Text:
---
{clinical_text}
---

Extracted Diagnoses (comma-separated):"""

    def parse_diagnoses(self, model_output: str) -> List[str]:
        """Parse the model's output to extract diagnoses."""
        try:
            # Clean the output and handle direct responses
            extracted_part = model_output.strip()

            # If the marker exists, extract after it
            answer_marker = "Extracted Diagnoses (comma-separated):"
            if answer_marker in extracted_part:
                start_index = extracted_part.index(answer_marker) + len(answer_marker)
                extracted_part = extracted_part[start_index:].strip()

            # Handle newlines
            first_newline = extracted_part.find('\n')
            if first_newline != -1:
                extracted_part = extracted_part[:first_newline].strip()

            # Clean up any special tokens
            extracted_part = re.sub(r'<eos>$|</s>$', '', extracted_part).strip()

            if extracted_part.lower() == 'none':
                return []

            # Split and clean diagnoses
            diagnoses = [diag.strip() for diag in extracted_part.split(',') if diag.strip()]
            # Filter out any medication names (simple heuristic)
            diagnoses = [d for d in diagnoses if d.lower() not in ['aspirin', 'statin', 'plavix']]
            logging.warning(f"Model output: {model_output}")
            return [d for d in diagnoses if d]

        except Exception as e:
            logging.warning(f"Error parsing model output: {e}")
            return []

    def process_text(self, clinical_text: str) -> List[str]:
        """Process a single clinical text and return extracted diagnoses."""
        if not clinical_text or pd.isna(clinical_text) or not clinical_text.strip():
            return []

        prompt = self._create_prompt(clinical_text)
        try:
            response = requests.post(self.base_url, json={
                'model': self.model_name,
                'prompt': prompt,
                'stream': False,
                'raw': True  # Get raw output without formatting
            }, timeout=30)  # Add timeout for local requests
            response.raise_for_status()
            response_json = response.json()
            full_output_text = response_json['response']
            return self.parse_diagnoses(full_output_text)
        except requests.exceptions.Timeout:
            logging.error("Local Ollama request timed out")
            return []
        except Exception as e:
            logging.error(f"Error processing text with local Ollama: {e}")
            return []

def process_file(input_file: str, output_file: str, model_name: str = 'gemma3'):
    """Process an entire input file and save results."""
    try:
        # Initialize extractor
        extractor = DiagnosisExtractor(model_name)
        
        # Read input file
        logging.info(f"Loading input data from: {input_file}")
        df_input = pd.read_csv(input_file)
        required_columns = ['SUBJECT_ID', 'TEXT']
        if not all(col in df_input.columns for col in required_columns):
            raise ValueError("Input CSV must contain 'SUBJECT_ID' and 'TEXT' columns.")

        # Process records
        results = []
        total_records = len(df_input)
        start_time = time.time()

        for index, row in df_input.iterrows():
            patient_id = row['SUBJECT_ID']
            clinical_text = row['TEXT']
            
            logging.info(f"Processing record {index + 1}/{total_records} for patient ID: {patient_id}")
            
            diagnoses = extractor.process_text(clinical_text)
            
            if diagnoses:
                results.extend([{'patient_id': patient_id, 'entity_name': diagnosis} 
                              for diagnosis in diagnoses])

        # Save results
        if results:
            df_output = pd.DataFrame(results)
            df_output.to_csv(output_file, index=False)
            logging.info(f"Saved {len(df_output)} diagnoses to {output_file}")
        else:
            pd.DataFrame(columns=['patient_id', 'entity_name']).to_csv(output_file, index=False)
            logging.info("No diagnoses found. Created empty output file.")

        processing_time = time.time() - start_time
        logging.info(f"Processing completed in {processing_time:.2f} seconds")

    except Exception as e:
        logging.error(f"Error processing file: {e}")
        raise

if __name__ == "__main__":
    # Configuration
    INPUT_FILE = '/input/dataset.csv'
    OUTPUT_FILE = '/output/dataset.csv'
    MODEL_NAME = 'gemma3'

    process_file(INPUT_FILE, OUTPUT_FILE, MODEL_NAME)
