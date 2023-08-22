extension_names = [
  ("DCMQI", "/root/Desktop/31382-linux-amd64-DCMQI-git451bf84-2023-01-26.tar.gz"),
  ("PETDICOMExtension", "/root/Desktop/31382-linux-amd64-PETDICOMExtension-git6840644-2022-03-18.tar.gz"),
  ("QuantitativeReporting", "/root/Desktop/31382-linux-amd64-QuantitativeReporting-git8a6e612-2022-11-30.tar.gz"),
  ("SlicerDevelopmentToolbox", "/root/Desktop/31382-linux-amd64-SlicerDevelopmentToolbox-git2c2465d-2022-09-14.tar.gz")
]

manager = slicer.app.extensionsManagerModel()
for extension_name, file_path in extension_names:
  print(f"installing {extension_name}")
  if not manager.isExtensionInstalled(extension_name):
    manager.installExtension(file_path)
exit()
