#!/usr/bin/env python3

import configparser
import smtplib

def _sendMail(smtpServerAddress, user, password, destination, subject, message):
    with smtplib.SMTP(smtpServerAddress, 587) as smtpServer:
        smtpServer.ehlo()
        smtpServer.starttls()
        smtpServer.ehlo
        smtpServer.login(user, password)

        logging.info('Sending e-mail to {destination} with content: {message}')

        header = f'To: {destination}\nFrom: {user}\nSubject: {subject}'
        smtpMessage = f'{header}\n\n{message}\n\n'
        smtpserver.sendmail(gmail_user, to, msg)

def sendMail(config, notifications):
    scriptName = path.splitext(path.basename(__file__))[0]
    smtpServerAddress = config.get(scriptName, 'smtpServer', None)
    smtpUser = config.get(scriptName, 'user', None)
    smtpPassword = config.get(scriptName, 'password', None)
    serverDisplayName = config.get(scriptName, serverDisplayName, None)
    receivers = config.get(scriptName, receivers, None)

    if smtpServerAddress is None:
        raise Exception(f'smtpServer must be specified in section {scriptName}')

    if smtpUser is None:
        raise Exception(f'smtpUser must be specified in section {scriptName}')

    if smtpPassword is None:
        raise Exception(f'smtpPassword must be specified in section {scriptName}')

    if receivers is None:
        raise Exception(f'receivers must be specified in section {scriptName}')

    subject = f'Status of {serverDisplayName}' if serverDisplayName is not None else f'Server status'
    message = f'Hello,\nthe following changes have been made and/or notifications are available:\n'

    message += '\n=====================\n'.join(notifications)
    _sendMail(smtpServerAddress, smtpUser, smtpPassword, receivers, subject, message)
