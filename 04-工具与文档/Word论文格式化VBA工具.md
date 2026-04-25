# Word 论文格式化 VBA 工具集

毕业论文写作中常用的 Word VBA 宏代码，用于快速完成格式化操作。

---

## 导入方法

1. 打开 Word，按 `Alt + F11` 打开 VBA 编辑器
2. 在左侧项目窗口中，右键当前文档 → 插入 → 模块
3. 将下方代码复制粘贴到模块中
4. 关闭 VBA 编辑器，返回 Word

---

## 宏功能说明

| 宏名称 | 功能 | 建议快捷键 |
|--------|------|------------|
| `PasteImageFormatted` | 粘贴图片：居中+单倍行距+嵌入式 | Ctrl+Alt+I |
| `FormatCitationsAsSuperscript` | 引用编号批量上标（如[1]→上标） | Ctrl+Alt+S |
| `FormatTableToThreeLine` | 当前表格→三线表格式 | Ctrl+Alt+T |
| `FormatAllTablesToThreeLine` | 全文所有表格→三线表格式 | Ctrl+Alt+A |
| `FormatAllImagesCenter` | 全文所有图片居中+单倍行距+嵌入式 | Ctrl+Alt+M |
| `ConvertPipeToTable` | 管道符文本转三线表（Markdown表格转Word） | Ctrl+Alt+P |
| `FormatFigureCaption` | 格式化图题：居中+宋体/TNR+五号+20磅行距 | Ctrl+Alt+F |

---

## 快捷键绑定方法

1. Word 菜单：文件 → 选项 → 自定义功能区 → 自定义键盘快捷键
2. 在"类别"中选择"宏"
3. 选择对应宏名，按下组合键，点击"指定"

**建议快捷键组合：**
- Ctrl+Alt+F → FormatFigureCaption（每插完一张图按一下格式化图题）
- Ctrl+Alt+I → PasteImageFormatted（粘贴图片自动格式化）
- Ctrl+Alt+S → FormatCitationsAsSuperscript（选中区域后批量上标引用）
- Ctrl+Alt+T → FormatTableToThreeLine（光标在表格内时应用三线表）

---

## VBA 代码

