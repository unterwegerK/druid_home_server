from configuration import Section

def getBackupVolumes(configuration):
    numberOfVolumes = int(configuration.get('backup', 'numberofvolumes', -1))

    if numberOfVolumes == -1:
        raise Exception('numberofvolumes needs to be defined in Section "backup"')

    for i in range(numberOfVolumes):
        configurationSection = Section(configuration, 'backupVolume' + str(i))

        fileSystem = configurationSection.get('filesystem', None)
        if fileSystem is None:
            errorMessage = f'Key filesystem must be defined in Section {configurationSection.sectionName}'
            raise Exception(errorMessage)

        yield (fileSystem, configurationSection)