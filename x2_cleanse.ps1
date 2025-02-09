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
        } else {
            Write-Host "$FileName already exists in $($_.FullName)"
        }
    }

    # Check for the file in the root folder itself
    $rootFilePath = Join-Path $RootFolder $FileName
    if (-not (Test-Path $rootFilePath)) {
        New-Item -Path $rootFilePath -ItemType File -Force | Out-Null
        Write-Host "Created $FileName in $RootFolder"
    } else {
        Write-Host "$FileName already exists in $RootFolder"
    }
}

function Create-DirectoryIfNotExist {
    param (
        [string]$Path
    )
    
    if (-not (Test-Path -Path $Path)) {
        New-Item -Path $Path -ItemType Directory
        Write-Host "Created directory: $Path"
    } else {
        Write-Host "Directory $Path already exists"
    }
}

# Python facepalm moment
Create-FileIfNotExists -RootFolder "./src" -FileName "__init__.py"
Create-FileIfNotExists -RootFolder "./src" -FileName "py.typed"

Create-DirectoryIfNotExist -Path "./test_data/domain"
Create-FileIfNotExists -RootFolder "./test_data" -FileName "__init__.py"
Create-FileIfNotExists -RootFolder "./test_data" -FileName "py.typed"
