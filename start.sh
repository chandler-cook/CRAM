#!/bin/bash

# Path to your .env file
ENV_FILE=".env"

# Check if .env file exists
if [[ ! -f $ENV_FILE ]]; then
  echo ".env file not found!"
  exit 1
fi

# Load the .env file
source $ENV_FILE

# List of keys to check
keys=("VULNCHECK_API")

# Loop through each key and check if it's empty or not
for key in "${keys[@]}"
do
  value=$(eval echo \$$key)

  if [[ -z "$value" ]]; then
    echo "Error: $key is empty or not set."
    echo "Please go to https://vulncheck.com/settings/tokens and create an account and token."
    #python3 /flask/backend/functions/CVE_Prioritizer/cve_prioritizer.py -sa
    printf "vulncheck\n" | python3 cve_prioritizer.py -sa

  else
    echo "$key is set"
    # Add your "if" condition here
  fi
done

