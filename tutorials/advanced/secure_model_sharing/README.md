# Secure Model Sharing

← encrypt and protect model code and weights

Encryption and protection of model code and weights when sharing across sites and collaborators on the Rhino FCP.

---

## Tutorials

### Model & Code Encryption — Concepts & Setup
Generate encryption keys and encrypt model code and weights for FCP deployment.

→ [`../../../../examples/nvflare/encrypted-model-code-and-weights/`](../../../../examples/nvflare/encrypted-model-code-and-weights/)

Key files:
- `encrypt_code/generate_key.py` — generate an encryption key
- `encrypt_code/encrypt_code.py` — encrypt your model code
- `custom/decrypt_code.py` — decrypt at run time within the container
- `infer.py` — run inference with an encrypted model

→ [docs.rhinohealth.com — Model and Code Encryption](https://docs.rhinohealth.com/hc/en-us/articles/28953915016221)

---

### Running Encrypted Code Objects (GC)
Encrypt a Python script and run it as a GC code object so source code is never exposed at collaborator sites.

→ [`../../../../examples/generalized-compute/run-encrypted-code/`](../../../../examples/generalized-compute/run-encrypted-code/)

Key files:
- `generate_key.py` — generate an encryption key
- `encrypt_code.py` — encrypt your script
- `decrypt_code.py` — decrypt at run time
- `run_encrypted_code.sh` — end-to-end run script

---

### Encrypted Model Weights — NVFlare End-to-End
Encrypt model weights during training, store them encrypted on FCP, and decrypt at inference using a run-time key.

→ [`../../../../examples/nvflare/encrypted-model-code-and-weights/`](../../../../examples/nvflare/encrypted-model-code-and-weights/)

---

### XGBoost with FHE (Fully Homomorphic Encryption)
Train XGBoost with NVFlare and the FHE encryption plugin.

→ [`../../../../examples/nvflare/xgboost/xgboost-fhe/`](../../../../examples/nvflare/xgboost/xgboost-fhe/)

---

## Additional resources

- [docs.rhinohealth.com — Model and Code Encryption](https://docs.rhinohealth.com/hc/en-us/articles/28953915016221)
- [Examples — GC run-encrypted-code](../../../../examples/generalized-compute/run-encrypted-code/)
- [Examples — NVFlare encrypted model](../../../../examples/nvflare/encrypted-model-code-and-weights/)
