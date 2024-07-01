from configuration import StaticSection, DynamicSection

def getBackupVolumes(staticConfiguration):
    numberOfVolumes = int(staticConfiguration.get('backup', 'numberofvolumes', -1))

    if numberOfVolumes == -1:
        raise Exception('numberofvolumes needs to be defined in Section "backup"')

    for i in range(numberOfVolumes):
        staticSection = StaticSection(staticConfiguration, 'backupVolume' + str(i))

        fileSystem = staticSection.get('filesystem', None)
        if fileSystem is None:
            errorMessage = f'Key filesystem must be defined in Section {staticSection.sectionName}'
            raise Exception(errorMessage)

        yield (fileSystem)

def getBackupDevices(staticSection):
    return staticSection.get('devices', '').split(';')