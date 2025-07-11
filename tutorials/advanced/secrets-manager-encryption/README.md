# Secrets Manager Integration and Encryption with Rhino FCP

This tutorial demonstrates how to integrate with Rhino FCP's third party Secrets Manager integration to securely encrypt and protect sensitive code and model weights in federated learning applications. The example uses a Chemprop-based molecular property prediction model with NVFlare federated learning framework.

## Overview

This tutorial shows how to:
- Encrypt sensitive Python code and model weights using hybrid RSA/AES encryption
- Integrate with Rhino FCP's third party Secrets Manager to securely store decryption keys
- Deploy encrypted federated learning applications that automatically decrypt at runtime
- Use the encrypted model in a federated learning workflow with NVFlare

## Directory Structure

```
secrets-manager-encryption/
├── README.md                    # This file
├── data/                        # Sample molecular datasets
│   ├── cyp3a4_A.csv            # Training dataset A
│   ├── cyp3a4_B.csv            # Training dataset B  
│   ├── cyp3a4_C.csv            # Training dataset C
│   └── cyp3a4_test.csv         # Test dataset
└── code/                        # Application code
    ├── chemprop_fl_classification.py  # Main federated learning model
    ├── requirements.txt         # Python dependencies
    ├── Dockerfile              # Container configuration
    ├── entrypoint.sh           # Container entrypoint for decryption
    ├── infer.py                # Inference script
    ├── meta.conf               # Model metadata
    ├── model_parameters.pt     # Pre-trained model weights
    ├── encrypt_code/           # Encryption utilities
    │   └── encrypt_code.py     # File encryption with AWS Secrets Manager integration
    └── app/                    # Application files
        ├── custom/             # Custom application code
        │   ├── chemprop_fl_classification.py.enc  # Encrypted main model
        │   ├── model_parameters.pt.enc            # Encrypted model weights
        │   ├── decrypt_code.py                    # Runtime decryption utility
        │   └── encrypted_persistor.py             # Encrypted model persistence
        └── config/             # NVFlare configuration
            ├── config_fed_client.conf  # Federated client configuration
            └── config_fed_server.conf  # Federated server configuration
```

## Prerequisites

- Python 3.12+
- Docker
- Access to Rhino FCP platform
- Access to a third party Secrets Manager platform (this example uses AWS Secrets Manager)

## Quick Start

### 1. Configure AWS Secrets Manager

Before encrypting files, you need to configure AWS Secrets Manager:

1. **Set up AWS IAM Role**: Create an IAM role with permissions to access Secrets Manager
2. **Update Configuration**: Modify the `encrypt_code.py` file to set your AWS account ID and role name:
   ```python
   ACCOUNT_ID = '<your-account-id>'
   ROLE_NAME = '<your-role-name>'
   ```
3. **Key Management**: Keys will be automatically created and stored as individual secrets in AWS Secrets Manager

The encryption utility will automatically generate and manage RSA key pairs within the Secrets Manager.

### 2. Encrypt Sensitive Files

Encrypt your model code and weights using the AWS Secrets Manager integration:

```bash
cd code/encrypt_code

# Encrypt the main model file
python encrypt_code.py -i ../chemprop_fl_classification.py \
                       -k model_key \
                       -o ../app/custom/chemprop_fl_classification.py.enc

# Encrypt model weights
python encrypt_code.py -i ../model_parameters.pt \
                       -k model_key \
                       -o ../app/custom/model_parameters.pt.enc

# Optional: Delete original files after encryption
python encrypt_code.py -i ../chemprop_fl_classification.py \
                       -k model_key \
                       -o ../app/custom/chemprop_fl_classification.py.enc \
                       -d
```

The encryption utility will:
- Automatically generate RSA key pairs if they don't exist
- Store each key pair as a separate secret in AWS Secrets Manager using the key name as the secret ID
- Use hybrid RSA/AES encryption for file protection
- Optionally delete original files after encryption (use `-d` flag)

### 3. Configure Rhino FCP to Use Secrets Manager

Reach out to a Rhino FCP representative to configure your Organization to utilize direct Secrets Manager Integration. This can only be configured by a Rhino Admin.

### 4. Deploy the Application

Build and deploy the Docker container:

```bash
cd code
../../../../rhino-utils/docker-push.sh <workgroup-ecr> <container-name>
```

The container will automatically:
- Decrypt files at startup using the private key from Secrets Manager
- Run the federated learning application
- Participate in the federated training process

## How It Works

### Encryption Process

1. **Hybrid Encryption**: Uses RSA for key exchange and AES for data encryption
2. **File Encryption**: Sensitive files are encrypted with AES using a random session key
3. **Key Protection**: The session key is encrypted with RSA public key
4. **Secure Storage**: Each key pair is stored as a separate secret in AWS Secrets Manager
5. **Key Management**: Private keys are retrieved from Rhino FCP's Secrets Manager at runtime

### Runtime Decryption

1. **Container Startup**: The `entrypoint.sh` script runs before the main application
2. **Key Retrieval**: `decrypt_code.py` retrieves the private key from Rhino FCP's integration with a third party Secrets Manager 
3. **File Decryption**: All `.enc` files are automatically decrypted using the retrieved key
4. **Application Execution**: The decrypted files are used by the federated learning application

## Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
