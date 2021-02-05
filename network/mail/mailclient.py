import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

server = smtplib.SMTP('smtp.world4you.com', 25)
server.ehlo()

with open('password.txt', 'r') as f:
    password = f.read()

server.login('mailtesting@neuralnine.com', password)

msg = MIMEMultipart()
msg['from'] = 'NeuralNine'
msg['To'] = 'testmails@spam1.de'
msg['Subject'] = 'test'

with open('message.txt', 'r') as f:
    message = f.read()

msg.attach(MIMEText(message, 'plain'))

filename = 'coding.jpg'
attachment = open(filename, 'rb')

payload = MIMEBase('application', 'octet-stream')
payload.set_payload(attachment.read())

encoders.encode_base64(payload)
payload.add_header('Content-Disposition', f'attachment; filename={filename}')
msg.attach(payload)

text = msg.as_string()
server.sendmail('mailtesting@neuralnine.com', 'testmails@spam1.de', text)
