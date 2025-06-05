#!/bin/bash

# Define the file to store the commit number
COMMIT_NUMBER_FILE="./.git_commit_number"

# Check if the commit number file exists
if [ ! -f "$COMMIT_NUMBER_FILE" ]; then
    echo 0 > "$COMMIT_NUMBER_FILE"
fi

# Read the current commit number
current_number=$(cat "$COMMIT_NUMBER_FILE")

# Increment the commit number
next_number=$((current_number + 1))

# Get current time in HHMM format
current_time=$(date +"%H%M")

# Construct the commit message
commit_message="$next_number $current_time"

# Add all changes to the staging area
git add .

# Commit the changes
git commit -m "$commit_message"

# Save the new commit number
echo "$next_number" > "$COMMIT_NUMBER_FILE"

echo "Changes added and committed with message: '$commit_message'"