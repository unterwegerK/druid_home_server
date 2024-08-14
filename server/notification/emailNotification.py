#!/usr/bin/env python3
import logging
from os import path
from notification.notification import Notification, Severity

def _concatenateNotifications(notifications):
    severityNotifications = list(filter(lambda n: isinstance(n, Notification), notifications))
    errorNotifications = list(filter(lambda n: n.severity == Severity.ERROR, severityNotifications))
    infoNotifications = list(filter(lambda n: n.severity != Severity.ERROR, severityNotifications))
    stringNotifications = list(filter(lambda n: not isinstance(n, Notification), notifications))

    concatenated = '\n'.join(map(lambda n: 'ERROR: ' + n.header, errorNotifications))

    concatenated += '\n\n'

    concatenated += '\n'.join(map(lambda n: f'==== {n.header} (ERROR) ====\n{n.message}\n', errorNotifications))

    concatenated += '\n'

    concatenated += '\n'.join(map(lambda n: f'==== {n.header} (INFO) ====\n{n.message}\n', infoNotifications))

    concatenated += '\n'

    concatenated += '\n'.join(map(lambda n: f'=====================\n{n}\n',stringNotifications))

    return concatenated

def sendMail(config, notifications, sender):
    scriptName = path.splitext(path.basename(__file__))[0]
    smtpServerAddress = config.get(scriptName, 'smtpServer', None)
    smtpUser = config.get(scriptName, 'user', None)
    smtpPassword = config.get(scriptName, 'password', None)
    serverDisplayName = config.get(scriptName, 'serverDisplayName', None)
    receivers = config.get(scriptName, 'receivers', None)

    if smtpServerAddress is None:
        raise Exception(f'smtpServer must be specified in section {scriptName}')

    if smtpUser is None:
        raise Exception(f'user must be specified in section {scriptName}')

    if smtpPassword is None:
        raise Exception(f'password must be specified in section {scriptName}')

    if receivers is None:
        raise Exception(f'receivers must be specified in section {scriptName}')

    subject = f'Status of {serverDisplayName}' if serverDisplayName is not None else f'Server status'
    message = f'Hello,\nthe following changes have been made and/or notifications are available:\n'

    message += _concatenateNotifications(notifications)
    
    logging.info(f'Sending e-mail to {receivers} with content: {message}')
    sender.sendEMail(smtpServerAddress, smtpUser, smtpPassword, receivers, subject, message)
