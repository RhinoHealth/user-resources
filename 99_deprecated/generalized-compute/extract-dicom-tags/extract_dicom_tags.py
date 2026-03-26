import csv
import json
from dataclasses import dataclass
from pathlib import Path

import funcy
import pydicom


@dataclass(frozen=True)
class RunParams:
    dicom_id_field: str
    dicom_id_attribute: str
    tags_to_extract: list[str]


def main():
    run_params_file_path = Path("/input/run_params.json")
    with run_params_file_path.open("rb") as f:
        run_params_dict = json.load(f)

    run_params = RunParams(**run_params_dict)
    if not (
        isinstance(run_params.tags_to_extract, list)
        and all(isinstance(field_name, str) for field_name in run_params.tags_to_extract)
    ):
        raise TypeError("tags_to_extract must be an array of strings.")

    print(
        f"Will select DICOM datasets by tag {run_params.dicom_id_attribute}, "
        f"matching with dataset field {run_params.dicom_id_field}."
    )
    print("Extracting DICOM tags: " + ", ".join(run_params.tags_to_extract))

    dicom_input_dir_path = Path("/input/dicom_data")
    dicom_file_paths = list(dicom_input_dir_path.rglob("*.[dD][cC][mM]"))
    dicoms = [pydicom.dcmread(file_path) for file_path in dicom_file_paths]

    print(f"Read {len(dicoms)} DICOM files from {str(dicom_input_dir_path)}.")

    id2dicom = {dcm[run_params.dicom_id_attribute].value: dcm for dcm in dicoms}

    def add_fields(row):
        dicom = id2dicom.get(row[run_params.dicom_id_field])
        if dicom is None:
            extracted = {tag_name: None for tag_name in run_params.tags_to_extract}
        else:
            extracted = {tag_name: dicom.get(tag_name) for tag_name in run_params.tags_to_extract}
        new_row = {**row, **extracted}
        return new_row

    with Path("/input/dataset.csv").open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        input_field_names = reader.fieldnames
        input_data = list(reader)

    output_field_names = funcy.ldistinct([*input_field_names, *run_params.tags_to_extract])
    output_data = [add_fields(row) for row in input_data]

    output_csv_path = Path("/output/dataset.csv")
    with output_csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_field_names)
        writer.writeheader()
        for row in output_data:
            writer.writerow(row)

    print(f"Done. Wrote CSV file to {str(output_csv_path)} with {len(output_data)} rows.")


if __name__ == "__main__":
    main()
