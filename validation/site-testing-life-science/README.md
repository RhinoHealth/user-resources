# Site Validation Script

The goal of this project is to validate the installation of a new Rhino Client. It uses the Rhino SDK to simulate the workflow of a standard project.

In this directory you will find two directories and the notebook to run the testing
- `./data/` - a directory containing the data to make accessible to your Rhino Client
- `./model/` - a directory containing an NVFlare model for testing Autocontainer NVFlare functionality
- `./site-testing.ipynb` - the Jupyter Notebook to run the process

This page will document the steps needed to perform the site validation.

## Preparing the Project

1. Copy the `./data/cyp3a4_all_no_test.csv` file to the location you wish to use for data accessible to the Rhino Client. This can be either on the Rhino Client (`/rhino_data/`) or on a client-mounted data store (e.g. S3, GCS).
2. Make sure you have your login credentials to the Rhino FCP
3. Update the `./site-testing.ipynb` file with the values in step 2.
   - `USERNAME` - The username (email) of your Rhino FCP user
   - `CLIENT_DATA_PATH` - The path to where you copied the contents of the `./data` folder, either within `/rhino_data/` or the mount point for client-mounted storage (e.g. `/rhino_data/external/my_storage_bucket`)

## Running the Project

Once everything is prepared, you may proceed by running the `./site-testing.ipynb` notebook. If everything succeeds, then the client is able to complete a simple project.

If there are failures, you may see errors either in the notebook, or within the Rhino Health Server UI.