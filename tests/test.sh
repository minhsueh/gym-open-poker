#!/bin/bash

# Find all files matching the pattern and store in a variable
test_files=$(find . -type f -name 'test_*.py')


# Iterate over each file in the variable
IFS=$'\n'  # Set Internal Field Separator to newline to handle file names with spaces
for file in $test_files; do
    echo "Processing file: $file"
    # Add your logic here for each file
    pytest $file
done