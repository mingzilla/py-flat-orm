function Create-FileIfNotExists {
    param (
        [string]$FileName
    )

    Get-ChildItem -Path "./src" -Recurse -Directory | ForEach-Object {
        $filePath = Join-Path $_.FullName $FileName
        if (-not (Test-Path $filePath)) {
            New-Item -Path $filePath -ItemType File -Force | Out-Null
            Write-Host "Created $FileName in $($_.FullName)"
        } else {
            Write-Host "$FileName already exists in $($_.FullName)"
        }
    }

    # Check for the file in the ./src directory itself
    $srcFilePath = Join-Path "./src" $FileName
    if (-not (Test-Path $srcFilePath)) {
        New-Item -Path $srcFilePath -ItemType File -Force | Out-Null
        Write-Host "Created $FileName in ./src"
    } else {
        Write-Host "$FileName already exists in ./src"
    }
}

# Python facepalm moment
Create-FileIfNotExists -FileName "__init__.py"
Create-FileIfNotExists -FileName "py.typed"
