#!/bin/bash

create_file_if_not_exists() {
    local root_folder="$1"
    local filename="$2"
    
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

    # Create file in root folder
    create_in_dir "$root_folder"

    # Create file in all subdirectories of root folder
    find "$root_folder" -type d | while read -r dir; do
        create_in_dir "$dir"
    done
}

# Python facepalm moment
create_file_if_not_exists "./src" "__init__.py"
create_file_if_not_exists "./src" "py.typed"

# Make files +x
find . -type f -name "*.sh" -exec chmod +x {} +
find . -type f -name "*.sh"