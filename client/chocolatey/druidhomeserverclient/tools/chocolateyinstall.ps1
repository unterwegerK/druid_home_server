$ErrorActionPreference = 'Stop' # stop on all errors
$toolsDirectory   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"

. "$toolsDirectory\paths.ps1"

#Install files
$sourceDirectory = getSourceDirectory($toolsDirectory)
$installDirectory = getInstallationDirectory
$configurationSourceDirectory = getConfigurationSourceDirectory($toolsDirectory)
$configurationInstallationDirectory = getConfigurationInstallationDirectory
Write-Output "Install to $installDirectory"

#Install scripts
if(-not(Test-Path -PathType container $installDirectory))
{
      New-Item -ItemType Directory -Path $installDirectory
}

Copy-Item $(Join-Path $sourceDirectory "*") -Destination $installDirectory -Recurse -Force

#Install configuration
if(-not(Test-Path -PathType container $configurationInstallationDirectory))
{
      New-Item -ItemType Directory -Path $configurationInstallationDirectory
}
Get-ChildItem $configurationSourceDirectory | ForEach-Object {    
    $destinationFile = Join-Path $configurationInstallationDirectory $_.Name

    if(-not(Test-Path $destinationFile))
    {
        Copy-Item -Path $_.FullName -Destination $destinationFile
    }
}

#Install scheduler task to check and start druid home server
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle hidden -File `"$installDirectory\checkDruidServer.ps1`" `"$configurationInstallationDirectory\config.xml`" `"$configurationInstallationDirectory\settings.xml`" `"$env:AppData\DruidHomeServerClient\log.txt`" "
$trigger = New-ScheduledTaskTrigger -Once -At "10pm" -RepetitionInterval (New-TimeSpan -Minutes 10)
$settings = New-ScheduledTaskSettingsSet -RunOnlyIfNetworkAvailable
$task = New-ScheduledTask -Action $action -Trigger $trigger -Settings $settings -Principal (New-ScheduledTaskPrincipal -UserId "$ENV:USERDOMAIN\$ENV:USERNAME")

Register-ScheduledTask StartDruidServer -InputObject $task -Force

Write-Output "Please adapt configuration in $env:AppData\DruidHomeServerClient\config.xml"
