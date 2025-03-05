import pandas as pd
from rdkit import Chem
from rdkit.Chem.Descriptors import ExactMolWt

def calculate_molecular_weight(smiles):
    """
    Calculates molecular weight for a single SMILES string.

    Args:
        smiles (str): A SMILES string.

    Returns:
        float: The molecular weight, or None if the SMILES is invalid.
    """
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is not None:
            return ExactMolWt(mol)
    except Exception as e:
        print(f"Error processing SMILES '{smiles}': {e}")
    return None

df = pd.read_csv('/input/dataset.csv')

# Calculate molecular weights and add to the DataFrame
df['molecule_weight'] = df['smiles'].apply(calculate_molecular_weight)

df.to_csv('/output/dataset.csv', index=False)