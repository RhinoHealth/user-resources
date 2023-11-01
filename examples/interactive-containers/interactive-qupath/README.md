# Interactive Container Example - Interactive QuPath

This example provides files that can be used with the Rhino Health Generalized Compute capability to remotely run an interactive QuPath session to view and/or annotate DICOM data on a Rhino Client

It shows how to:
* Structure a Dockerfile to run an interactive QuPath application
* Add links to the interactive desktop to load QuPath
* Add a script to create a manifest CSV file from the QuPath output files

Please reference the User Documentation and/or Tutorials for in depth explanations on how to use the Interactive Container capability.

## How to Run Locally



## Resources
- `Dockerfile` - This is the Dockerfile to be used for building the container image. It starts from an Ubuntu desktop base image and installs QuPath and other dependencies 
- `qupath_128.png`, `QuPath.desktop`, `QuPath-link.desktop` - Files for creating a desktop link to open QuPath
- `create_cohort_csv.py` - A script to create a manifest CSV file from the 3D Slicer output files
- `Rhino-Health-Logo.svg`, `Create-Output-Cohort.desktop`, `Create-Output-Cohort-link.desktop` - Files for creating a desktop link to run the create_cohort_csv.py script

## Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
