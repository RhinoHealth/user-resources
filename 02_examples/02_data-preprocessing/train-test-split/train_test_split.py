import pandas as pd
from sklearn.model_selection import train_test_split


if __name__ == '__main__':
	# Read the input data from /input
	df_input = pd.read_csv('/input/0/dataset.csv')

	# Split to train and test sets
	df_train, df_test = train_test_split(df_input, test_size=0.33)

	# Write the output data to /output
	df_train.to_csv('/output/0/dataset.csv', index=False)
	df_test.to_csv('/output/1/dataset.csv', index=False)

