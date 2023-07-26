import cudf

filename = '/input/cohort_data.csv'

# Load cohort
cu_df = cudf.read_csv(filename)

# One hot Encoding
categorical_columns = [
    'gender',
    'admit_type',
    'admit_location'
]
for col in categorical_columns:
    # if the original column is present replace it with a one-hot
    if col in cu_df.columns:
        one_hot_encoded = cudf.get_dummies(cu_df[col])
        cu_df = cu_df.drop(col, axis=1)
        cu_df = cu_df.join(one_hot_encoded, lsuffix='_left', rsuffix='_right')

# Write cohorts to /output
cu_df.to_csv('/output/cohort_data.csv', index=False)

