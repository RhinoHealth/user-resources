import getpass
from pprint import pprint

import rhino_health as rh
from rhino_health.lib.endpoints.project.project_dataclass import ProjectCreateInput
from rhino_health.lib.endpoints.sql_query.sql_query_dataclass import (
    SQLQueryImportInput,
    SQLQueryInput,
    SQLServerTypes,
    ConnectionDetails
)
from rhino_health.lib.endpoints.code_object.code_object_dataclass import (
    CodeObject,
    CodeObjectCreateInput,
    CodeTypes,
    CodeObjectRunInput
)
from rhino_health.lib.endpoints.syntactic_mapping.syntactic_mapping_dataclass import (
    DataHarmonizationRunInput
)


def main():
    # Authentication
    my_username = ""  # Replace with your email
    session = rh.login(
        username=my_username,
        password=getpass.getpass(),
    )
    
    # Project configuration
    project_uid = '2d32128d-3a27-408a-9315-e7e37c458718'
    workgroup_uid = 'c50eb65a-7c61-422f-84a5-dd515fff5c24'
    
    # Execute data harmonization
     print("Transforming Data to FlatFHIR")
    data_harmonization_params = DataHarmonizationRunInput(
        input_dataset_uids=['1f124ad2-6a14-4bcd-ba00-9951cdf33758'],
        semantic_mapping_uids_by_vocabularies={}
    )
    
    code_run = session.code_object.run_data_harmonization(
        code_object_uid='120569bb-6c9e-4760-9a1d-1151d6e57ca4',
        run_params=data_harmonization_params
    )
    run_result = code_run.wait_for_completion()
    
    # Extract output dataset UID
    output_dataset_uid = run_result.output_dataset_uids.root[0].root[2].root[0]
    
    # Generate FHIR resources
    print("Generating FHIR Resources")
    code_object_params = CodeObjectRunInput(
        code_object_uid='b54d8b44-3b10-4a64-85e0-767df07aa40b',
        input_dataset_uids=[[output_dataset_uid]],
        timeout_seconds=8600
    )
    
    # Run Python code object
    code_run = session.code_object.run_code_object(code_object_params)
    run_result = code_run.wait_for_completion()
    fhir_dataset_uid = code_run.code_run.output_dataset_uids.root[0].root[0].root[0]
    
    # Export results as CSV
    print("Saving FHIR JSON To Rhino Client")
    export_response = session.dataset.export_dataset(
        dataset_uid=fhir_dataset_uid,
        output_location='/rhino_data/fhir_data/',
        output_format='csv'
    )
    
    return export_response


if __name__ == "__main__":
    main()