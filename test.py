import imaplib
mail = imaplib.IMAP4('localhost', 143)
mail.login('operator1@financepro.ru', '1q2w#E$R')
print("✅ Подключение успешно!")
mail.list()
mail.logout()
