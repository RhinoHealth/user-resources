# Interactive Container Example - Interactive 3D Slicer
<br/>

### **Description**

This example provides files that can be used with the Rhino Health Generalized Compute capability to remotely run an interactive 3D Slicer session to view and/or annotate DICOM data on a Rhino Client

It shows how to:
* Structure a Dockerfile to run an interactive 3D Slicer application
* Add links to the interactive desktop to load 3D Slicer
* Add a script to create a manifest CSV file from the 3D Slicer output files

Please reference the User Documentation and/or Tutorials for in depth explanations on how to use the Generalized Compute and Interactive Container capability.
<br/><br/>

### **Resources**
- `Dockerfile` - This is the Dockerfile to be used for building the container image. It starts from an Ubuntu desktop base image and installs 3D Slicer and other dependencies 
- `3D-Slicer-Mark.svg`, `3DSlicer.desktop`, `3DSlicer-link.desktop` - Files for creating a desktop link to open 3D Slicer
- `create_cohort_csv.py` - A script to create a manifest CSV file from the 3D Slicer output files
- `Rhino-Health-Logo.svg`, `Create-Output-Cohort.desktop`, `Create-Output-Cohort-link.desktop` - Files for creating a desktop link to run the create_cohort_csv.py script
<br><br>

# Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
