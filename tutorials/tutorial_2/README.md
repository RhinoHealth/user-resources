# Tutorial #2 - Rhino Health Federated Computing Platform Data Harmonization on the FCP SDK
<br/>

### **Description**

By following the [step-by-step instruction](https://docs.rhinohealth.com/hc/en-us/articles/10289950903837-Tutorial-2-Rhino-Health-Federated-Computing-Platform-Data-Harmonization-on-the-FCP-SDK) in this tutorial, you will learn how to:

1. Install and configure the Rhino Health Python SDK
2. Import cohorts with local CSV files
3. Easily harmonize data on multiple cohorts with multiple cohorts from similar sites
<br/><br/>

### **Resources**
- `notebooks/` - This folder contains the jupyter notebook you will use within this tutorial
  - `Tutorial 2 - Data Harmonization.ipynb` - this jupyter notebook is a step-by-step tutorial for producing model results visualizations using the Rhino Health Python SDK.
- `data/` - This directory contains the data that is need for the tutorial
  - `input/`
    - `site1_part1_cohort_data.csv`, `site2_part1_cohort_data.csv`, `site3_part1_cohort_data.csv` - The files that define the datasets at the three different sites you will import during the tutorial.
    - `site1_part2_cohort_data.csv`, `site2_part2_cohort_data.csv`, `site3_part2_cohort_data.csv` - The files that define the second part of the datasets at the three different sites. This second part of the dataset is meant to illustrate how easy it is to create re-usable data harmonization workflows using the Rhino Health Python SDK
- `schemas/` - This folder contains the data schema you will need to complete this tutorial
  - `Harmonization schema.csv` - This schema is used when importing your cohorts to inform the platform what structure the data should be in.

<br><br>

# Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).