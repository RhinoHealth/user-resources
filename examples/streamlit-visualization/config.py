from typing import Dict

# Visualization constants
FIGURE_SIZE = (12, 6)
BAR_WIDTH_FACTOR = 0.8
DATASET_EXPORT_YEAR = 2008
BIRTH_YEAR_DIVISOR = 10000

# Color scheme
COLOR_PALETTE = {
    "green": "#36BC45",
    "blue": "#003865",
    "teal": "#34EBEB",
    "light_green": "#C2E4BA",
    "gray": "#E2DCD5",
}

# Data mappings
RACE_CODES: Dict[str, str] = {
    '0': "Unknown",
    '1': "White",
    '2': "Black",
    '3': "Other",
    '4': "Asian",
    '5': "Hispanic",
    '6': "Native American"
}

REGION_MAPPING: Dict[str, str] = {
    '1': 'South', '2': 'West', '4': 'West', '5': 'South', '6': 'West', '8': 'West', 
    '9': 'Northeast', '10': 'South', '11': 'South', '12': 'South', '13': 'South', 
    '15': 'West', '16': 'West', '17': 'Midwest', '18': 'Midwest', '19': 'Midwest', 
    '20': 'Midwest', '21': 'South', '22': 'South', '23': 'Northeast', '24': 'South', 
    '25': 'Northeast', '26': 'Midwest', '27': 'Midwest', '28': 'South', '29': 'Midwest', 
    '30': 'West', '31': 'Midwest', '32': 'West', '33': 'Northeast', '34': 'Northeast', 
    '35': 'West', '36': 'Northeast', '37': 'South', '38': 'Midwest', '39': 'Midwest', 
    '40': 'South', '41': 'West', '42': 'Northeast', '44': 'Northeast', '45': 'South', 
    '46': 'Midwest', '47': 'South', '48': 'South', '49': 'West', '50': 'Northeast', 
    '51': 'South', '53': 'West', '54': 'South', '55': 'Midwest', '56': 'West', 
    '60': 'Other', '66': 'Other', '69': 'Other', '72': 'Other', '78': 'Other'
}

MEASURES = {
    'Alzheimer or related disorders or senile': 'SP_ALZHDMTA',
    'Heart Failure': 'SP_CHF',
    'Chronic Kidney Disease': 'SP_CHRNKIDN',
    'Cancer': 'SP_CNCR',
    'Chronic Obstructive Pulmonary Disease': 'SP_COPD',
    'Depression': 'SP_DEPRESSN',
    'Diabetes': 'SP_DIABETES',
    'Ischemic Heart Disease': 'SP_ISCHMCHT',
    'Osteoporosis': 'SP_OSTEOPRS',
    'Rheumatoid Arthritis or Osteoarthritis': 'SP_RA_OA'
}