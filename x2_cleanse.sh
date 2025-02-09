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
        fi
    }

    # Create file in root folder
    create_in_dir "$root_folder"

    # Create file in all subdirectories of root folder
    find "$root_folder" -type d | while read -r dir; do
        create_in_dir "$dir"
    done
}

create_directory_if_not_exists() {
    local path="$1"
    
    if [ ! -d "$path" ]; then
        mkdir -p "$path"
        echo "Created directory: $path"
    fi
}

clean_file_from_folders() {
    local root_folder="$1"       # The root folder to start searching
    local folder_name_to_act="$2" # The folder name to target
    local file_name="$3"          # The file name to delete

    # Find directories matching the FolderNameToAct
    find "$root_folder" -type d -name "$folder_name_to_act" | while read -r dir; do
        target_file_path="$dir/$file_name"

        if [ -f "$target_file_path" ]; then
            rm "$target_file_path"
            echo "Deleted file: $target_file_path"
        fi
    done
}

create_file_if_not_exists_excluding_folders() {
    local root_folder="$1"
    local folders_to_exclude="$2" # e.g. "__pycache__, hello" - separated by ,
    local file_name="$3"

    # Convert comma-separated string to array and trim each element
    IFS=',' read -ra exclude_folders <<< "$folders_to_exclude"
    exclude_folders=("${exclude_folders[@]// /}")

    # Function to check if a folder should be excluded
    is_excluded() {
        local folder_name="$1"
        for excluded in "${exclude_folders[@]}"; do
            if [[ "$folder_name" == "$excluded" ]]; then
                return 0
            fi
        done
        return 1
    }

    # Create file in root folder if it doesn't exist
    if [ ! -f "$root_folder/$file_name" ]; then
        touch "$root_folder/$file_name"
        echo "Created $file_name in $root_folder"
    else
        echo "$file_name already exists in $root_folder"
    fi

    # Traverse subdirectories
    find "$root_folder" -type d | while read -r dir; do
        dir_name=$(basename "$dir")
        if ! is_excluded "$dir_name"; then
            file_path="$dir/$file_name"
            if [ ! -f "$file_path" ]; then
                touch "$file_path"
                echo "Created $file_name in $dir"
            else
                echo "$file_name already exists in $dir"
            fi
        fi
    done
}


# Python facepalm moment
create_file_if_not_exists_excluding_folders "./src" "__pycache__" "__init__.py"
create_file_if_not_exists_excluding_folders "./src" "__pycache__" "py.typed"

create_file_if_not_exists_excluding_folders "./tests" "__pycache__" "__init__.py"
create_file_if_not_exists_excluding_folders "./tests" "__pycache__" "py.typed"

create_directory_if_not_exists "./test_data/domain"
create_file_if_not_exists_excluding_folders "./test_data" "__pycache__" "__init__.py"
create_file_if_not_exists_excluding_folders "./test_data" "__pycache__" "py.typed"

# Make files +x
find . -type f -name "*.sh" -exec chmod +x {} +
find . -type f -name "*.sh"