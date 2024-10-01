$toolsDirectory   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
. "$toolsDirectory\paths.ps1"

#Uninstall scheduler task
$task = Get-ScheduledTask -TaskName "StartDruidServer"

if($null -ne $task) {
    Unregister-ScheduledTask -TaskName $task.TaskName -TaskPath $task.TaskPath -Confirm:$false
}

#Uninstall files
$sourceDirectory = getSourceDirectory($toolsDirectory)
$installDirectory = getInstallationDirectory

Write-Output "Uninstall from $installDirectory"

Get-ChildItem $sourceDirectory -Recurse |
Foreach-Object {
    $installedFile = Join-Path $installDirectory $_.Name
    Remove-Item -LiteralPath $installedFile -Force
}

if((Get-ChildItem $installDirectory | Measure-Object).count -eq 0)
{
    Remove-Item $installDirectory
}
else {
    Write-Warning "Could not delete installation directory $installDirectory because it is not empty."
    exit 1
}