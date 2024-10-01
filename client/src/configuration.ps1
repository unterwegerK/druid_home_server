

function CreateConfiguration()
{
    $configuration = New-Object System.Xml.XmlDocument
    $rootElement = $configuration.CreateElement("druid")
    [void]$configuration.AppendChild($rootElement)
    return $configuration
}

function GetConfiguration($configurationFilePath, $createIfNecessary)
{
    if(Test-Path "$configurationFilePath") {
        [xml]$configuration = Get-Content "$configurationFilePath"

        if($null -eq $configuration)
        {
            $configuration = CreateConfiguration
        }
    } elseif($createIfNecessary) {
        $configuration = CreateConfiguration
    } else {
        Write-Error "Configuration file $configurationFilePath does not exist." 
        exit 2
    }
    return $configuration
}

function SetTimestamp($configuration)
{
        $timestamp = $(get-date -format "yyyy-MM-dd HH:mm:ss")
        $lastConnection = $configuration.SelectSingleNode("/druid/lastConnection")
        if($null -eq $lastConnection)
        {
            $rootNode = $configuration.SelectSingleNode("/druid")

            if($null -eq $rootNode)
            {
                Write-Error "Root node 'druid' does not exist in dynamic configuration-file." 
                exit 2
            }

            $lastConnection = $configuration.CreateElement("lastConnection")
            $lastConnection = $rootNode.AppendChild($lastConnection)
        }

        $lastConnection.set_InnerText($timestamp)
}

function CheckTimeSinceLastConnection($configuration)
{
    $lastConnection = $configuration.SelectSingleNode("/druid/lastConnection")
    if($null -eq $lastConnection)
    {
        return $true
    }
    $lastConnectionDateTime = [datetime]::ParseExact($lastConnection.Innertext, 'yyyy-MM-dd HH:mm:ss', $null)
    $currentDateTime = get-date
    return $currentDateTime -gt $lastConnectionDateTime.AddDays(1)
}
