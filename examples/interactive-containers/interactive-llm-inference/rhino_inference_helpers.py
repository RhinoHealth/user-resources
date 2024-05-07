from typing import Any, Tuple
import logging
import os
import sys
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, PreTrainedTokenizer


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def load_tokenizer_and_model(model_artifacts, device_map) -> Tuple:
    # Instantiate the tokenizer for an LLM and the LLM itself
    tokenizer = AutoTokenizer.from_pretrained(model_artifacts)
    model = AutoModelForCausalLM.from_pretrained(model_artifacts, device_map=device_map, torch_dtype=torch.bfloat16)
    return tokenizer, model


def read_data() -> pd.DataFrame:
    # Read the input data from /input
    data = pd.read_csv("/input/dataset.csv")
    return data


def inference(input_text: str, tokenizer: PreTrainedTokenizer, model: Any) -> str:
    # Performs inference with an LLM model
    chat = [{"role": "user", "content": input_text}, ]
    prompt = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer.encode(prompt, add_special_tokens=False, return_tensors="pt")
    outputs = model.generate(inputs.to(model.device), max_length=8192)
    decoded_outputs = tokenizer.decode(outputs[0])
    decoded_outputs = decoded_outputs.split("<start_of_turn>model")[1]
    decoded_outputs = decoded_outputs.replace("<eos>", "")
    response = "Response: \n\n" + decoded_outputs
    response = response.split("Response:")[1]
    return response


def create_dataset(dataframe: pd.DataFrame) -> None:
    # Create a new dataset in the output directory, so that it can be imported into the FCP as a Dataset
    if os.path.isfile("/output/dataset.csv"):
        logging.debug("Output file exists. Appending new response.")
    else:
        logging.debug("Output file does NOT exist. Creating new file and writing response to it.")
    dataframe.to_csv("/output/dataset.csv", index=False)


def read_output_datasets() -> pd.DataFrame:
    # Reads the output csv file
    df = pd.read_csv("/output/dataset.csv")
    return df
