# Site Validation Script

The goal of this project is to validate the installation of a new client site. It uses the Rhino SDK to simulate the workflow of a standard project.

In this directory you will find two directories and the notebook to run the testing
- `./data/` - a directory containing the data to upload into the cloud mounted storage
- `./model/` - a directory containing an NVFlare model for testing Autocontainer NVFlare functionality
- `./site-testing.ipynb` - the Jupyter Notebook to run the process

This page will document the steps needed to perform the site validation.

## Preparing the Project

1. Copy the `./data/credit_risk_dataset.csv` file to the location you wish to use for data uploads. This can be either on the Rhino Client (`/rhino_health/`) or on an external data store (e.g. S3, GCS)
2. Gather the login credentials for a Rhino Cloud user
3. Update the `./site-testing.ipynb` file with the values in step 2.
   - `USERNAME` - The username of the Rhino Cloud user
   - `DATASTORE_PATH` - The path to where you copied the `./data` folder, either locally or on cloud storage

## Running the Project

Once everything is prepared, you may proceed by running the `./site-testing.ipynb` notebook. If everything succeeds, then the client is able to complete a simple project.

If there are failures, you may see errors either in the notebook, or within the Rhino Health Server UI.