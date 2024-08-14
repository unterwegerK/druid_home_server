import smtplib

class EMailSender:
    def sendEMail(smtpServerAddress, user, password, destination, subject, message):
        with smtplib.SMTP(smtpServerAddress, 587) as smtpServer:
            smtpServer.ehlo()
            smtpServer.starttls()
            smtpServer.ehlo
            smtpServer.login(user, password)

            header = f'To: {destination}\nFrom: {user}\nSubject: {subject}'
            smtpMessage = f'{header}\n\n{message}\n\n'
            smtpServer.sendmail(user, destination, smtpMessage)