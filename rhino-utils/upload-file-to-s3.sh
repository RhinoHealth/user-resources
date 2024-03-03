#!/bin/bash
set -eu -o pipefail

# Function to display usage
usage() {
    echo "Usage: $0 <upload_directory> <s3_bucket> <path_in_bucket>"
    echo
    echo "Parameters:"
    echo "<upload_directory>   The local directory to upload."
    echo "<s3_bucket>         The name of the S3 bucket."
    echo "<path_in_bucket>    The path in the S3 bucket where the directory should be uploaded."
    exit 1
}

# Check if the correct number of arguments are provided
if [ "$#" -ne 3 ]; then
    usage
fi

# Assign the arguments to variables
upload_directory=$1
s3_bucket=$2
path_in_bucket=$3


if [[ ! -v AWS_ACCESS_KEY_ID ]] || [[ -z "$AWS_ACCESS_KEY_ID" ]]; then
	    echo "The 'AWS_ACCESS_KEY_ID' environment variable is empty - please set it to a valid value"
	    exit 1
fi

if [[ ! -v AWS_SECRET_ACCESS_KEY ]] || [[ -z "$AWS_SECRET_ACCESS_KEY" ]]; then
	    echo "The 'AWS_SECRET_ACCESS_KEY' environment variable is empty - please set it to a valid value"
	    exit 1
fi

set -x
# Use the AWS CLI to upload the directory to the S3 bucket
if aws s3 cp --recursive "$upload_directory" "s3://$s3_bucket/$path_in_bucket/"; then
    echo "Upload completed."
else
    echo "Upload failed. Please check your parameters and try again."
fi
