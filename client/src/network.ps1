
function CheckExistingConnection($hostName)
{
    $ipAddresses = [System.Collections.Generic.HashSet[System.String]]::new()
    foreach($serverAddress in [System.Net.Dns]::GetHostAddresses("$hostName"))
    {
        $ipAddresses.Add($serverAddress.ToString()) | out-null
    }
    
    $foundConnection = $false
    foreach($connection in Get-NetTCPConnection -State Established)
    {
        $remoteAddress = $connection.RemoteAddress
        if($ipAddresses.Contains($remoteAddress)) 
        {
            $foundConnection = $true
        }
    }

    return $foundConnection
}

function CheckConnection($hostName)
{
    return (Test-Connection $hostName -Count 1 -ErrorAction 0 -quiet)
}

function StartHost($macAddress, $broadcastAddress)
{
    if($broadcastAddress)
    {
        & wakeonlan $macAddress $broadcastAddress
    }
    else {
        & wakeonlan $macAddress
    }
    
}