```vb
Attribute VB_Name = "PaperTools"
Option Explicit

Private Sub ApplyImageParaFormat(oPara As Paragraph)
    On Error Resume Next
    oPara.Style = ActiveDocument.Styles(wdStyleNormal)
    With oPara.Format
        .Alignment = wdAlignParagraphCenter
        .LineSpacingRule = wdLineSpaceSingle
        .LineSpacing = 12
        .SpaceBefore = 0
        .SpaceAfter = 0
        .SpaceBeforeAuto = False
        .SpaceAfterAuto = False
        .WidowControl = False
        .KeepWithNext = False
        .KeepTogether = False
    End With
    On Error GoTo 0
End Sub

Private Sub ApplyThreeLineFormat(oTable As Table)
    Dim oRow As Row
    Dim oCell As Cell

    ' 第一步：整体清除
    With oTable.Borders
        .InsideLineStyle = wdLineStyleNone
        .OutsideLineStyle = wdLineStyleNone
    End With

    ' 第二步：逐行清除行级别边框（解决行底部线残留）
    For Each oRow In oTable.Rows
        With oRow.Borders
            .InsideLineStyle = wdLineStyleNone
            .OutsideLineStyle = wdLineStyleNone
        End With
        oRow.Borders(wdBorderTop).LineStyle = wdLineStyleNone
        oRow.Borders(wdBorderBottom).LineStyle = wdLineStyleNone
        oRow.Borders(wdBorderLeft).LineStyle = wdLineStyleNone
        oRow.Borders(wdBorderRight).LineStyle = wdLineStyleNone
        oRow.Borders(wdBorderHorizontal).LineStyle = wdLineStyleNone
    Next oRow

    ' 第三步：逐单元格清除（解决竖线残留）
    For Each oRow In oTable.Rows
        For Each oCell In oRow.Cells
            oCell.Borders(wdBorderLeft).LineStyle = wdLineStyleNone
            oCell.Borders(wdBorderRight).LineStyle = wdLineStyleNone
            oCell.Borders(wdBorderTop).LineStyle = wdLineStyleNone
            oCell.Borders(wdBorderBottom).LineStyle = wdLineStyleNone
        Next oCell
    Next oRow

    ' 第四步：画三条线
    ' 逐单元格设置，避免合并单元格或内容换行导致线断开

    ' 顶部粗线：第一行每个单元格顶部（1.5磅）
    Dim oCell2 As Cell
    For Each oCell2 In oTable.Rows(1).Cells
        With oCell2.Borders(wdBorderTop)
            .LineStyle = wdLineStyleSingle
            .LineWidth = wdLineWidth150pt
            .Color = wdColorBlack
        End With
    Next oCell2

    ' 表头下细线：第一行每个单元格底部（0.5磅）
    For Each oCell2 In oTable.Rows(1).Cells
        With oCell2.Borders(wdBorderBottom)
            .LineStyle = wdLineStyleSingle
            .LineWidth = wdLineWidth050pt
            .Color = wdColorBlack
        End With
    Next oCell2

    ' 底部粗线：最后一行每个单元格底部（1.5磅）
    For Each oCell2 In oTable.Rows(oTable.Rows.Count).Cells
        With oCell2.Borders(wdBorderBottom)
            .LineStyle = wdLineStyleSingle
            .LineWidth = wdLineWidth150pt
            .Color = wdColorBlack
        End With
    Next oCell2
End Sub

' ------------------------------------------------------------
' Macro 1: 粘贴图片 - 居中+单倍行距+嵌入式
' ------------------------------------------------------------
Sub PasteImageFormatted()
    On Error GoTo ErrHandler

    Dim posStart As Long
    posStart = Selection.Start

    Selection.Paste

    Dim posEnd As Long
    posEnd = Selection.End

    Dim pastedRange As Range
    Set pastedRange = ActiveDocument.Range(posStart, posEnd)

    If pastedRange.Start = pastedRange.End Then Exit Sub

    Dim k As Integer
    For k = ActiveDocument.Shapes.Count To 1 Step -1
        On Error Resume Next
        Dim oShp As Shape
        Set oShp = ActiveDocument.Shapes(k)
        If oShp.Anchor.Start >= posStart And oShp.Anchor.Start <= posEnd Then
            oShp.ConvertToInlineShape
        End If
        On Error GoTo ErrHandler
    Next k

    Set pastedRange = ActiveDocument.Range(posStart, Selection.End)

    Dim oPara As Paragraph
    For Each oPara In pastedRange.Paragraphs
        ApplyImageParaFormat oPara
    Next oPara

    With Selection.ParagraphFormat
        .Alignment = wdAlignParagraphCenter
        .LineSpacingRule = wdLineSpaceSingle
        .LineSpacing = 12
        .SpaceBefore = 0
        .SpaceAfter = 0
        .SpaceBeforeAuto = False
        .SpaceAfterAuto = False
    End With

    Exit Sub
ErrHandler:
    MsgBox "Error: " & Err.Description, vbCritical
End Sub

' ------------------------------------------------------------
' Macro 2: 引用编号批量上标
' ------------------------------------------------------------
Sub FormatCitationsAsSuperscript()
    On Error GoTo ErrHandler

    If Selection.Type = wdSelectionIP Then
        MsgBox "Please select a text range first, then run the macro.", vbExclamation
        Exit Sub
    End If

    Dim oRange As Range
    Set oRange = Selection.Range

    Dim oRegex As Object
    Set oRegex = CreateObject("VBScript.RegExp")
    oRegex.Pattern = "\[\d+\]"
    oRegex.Global = True

    Dim oMatches As Object
    Set oMatches = oRegex.Execute(oRange.Text)

    If oMatches.Count = 0 Then
        MsgBox "No citation numbers like [1] found in the selected range.", vbInformation
        Exit Sub
    End If

    Dim processed As Integer
    processed = 0

    Dim i As Integer
    For i = 0 To oMatches.Count - 1
        Dim oMatch As Object
        Set oMatch = oMatches(i)

        Dim matchRange As Range
        Set matchRange = ActiveDocument.Range( _
            oRange.Start + oMatch.FirstIndex, _
            oRange.Start + oMatch.FirstIndex + oMatch.Length)

        If matchRange.Start >= oRange.Start And matchRange.End <= oRange.End Then
            matchRange.Font.Superscript = True
            matchRange.Font.Subscript = False
            processed = processed + 1
        End If
    Next i

    MsgBox "Done! Processed " & processed & " citation(s).", vbInformation
    Exit Sub
ErrHandler:
    MsgBox "Error: " & Err.Description, vbCritical
End Sub

' ------------------------------------------------------------
' Macro 3: 当前表格三线表
' ------------------------------------------------------------
Sub FormatTableToThreeLine()
    On Error GoTo ErrHandler

    If Not Selection.Information(wdWithInTable) Then
        MsgBox "Please place the cursor inside a table first.", vbExclamation
        Exit Sub
    End If

    Call ApplyThreeLineFormat(Selection.Tables(1))
    MsgBox "Three-line table format applied!", vbInformation
    Exit Sub
ErrHandler:
    MsgBox "Error: " & Err.Description, vbCritical
End Sub

' ------------------------------------------------------------
' Macro 4: 全文所有表格三线表
' ------------------------------------------------------------
Sub FormatAllTablesToThreeLine()
    On Error GoTo ErrHandler

    Dim tableCount As Integer
    tableCount = ActiveDocument.Tables.Count

    If tableCount = 0 Then
        MsgBox "No tables found in this document.", vbInformation
        Exit Sub
    End If

    Dim oTable As Table
    Dim successCount As Integer
    successCount = 0

    For Each oTable In ActiveDocument.Tables
        On Error Resume Next
        Call ApplyThreeLineFormat(oTable)
        If Err.Number = 0 Then successCount = successCount + 1
        Err.Clear
        On Error GoTo ErrHandler
    Next oTable

    MsgBox "Done! Processed " & successCount & " / " & tableCount & " table(s).", vbInformation
    Exit Sub
ErrHandler:
    MsgBox "Error: " & Err.Description, vbCritical
End Sub

' ------------------------------------------------------------
' Macro 5: 全文所有图片居中+单倍行距+嵌入式
' ------------------------------------------------------------
Sub FormatAllImagesCenter()
    On Error GoTo ErrHandler

    Dim shapeCount As Integer
    shapeCount = ActiveDocument.Shapes.Count
    Dim convertedCount As Integer
    convertedCount = 0

    If shapeCount > 0 Then
        Dim i As Integer
        For i = shapeCount To 1 Step -1
            On Error Resume Next
            Dim oShp As Shape
            Set oShp = ActiveDocument.Shapes(i)
            If oShp.Type = msoPicture Or oShp.Type = msoLinkedPicture Then
                oShp.ConvertToInlineShape
                convertedCount = convertedCount + 1
            End If
            On Error GoTo ErrHandler
        Next i
    End If

    Dim imgCount As Integer
    imgCount = ActiveDocument.InlineShapes.Count

    If imgCount = 0 Then
        MsgBox "No images found in this document.", vbInformation
        Exit Sub
    End If

    Dim j As Integer
    Dim successCount As Integer
    successCount = 0

    For j = 1 To imgCount
        On Error Resume Next
        Dim oPara As Paragraph
        Set oPara = ActiveDocument.InlineShapes(j).Range.Paragraphs(1)
        ApplyImageParaFormat oPara
        If Err.Number = 0 Then successCount = successCount + 1
        Err.Clear
        On Error GoTo ErrHandler
    Next j

    Dim msg As String
    msg = "Done! Processed " & successCount & " / " & imgCount & " image(s)."
    If convertedCount > 0 Then
        msg = msg & Chr(10) & "(" & convertedCount & " floating image(s) converted to inline)"
    End If
    MsgBox msg, vbInformation
    Exit Sub
ErrHandler:
    MsgBox "Error: " & Err.Description, vbCritical
End Sub

' ------------------------------------------------------------
' Macro 6: 把选中的 | 分隔文本转换为三线表格
' 用法：选中类似 "A | B | C" 的多行文本，运行宏
' 第一行如果是 "--- | --- | ---" 分隔行会自动跳过
' ------------------------------------------------------------
Sub ConvertPipeToTable()
    On Error GoTo ErrHandler

    If Selection.Type = wdSelectionIP Then
        MsgBox "Please select the pipe-separated text first.", vbExclamation
        Exit Sub
    End If

    Dim selectedText As String
    selectedText = Selection.Text

    ' 兼容不同换行符
    selectedText = Join(Split(selectedText, Chr(10)), Chr(13))
    Dim lines() As String
    lines = Split(selectedText, Chr(13))

    ' 过滤空行和纯分隔行（--- | --- 这种）
    Dim validLines() As String
    ReDim validLines(UBound(lines))
    Dim validCount As Integer
    validCount = 0

    Dim i As Integer
    For i = 0 To UBound(lines)
        Dim trimmed As String
        trimmed = Trim(lines(i))
        If Len(trimmed) = 0 Then GoTo NextLine

        Dim isSep As Boolean
        isSep = True
        Dim c As Integer
        For c = 1 To Len(trimmed)
            Dim ch As String
            ch = Mid(trimmed, c, 1)
            If ch <> "-" And ch <> "|" And ch <> " " Then
                isSep = False
                Exit For
            End If
        Next c

        If Not isSep Then
            validLines(validCount) = trimmed
            validCount = validCount + 1
        End If
NextLine:
    Next i

    If validCount = 0 Then
        MsgBox "No valid content found.", vbInformation
        Exit Sub
    End If

    ' 按第一行算列数
    Dim firstCells() As String
    firstCells = Split(validLines(0), "|")
    Dim colCount As Integer
    colCount = 0
    Dim fc As Integer
    For fc = 0 To UBound(firstCells)
        If Len(Trim(firstCells(fc))) > 0 Then colCount = colCount + 1
    Next fc

    If colCount = 0 Then
        MsgBox "Cannot determine column count.", vbInformation
        Exit Sub
    End If

    ' 删除选中文本，在原位置插入表格
    Dim insertRange As Range
    Set insertRange = Selection.Range
    insertRange.Delete

    Dim oTable As Table
    Set oTable = ActiveDocument.Tables.Add(insertRange, validCount, colCount)

    ' 填充内容
    Dim r As Integer
    For r = 0 To validCount - 1
        Dim cellValues() As String
        cellValues = Split(validLines(r), "|")

        Dim colIndex As Integer
        colIndex = 1
        Dim cv As Integer
        For cv = 0 To UBound(cellValues)
            Dim cellText As String
            cellText = Trim(cellValues(cv))
            If Len(cellText) > 0 Then
                If colIndex <= colCount Then
                    oTable.Cell(r + 1, colIndex).Range.Text = cellText
                    colIndex = colIndex + 1
                End If
            End If
        Next cv
    Next r

    ' 应用三线表格式
    Call ApplyThreeLineFormat(oTable)

    ' 表格整体居中
    oTable.Rows.Alignment = wdAlignRowCenter

    MsgBox "Done! Created " & validCount & " x " & colCount & " table.", vbInformation
    Exit Sub
ErrHandler:
    MsgBox "Error: " & Err.Description, vbCritical
End Sub

' ------------------------------------------------------------
' Macro 7: 格式化图题（居中+宋体/Times New Roman+五号+20磅行距）
' 用法：光标放在图题所在行，或选中多行图题，运行宏
' ------------------------------------------------------------
Sub FormatFigureCaption()
    On Error GoTo ErrHandler

    Dim targetRange As Range

    ' 有选中内容就处理选中范围，否则处理光标所在段落
    If Selection.Type <> wdSelectionIP Then
        Set targetRange = Selection.Range
    Else
        Set targetRange = Selection.Paragraphs(1).Range
    End If

    Dim oPara As Paragraph
    For Each oPara In targetRange.Paragraphs
        ' 跳过空段落
        If Len(Trim(oPara.Range.Text)) <= 1 Then GoTo NextPara

        ' 段落格式
        With oPara.Format
            .Alignment = wdAlignParagraphCenter
            .LineSpacingRule = wdLineSpaceExactly
            .LineSpacing = 20          ' 20磅固定行距
            .SpaceBefore = 0
            .SpaceAfter = 0
            .SpaceBeforeAuto = False
            .SpaceAfterAuto = False
        End With

        ' 字体格式：中文宋体，英文Times New Roman，五号（10.5磅）
        With oPara.Range.Font
            .Size = 10.5               ' 五号
            .Color = wdColorBlack
            .Bold = False
            .Italic = False
            .Name = "Times New Roman"  ' 英文字体
            .NameFarEast = "宋体"      ' 中文字体
        End With

NextPara:
    Next oPara

    MsgBox "Done! Figure caption format applied.", vbInformation
    Exit Sub
ErrHandler:
    MsgBox "Error: " & Err.Description, vbCritical
End Sub
```

---

## 使用提示

1. **粘贴图片后格式化**：复制图片 → Ctrl+V → 按 Ctrl+Alt+I 自动居中
2. **图题格式化**：光标放在图题行 → Ctrl+Alt+F 自动应用宋体/TNR+五号+居中+20磅行距
3. **批量处理引用上标**：选中正文段落 → Ctrl+Alt+S 所有 `[1]` `[2]` 等自动变上标
4. **Markdown表格转Word**：从文档/网页复制管道符表格 → 选中 → Ctrl+Alt+P 自动生成三线表