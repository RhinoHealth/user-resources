# Tutorial 2 -  Using the Rhino Python SDK
> Last validated: 2026-10-27

## Description

Contains the resources for Tutorial 2, that goes over basic functionalities of the Rhino Python SDK, including how to register datasets and process and explore that data programmatically. 

See [RhinoDocs](https://docs.rhinofcp.com/tutorials-recipes-and-demos/tutorial-2-using-the-sdk) for additional info and instructions.

## Resources
- `data/` - The data needed for the tutorial
  - `input/`
    - `site1_part1_dataset.csv` - The first batch of data for site 1, registered as its own dataset during the tutorial
    - `site1_part2_dataset.csv` - A second batch of data for site 1, registered later to demonstrate re-running the same harmonization workflow on new data
    - `site2_part1_dataset.csv` - The first batch of data for site 2, registered as its own dataset during the tutorial
    - `site2_part2_dataset.csv` - A second batch of data for site 2, registered later to demonstrate re-running the same harmonization workflow on new data
    - `site3_part1_dataset.csv` - The first batch of data for site 3, registered as its own dataset during the tutorial
    - `site3_part2_dataset.csv` - A second batch of data for site 3, registered later to demonstrate re-running the same harmonization workflow on new data
- `notebooks/` - The Jupyter notebook used in this tutorial, plus the Dashboard UI screenshots it embeds
  - `all_data_fixed.png` - Screenshot: all three sites' harmonized ("Fixed") datasets combined and filtered together in the Dashboard UI, at the end of the tutorial
  - `part_1_data_discrepancies.png` - Screenshot: the raw, un-harmonized Part 1 datasets in the Dashboard UI, showing the cross-site inconsistencies (e.g. mismatched Outcome values, different units for Weight/Height/SkinThickness) that motivate harmonization
  - `part_1_data_fixed.png` - Screenshot: the three Part 1 "Fixed" output datasets in the Dashboard UI, after harmonization resolves those inconsistencies
  - `Tutorial_2_Notebook.ipynb` - A step-by-step walkthrough for logging in, registering each site's datasets with the Rhino Python SDK, and applying a reusable data harmonization/ETL workflow across them
- `schemas/` - The data schema needed to complete this tutorial
  - `harmonization_schema.csv` - The schema used when registering the datasets above, telling FCP what structure to expect the data to be in
- `README.md` - This file

## Getting Help
For additional support, check out [RhinoDocs](https://docs.rhinofcp.com/) or reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).