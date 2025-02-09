#!/bin/bash

create_file_if_not_exists() {
    local filename="$1"
    
    # Function to create file in a directory if it doesn't exist
    create_in_dir() {
        local dir="$1"
        local filepath="$dir/$filename"
        if [ ! -f "$filepath" ]; then
            touch "$filepath"
            echo "Created $filename in $dir"
        else
            echo "$filename already exists in $dir"
        fi
    }

    # Create file in ./src directory
    create_in_dir "./src"

    # Create file in all subdirectories of ./src
    find ./src -type d | while read -r dir; do
        create_in_dir "$dir"
    done
}

# Python facepalm moment
create_file_if_not_exists "__init__.py"
create_file_if_not_exists "py.typed"

# Make files +x
find . -type f -name "*.sh" -exec chmod +x {} +
find . -type f -name "*.sh"