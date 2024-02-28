#!/bin/bash

# Check if the correct number of arguments are provided
if [ "$#" -lt 3 ]; then
    echo "Usage: $0 <upload_directory> <s3_bucket> <path_in_bucket> [aws_access_key_id] [aws_secret_access_key]"
    exit 1
fi

# Assign the arguments to variables
upload_directory=$1
s3_bucket=$2
path_in_bucket=$3

# If AWS credentials are provided, use them. Otherwise, use the ones from the environment.
if [ "$#" -ge 5 ]; then
    aws_access_key_id=$4
    aws_secret_access_key=$5
else
    aws_access_key_id=$AWS_ACCESS_KEY_ID
    aws_secret_access_key=$AWS_SECRET_ACCESS_KEY
fi

# Use the AWS CLI to upload the directory to the S3 bucket
if AWS_ACCESS_KEY_ID=$aws_access_key_id AWS_SECRET_ACCESS_KEY=$aws_secret_access_key aws s3 cp --recursive "$upload_directory" "s3://$s3_bucket/$path_in_bucket/"; then
    echo "Upload completed."
else
    echo "Upload failed. Please check your parameters and try again."
fi
