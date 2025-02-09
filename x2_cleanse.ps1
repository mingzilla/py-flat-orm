function Create-FileIfNotExists {
    param (
        [string]$RootFolder,
        [string]$FileName
    )

    Get-ChildItem -Path $RootFolder -Recurse -Directory | ForEach-Object {
        $filePath = Join-Path $_.FullName $FileName
        if (-not (Test-Path $filePath)) {
            New-Item -Path $filePath -ItemType File -Force | Out-Null
            Write-Host "Created $FileName in $($_.FullName)"
        }
    }

    # Check for the file in the root folder itself
    $rootFilePath = Join-Path $RootFolder $FileName
    if (-not (Test-Path $rootFilePath)) {
        New-Item -Path $rootFilePath -ItemType File -Force | Out-Null
        Write-Host "Created $FileName in $RootFolder"
    }
}

function Create-DirectoryIfNotExists {
    param (
        [string]$Path
    )

    if (-not (Test-Path -Path $Path)) {
        New-Item -Path $Path -ItemType Directory
        Write-Host "Created directory: $Path"
    }
}

function Clean-FileFromFolders {
    param (
        [string]$RootFolder,       # The root folder to start searching
        [string]$FolderNameToAct,  # The folder name to target
        [string]$FileName          # The file name to delete
    )

    # Get all subdirectories under the RootFolder
    Get-ChildItem -Path $RootFolder -Recurse -Directory | Where-Object {
        $_.Name -eq $FolderNameToAct
    } | ForEach-Object {
        $targetFilePath = Join-Path $_.FullName $FileName

        if (Test-Path $targetFilePath) {
            Remove-Item -Path $targetFilePath -Force
            Write-Host "Deleted file: $targetFilePath"
        }
    }
}

function Create-FileIfNotExistsExcludingFolders {
    param (
        [string]$RootFolder,
        [string]$FoldersToExclude, # e.g. "__pycache__, hello" - separated by ,
        [string]$FileName
    )

    # Convert comma-separated string to array and trim each element
    $excludeFolders = $FoldersToExclude.Split(',') | ForEach-Object { $_.Trim() }

    Get-ChildItem -Path $RootFolder -Recurse -Directory | Where-Object {
        $folderName = $_.Name
        -not ($excludeFolders -contains $folderName)
    } | ForEach-Object {
        $filePath = Join-Path $_.FullName $FileName
        if (-not (Test-Path $filePath)) {
            New-Item -Path $filePath -ItemType File -Force | Out-Null
            Write-Host "Created $FileName in $($_.FullName)"
        }
    }

    # Check for the file in the root folder itself
    $rootFilePath = Join-Path $RootFolder $FileName
    if (-not (Test-Path $rootFilePath)) {
        New-Item -Path $rootFilePath -ItemType File -Force | Out-Null
        Write-Host "Created $FileName in $RootFolder"
    }
}

# Python facepalm moment
Create-FileIfNotExistsExcludingFolders -RootFolder "./src" -FoldersToExclude "__pycache__" -FileName "__init__.py"
Create-FileIfNotExistsExcludingFolders -RootFolder "./src" -FoldersToExclude "__pycache__" -FileName "py.typed"

Create-FileIfNotExistsExcludingFolders -RootFolder "./tests" -FoldersToExclude "__pycache__" -FileName "__init__.py"
Create-FileIfNotExistsExcludingFolders -RootFolder "./tests" -FoldersToExclude "__pycache__" -FileName "py.typed"

Create-DirectoryIfNotExists -Path "./test_data/domain"
Create-FileIfNotExistsExcludingFolders -RootFolder "./test_data" -FoldersToExclude "__pycache__" -FileName "__init__.py"
Create-FileIfNotExistsExcludingFolders -RootFolder "./test_data" -FoldersToExclude "__pycache__" -FileName "py.typed"
