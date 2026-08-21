# NVIDIA FLARE Example - Hello Numpy Scatter and Gather
> Last validated: 2026-08-18
<br/>

### **Description**

This example adapts NVIDIA's [Hello Numpy Scatter and Gather](https://github.com/NVIDIA/NVFlare/tree/main/examples/hello-world/hello-numpy-sag) NVIDIA FLARE example to run on Rhino's Federated Computing Platform (FCP).

It shows how to:
* Use model code adapted to NVIDIA FLARE (NVFlare), and apply the necessary changes for it to run on FCP
* Add an `infer.py` script to perform inference on the trained model
* Package the code in a Docker container that can be used with FCP

Please reference the User Documentation and/or Tutorials for in-depth explanations on how to use NVFlare on FCP:
- [Creating and Running NVFlare Code and Running Inference](https://docs.rhinofcp.com/creating-and-running-code-objects/creating-and-running-nvflare-code-and-running-inference) (FCP UI)
- [Creating a New NVFlare Code Object Using the Rhino SDK](https://docs.rhinofcp.com/rhino-sdk/creating-a-new-nvflare-code-object-using-the-rhino-sdk)
- [Running NVFlare Code Using the Rhino SDK](https://docs.rhinofcp.com/rhino-sdk/running-nvflare-code-using-the-rhino-sdk)
<br/><br/>

### **Requirements**

This example is validated with **NVFlare 2.8.1** on Python 3.12.
<br/><br/>

### **Resources**
- `config` - This is the standard NVFlare directory for config files
- `custom` - This is the standard NVFlare directory for custom model code, containing the code from the NVIDIA examples, but with the inputs being read from the `/input` folder in order to work with FCP
- `data` - A folder with some example data (`dataset.csv`) to train/test with locally, before deploying to FCP
- `Dockerfile` - This is the Dockerfile to be used for building the container image. It uses a single-step build process (without installing requirements in a separate build step)
- `infer.py` - A script for running inference on the trained model. The model in this example is a simple placeholder, so `infer.py` likewise emits a placeholder `SCORE` column rather than a real prediction - swap in your own model and scoring logic for real use cases.
- `requirements.txt` - The python requirements for this project
<br><br>

### **Running this example locally**

The trained model and inference output are written to `/output`, matching how FCP mounts your container. Run this example inside Docker so `/input` and `/output` behave the same way they will on FCP.

1. **(Optional) Create a virtual environment and install dependencies**, to confirm `requirements.txt` resolves cleanly on your machine before building the image:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Build the Docker image:**
   ```bash
   docker build -t hello-numpy-sag .
   ```

3. **Set up local input/output folders and start a container shell**, with `/input` and `/output` mounted in:
   ```bash
   mkdir -p ~/nvflare-test/input ~/nvflare-test/output
   cp data/dataset.csv ~/nvflare-test/input/dataset.csv

   docker run -it \
     -v ~/nvflare-test/input:/input \
     -v ~/nvflare-test/output:/output \
     hello-numpy-sag bash
   ```

4. **Inside the container, run the FL Simulator** (1 client, 1 thread is enough for this example):
   ```bash
   nvflare simulator -w /tmp/nvflare-workspace -n 1 -t 1 .
   ```
   You should see log output for 3 rounds of Scatter-and-Gather training, ending with `Finished ScatterAndGather Training.`

5. **Test inference** against the trained model, still inside the container:
   ```bash
   python infer.py /output/model_parameters.npy
   cat /output/dataset.csv   # should show a SCORE column added
   ```

6. `exit` the container when done. Since `/input` and `/output` were mounted from your machine, the output is also visible on your host at `~/nvflare-test/output`.

### **Running this example on FCP**

Once your image is built and pushed to your workgroup's container registry, create and run it as an NVFlare Code Object:
- Using the FCP UI: [Creating and Running NVFlare Code and Running Inference](https://docs.rhinofcp.com/creating-and-running-code-objects/creating-and-running-nvflare-code-and-running-inference)
- Using the Rhino SDK: [Creating a New NVFlare Code Object Using the Rhino SDK](https://docs.rhinofcp.com/rhino-sdk/creating-a-new-nvflare-code-object-using-the-rhino-sdk) and [Running NVFlare Code Using the Rhino SDK](https://docs.rhinofcp.com/rhino-sdk/running-nvflare-code-using-the-rhino-sdk)

FCP mounts the platform's `/input` and `/output` directories into the running container automatically - you do not need to create them yourself as you did for the local test above.
<br><br>

### **Using a different Python or NVFlare version**

- If your environment needs to stay on **Python 3.8**, use **NVFlare 2.4.2** instead of 2.8.1, and keep `python:3.8-slim-bullseye` as the `Dockerfile` base image.
- For any other Python/NVFlare pairing, update the `nvflare==` line in `requirements.txt` and the base image in the `Dockerfile` accordingly, then re-run the steps above to confirm training and inference both complete successfully.
<br><br>

# Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
