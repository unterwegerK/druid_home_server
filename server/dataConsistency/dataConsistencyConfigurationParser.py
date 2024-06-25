from configuration import StaticSection, DynamicSection

def getBackupVolumes(configuration):
    numberOfVolumes = int(configuration.get('backup', 'numberofvolumes', -1))

    if numberOfVolumes == -1:
        raise Exception('numberofvolumes needs to be defined in Section "backup"')

    for i in range(numberOfVolumes):
        staticSection = StaticSection(configuration, 'backupVolume' + str(i))
        dynamicSection = DynamicSection(configuration, 'backupVolume' + str(i))

        fileSystem = staticSection.get('filesystem', None)
        if fileSystem is None:
            errorMessage = f'Key filesystem must be defined in Section {staticSection.sectionName}'
            raise Exception(errorMessage)

        yield (fileSystem, staticSection, dynamicSection)