# NVIDIA FLARE Example - Hello PyTorch
> Last validated: 2026-08-19
<br/>

### **Description**

This example adapts NVIDIA's [Hello PyTorch](https://github.com/NVIDIA/NVFlare/tree/main/examples/hello-world/hello-pt) NVIDIA FLARE example to run on Rhino's Federated Computing Platform (FCP).

It shows how to:
* Use PyTorch model code adapted to NVIDIA FLARE (NVFlare), and apply the necessary changes for it to run on FCP
* Add an `infer.py` script to perform inference on the trained model
* Package the code in a Docker container that can be used with FCP

Please reference the User Documentation and/or Tutorials for in-depth explanations on how to use NVFlare on FCP:
- [Creating and Running NVFlare Code and Running Inference](https://docs.rhinofcp.com/creating-and-running-code-objects/creating-and-running-nvflare-code-and-running-inference) (FCP UI)
- [Creating a New NVFlare Code Object Using the Rhino SDK](https://docs.rhinofcp.com/rhino-sdk/creating-a-new-nvflare-code-object-using-the-rhino-sdk)
- [Running NVFlare Code Using the Rhino SDK](https://docs.rhinofcp.com/rhino-sdk/running-nvflare-code-using-the-rhino-sdk)
<br/><br/>

### **Requirements**

This example is validated with **NVFlare 2.8.1**, **torch 2.4.0**, and **torchvision 0.19.0** on Python 3.12.
<br/><br/>

### **Resources**
- `config` - This is the standard NVFlare directory for config files
  - `config_fed_client.json` - The standard NVFlare federated client config, setting to 4 epochs for the example
  - `config_fed_server.json` - The standard NVFlare federated server config, setting the output model weights file to be stored in `/output/model_parameters.pt`
- `custom` - This is the standard NVFlare directory for custom model code, containing the code from the NVIDIA examples, but with the inputs being read from the `/input` folder in order to work with FCP
- `data` - A folder with some example data to train/test with
- `Dockerfile` - This is the Dockerfile to be used for building the container image. It uses a single-step build process (without installing requirements in a separate build step)
- `infer.py` - A script for running inference on the trained model
- `requirements.txt` - The python requirements for this project
<br><br>

### **Running this example locally**

The trained model and inference output are written to `/output`, matching how FCP mounts your container. Run this example inside Docker so `/input` and `/output` behave the same way they will on FCP.

1. **Build the Docker image:**
   ```bash
   docker build -t hello-pt .
   ```

2. **Prepare the training data mount:**
   ```bash
   mkdir -p ~/hellopt-test/train_mount/file_data
   cd ~/hellopt-test/train_mount/file_data
   unzip /path/to/hello-pt-rhino/data/train_data.zip
   # creates file_data/train/0 ... file_data/train/9
   mkdir -p ~/hellopt-test/output
   ```

3. **Run training**, with `/input` and `/output` mounted in:
   ```bash
   docker run -it \
     -v ~/hellopt-test/train_mount:/input \
     -v ~/hellopt-test/output:/output \
     hello-pt bash
   ```
   Inside the container:
   ```bash
   nvflare simulator -w /tmp/nvflare-workspace -n 1 -t 1 .
   ```
   You should see log output for 2 rounds of Scatter-and-Gather training, ending with `Finished ScatterAndGather Training.` Confirm the model was saved:
   ```bash
   ls -la /output   # should show model_parameters.pt
   ```
   `exit` the container when done.

4. **Prepare the inference data mount** (separate from training - classes go directly under `file_data`, with no `train`/`test` prefix folder):
   ```bash
   mkdir -p ~/hellopt-test/infer_mount/file_data
   cd /tmp && unzip /path/to/hello-pt-rhino/data/test_data.zip -d test_extract
   for d in test_extract/test/*/; do
     cls=$(basename "$d")
     mkdir -p ~/hellopt-test/infer_mount/file_data/$cls
     cp "$d"*.png ~/hellopt-test/infer_mount/file_data/$cls/
   done
   cp /tmp/test_extract/test/cohort_data_test.csv ~/hellopt-test/infer_mount/dataset.csv
   ```

5. **Run inference:**
   ```bash
   docker run -it \
     -v ~/hellopt-test/infer_mount:/input \
     -v ~/hellopt-test/output:/output \
     hello-pt bash
   ```
   Inside the container:
   ```bash
   python infer.py /output/model_parameters.pt
   cat /output/dataset.csv   # should show a Model_Score column added
   ```

6. Since `/input` and `/output` were mounted from your machine, the output is also visible on your host at `~/hellopt-test/output`.

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
For additional support, please reach out to [support@rhinofcp.com](mailto:support@rhinofcp.com).
