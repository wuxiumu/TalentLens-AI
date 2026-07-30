# Step 2: parse 命令实现

**日期**: 2026-07-30
**状态**: ✅ 完成

## 目标

实现 `resume-cli parse <pdf_path>` 命令，读取 PDF 简历并提取文本内容，支持完善的错误处理。

## 实现内容

### 1. 核心模块：`resume_cli/core/pdf_parser.py`

封装了 PDF 文本提取的核心逻辑，与 CLI 层解耦：

| 函数 | 功能 |
|------|------|
| `extract_text_from_pdf(path)` | 提取 PDF 全部文本 |
| `get_pdf_info(path)` | 获取 PDF 元信息（页数、大小等） |

### 2. 自定义异常体系

```
PDFError (基类)
├── FileNotFoundError_    文件不存在
├── NotPDFError          文件不是 PDF
├── PDFReadError         PDF 无法读取 / 损坏
└── EmptyPDFError        PDF 文本为空
```

### 3. parse 命令功能

| 参数/选项 | 说明 |
|-----------|------|
| `pdf_path` (必选) | PDF 文件路径 |
| `--output, -o` | 将结果保存到文件 |
| `--raw` | 只输出纯文本，不带 JSON 格式 |

### 4. 错误处理流程

```
1. 文件是否存在？ → FileNotFoundError_
2. 扩展名是 .pdf？ → NotPDFError
3. 文件头是 %PDF-？ → NotPDFError（伪装检测）
4. PyMuPDF 能打开？ → PDFReadError
5. 提取文本非空？ → EmptyPDFError
```

## 验证结果

### ✅ 正常解析
```
$ resume-cli parse examples/resume.pdf
→ 输出 JSON（含 file/pages/file_size/text_length/content 字段）
```

### ✅ 纯文本模式
```
$ resume-cli parse examples/resume.pdf --raw
→ 输出纯文本内容
```

### ✅ 保存到文件
```
$ resume-cli parse examples/resume.pdf --output result.json
→ ✅ 解析结果已保存到: result.json
```

### ✅ 文件不存在
```
$ resume-cli parse nonexistent.pdf
→ ❌ 错误: 文件不存在: nonexistent.pdf
```

### ✅ 文件不是 PDF
```
$ resume-cli parse examples/jd.txt
→ ❌ 错误: 文件不是 PDF 格式（扩展名不是 .pdf）: examples/jd.txt
```

### ✅ 伪装 PDF 检测
```
$ echo "fake" > /tmp/fake.pdf && resume-cli parse /tmp/fake.pdf
→ ❌ 错误: 文件头不是 PDF 格式（期望 '%PDF-'，实际: b'this '）
```

## 关键设计决策

1. **核心逻辑与 CLI 解耦**：`pdf_parser.py` 可被 extract/score 命令复用
2. **多层校验**：扩展名检查 + 文件头魔数检查，双重防御
3. **日志输出到 stderr**：不污染 stdout 的结构化输出
4. **JSON 输出格式**：包含文件元信息 + 文本内容，方便后续管道处理

## 下一步

→ Step 3: 实现 extract 命令（AI 结构化信息提取）
