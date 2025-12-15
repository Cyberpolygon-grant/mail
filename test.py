import imaplib
import email
from email.header import decode_header

# Подключение к IMAP
mail = imaplib.IMAP4('localhost', 1143)  # Прямой доступ к dovecot
mail.login('operator1@financepro.ru', '1q2w#E$R')
print("✅ Подключение успешно!")

# Выбираем INBOX
mail.select('INBOX')

# Ищем все письма и сортируем по дате (последнее первым)
status, messages = mail.search(None, 'ALL')
if status != 'OK':
    print("❌ Ошибка поиска писем")
    mail.logout()
    exit(1)

# Получаем список ID писем
email_ids = messages[0].split()
if not email_ids:
    print("📭 Нет писем в INBOX")
    mail.logout()
    exit(0)

# Берём последнее письмо (самое новое)
latest_email_id = email_ids[-1]

# Получаем письмо
status, msg_data = mail.fetch(latest_email_id, '(RFC822)')
if status != 'OK':
    print("❌ Ошибка получения письма")
    mail.logout()
    exit(1)

# Парсим письмо
raw_email = msg_data[0][1]
email_message = email.message_from_bytes(raw_email)

# Выводим заголовки
print("\n" + "="*60)
print("📧 ПОСЛЕДНЕЕ ПИСЬМО:")
print("="*60)

# Функция для декодирования заголовков
def decode_mime_header(s):
    if s is None:
        return ""
    decoded_parts = decode_header(s)
    decoded_str = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            decoded_str += part.decode(encoding or 'utf-8', errors='ignore')
        else:
            decoded_str += part
    return decoded_str

# Выводим основные заголовки
print(f"From: {decode_mime_header(email_message['From'])}")
print(f"To: {decode_mime_header(email_message['To'])}")
print(f"Subject: {decode_mime_header(email_message['Subject'])}")
print(f"Date: {email_message['Date']}")
print(f"Message-ID: {email_message.get('Message-ID', 'N/A')}")

# Выводим спам-заголовки
print("\n--- Спам-заголовки ---")
spam_headers = ['X-Spam', 'X-Spam-Level', 'X-Spamd-Bar', 'X-Spam-Flag', 'X-Spam-Status', 'X-Spam-Score']
for header in spam_headers:
    value = email_message.get(header)
    if value:
        print(f"{header}: {value}")

# Выводим тело письма
print("\n--- Тело письма ---")
if email_message.is_multipart():
    for part in email_message.walk():
        content_type = part.get_content_type()
        content_disposition = str(part.get("Content-Disposition"))
        
        if content_type == "text/plain" and "attachment" not in content_disposition:
            body = part.get_payload(decode=True)
            if body:
                try:
                    print(body.decode('utf-8', errors='ignore'))
                except:
                    print(body.decode('latin-1', errors='ignore'))
else:
    body = email_message.get_payload(decode=True)
    if body:
        try:
            print(body.decode('utf-8', errors='ignore'))
        except:
            print(body.decode('latin-1', errors='ignore'))

print("="*60)

mail.logout()
print("✅ Отключение успешно!")
