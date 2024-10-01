
function getSourceDirectory($scriptDirectory)
{
    return Join-Path $scriptDirectory "druidhomeserverclient"
}

function getInstallationDirectory()
{
    return Join-Path $Env:ProgramFiles "DruidHomeServerClient"
}

function getConfigurationSourceDirectory($scriptDirectory)
{
    return Join-Path $scriptDirectory "configuration"
}

function getConfigurationInstallationDirectory()
{
    return Join-Path $env:AppData DruidHomeServerClient
}