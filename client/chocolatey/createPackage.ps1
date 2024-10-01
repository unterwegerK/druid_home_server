$scriptPath = split-path -parent $MyInvocation.MyCommand.Definition
choco pack "$scriptPath/druidhomeserverclient/druidhomeserverclient.nuspec" --outputdirectory "$scriptPath/packages/"