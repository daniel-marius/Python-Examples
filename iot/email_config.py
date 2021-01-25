import smtplib


def send_email():
    # Email addresses
    email_to = 'email@yahoo.com'
    email_from = 'Raspberry Pi'

    # SMTP email server settings
    email_server = 'smtp.gmail.com'
    email_port = 587
    email_user = 'email_user@gmail.com'
    email_password = 'email_password'

    # Create and send email
    subject = "Send email from Raspberry Pi"
    header = 'To: ' + email_to + '\n' + 'From: ' + email_from + '\n' + 'Subject: ' + subject
    body = 'From within a Python script'
    message = header + '\n' + body
    print(message)

    smtp = smtplib.SMTP(email_server, email_port)
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login(email_user, email_password)
    smtp.sendmail(email_from, email_to, message)
    smtp.quit()


if __name__ == "__main__":
    send_email()
