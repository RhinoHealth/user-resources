## This folder contains a minimal working example for computing Cox proportional hazard metrics using the Rhino SDK.

## Files

- `cox_sampledata1.csv` – sample dataset 1
- `cox_sampledata2.csv` – sample dataset 2
- `cox.ipynb` – interactive notebook demonstrating the end-to-end process

## How to Use

1. Upload both CSV files as datasets in your Rhino project.
2. Run the cells in `cox.ipynb` to compute and visualize the Cox regression results.
3. All column names are pre-formatted and aligned with the metric's expected input schema.

### Both sample datasets are synthetic and contain the following columns:

| Column  | Description                         |
| ------- | ----------------------------------- |
| `Time`  | Duration until event or censoring   |
| `Event` | 1 if event occurred / 0 if censored |
| `COV1`  | Age                                 |
| `COV2`  | Heart rate                          |
