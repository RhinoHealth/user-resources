# Tutorial 2 -  Multi-Cohort Data Harmonization with the Rhino Health Python SDK
<br/>

### **Description**

By following the step-by-step instruction in this tutorial, you will learn how to:

1. Install and configure the Rhino Health Python SDK
2. Import cohorts with local CSV files
3. Easily harmonize data on multiple cohorts with multiple cohorts from similar sites
<br/><br/>

### **Resources**
1. `Tutorial 2 - Data Harmonization.ipynb` - this jupyter notebook is a step-by-step tutorial for producing model results visualizations using the Rhino Health Python SDK.
2. `cohorts/` - This folder contains a python script (dataprep_gc.py), and several additional files required to create the docker container that will run the script on the RHP (to be used in Step 5).
    - **diabetes_site1_part1.csv**, **diabetes_site2_part1.csv**, **diabetes_site3_part1.csv** - The files that define the datasets at the three different sites you will import during the tutorial.
    - **diabetes_site1_part2.csv**, **diabetes_site2_part2.csv**, **diabetes_site3_part2.csv** - The files that define the second part of the datasets at the three different sites. This second part of the dataset is meant to illustrate how easy it is to create re-usable data harmonization workflows using the Rhino Health Python SDK
3. `Harmonization schema.csv` - This schema is used when importing your cohorts to inform the platform what structure the data should be in.

### Getting Help
Please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com) if you encounter any issues while following this tutorial.