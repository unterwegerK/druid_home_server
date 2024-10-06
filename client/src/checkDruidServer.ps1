#This script is used to check whether the druid server currently is reachable and start it if the
#waiting interval is expired.

$scriptDirectory = Split-Path $MyInvocation.MyCommand.Path
. "$scriptDirectory\configuration.ps1"
. "$scriptDirectory\network.ps1"

#MAIN
if(-not $args[0] -or -not $args[1] -or -not $args[2])
{
    Start-Transcript -Path $Env:AppData\DruidHomeServerClient\log.txt
    $scriptName = $MyInvocation.MyCommand.Name
    Write-Output "Usage: $scriptName <staticConfigurationFilePath> <dynamicConfigurationFilePath> <logFilePath>"
    Stop-Transcript
    exit 1
}

Start-Transcript -Path $args[2]

$staticConfiguration = GetConfiguration $args[0]
$dynamicConfiguration = GetConfiguration $args[1] $true

$hostName = $staticConfiguration.druid.host
$macAddress = $staticConfiguration.druid.macAddress
$broadcastAddress = $staticConfiguration.druid.broadcastAddress

if(-not $hostName)
{
    Write-Output "No hostname specified in configuration."
    exit 2
}

if(-not $macAddress)
{
    Write-Output "No mac address specified in configuration."
    exit 3
}

if(CheckExistingConnection "$hostName" -or CheckConnection "$hostName")
{
    Write-Output "Found connection"
    SetTimestamp $dynamicConfiguration    
}
elseif(CheckTimeSinceLastConnection $dynamicConfiguration)
{
    Write-Output "Starting server with MAC address $macAddress."
    StartHost($macAddress, $broadcastAddress)
}
Write-Output "Finished"
$dynamicConfiguration.Save($args[1])

Stop-Transcript