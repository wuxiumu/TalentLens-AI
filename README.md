# Resume CLI - AI 简历解析命令行工具

一个基于 AI 的简历解析与岗位匹配评分 CLI 工具，支持 PDF 简历解析、结构化信息提取、JD 匹配评分。

## 📖 项目简介

在招聘流程中，快速理解候选人简历并判断其与岗位的匹配程度是一项常见但耗时的工作。Resume CLI 通过命令行工具的形式，让 recruiter 和 HR 可以快速：

- **解析 PDF 简历**：提取文本内容
- **AI 结构化提取**：自动识别姓名、联系方式、教育经历、技能等关键信息
- **JD 匹配评分**：基于简历和岗位描述，给出多维度评分和面试建议

## 🛠 技术选型

| 组件 | 技术 | 说明 |
|------|------|------|
| 编程语言 | Python 3.9+ | 全栈语言，生态丰富 |
| CLI 框架 | [Typer](https://typer.tiangolo.com/) | 基于类型提示的现代 CLI 框架 |
| PDF 解析 | [PyMuPDF](https://pymupdf.readthedocs.io/) | 高性能 PDF 文本提取 |
| 数据校验 | [Pydantic v2](https://docs.pydantic.dev/) | AI 返回 JSON 的结构化校验 |
| AI 调用 | [OpenAI SDK](https://github.com/openai/openai-python) | 兼容 OpenAI 及所有兼容接口 |
| 测试 | [pytest](https://pytest.org/) | 单元测试 + 集成测试 |
| 容器化 | Docker | 一键运行环境 |

## 🔧 环境变量配置

通过环境变量配置 AI 模型，支持 `.env` 文件自动加载：

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env，填入你的配置
vi .env
```

`.env` 内容示例：
```bash
OPENAI_API_KEY=sk-your-api-key-here          # 必填：API Key
OPENAI_BASE_URL=https://api.openai.com/v1    # 可选：API 地址
OPENAI_MODEL=gpt-4o-mini                     # 可选：模型名称
LOG_LEVEL=INFO                               # 可选：日志级别
REQUEST_TIMEOUT=60                           # 可选：超时秒数
```

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `OPENAI_API_KEY` | ✅ | - | API 密钥 |
| `OPENAI_BASE_URL` | ❌ | `https://api.openai.com/v1` | API 基础地址（支持 DeepSeek、通义等兼容接口） |
| `OPENAI_MODEL` | ❌ | `gpt-4o-mini` | 模型名称 |
| `LOG_LEVEL` | ❌ | `INFO` | 日志级别（DEBUG/INFO/WARNING/ERROR） |
| `REQUEST_TIMEOUT` | ❌ | `60` | 请求超时（秒） |

> 💡 没有 API Key？使用 `--mock` 模式即可体验全部功能！

验证配置：
```bash
python3 -c "
from resume_cli.config import get_settings
s = get_settings()
print('API Key:', '✅ 已配置' if s.has_api_key else '❌ 未配置')
print('Model:', s.openai_model)
"
```

## 📦 安装方式

### 方式一：本地安装

```bash
# 1. 克隆项目
git clone git@github.com:wuxiumu/TalentLens-AI.git
cd TalentLens-AI

# 2. 安装依赖
pip install -r requirements.txt

# 3. 验证安装
./resume-cli --version
```

### 方式二：Docker

```bash
# 构建镜像
docker build -t resume-cli .

# 运行
docker run --rm resume-cli --help
```

### 方式三：Makefile

```bash
make install    # 安装依赖
make help       # 查看所有命令
```

---

## 🔍 操作验证流程

安装完成后，按以下流程验证全部功能。详细文档见 [`doc/操作验证流程.md`](doc/操作验证流程.md)。

### 快速验证（3 步）

```bash
# Step 1: 验证安装
./resume-cli --version
# 期望: resume-cli v0.1.0

# Step 2: 验证 PDF 解析
./resume-cli parse examples/resume.pdf
# 期望: 输出 JSON（含 file/pages/content 字段）

# Step 3: 验证 AI 提取（Mock 模式，无需 API Key）
./resume-cli extract examples/resume.pdf --mock
# 期望: 输出结构化 JSON（name/phone/education/skills）
```

### 完整验证（需 API Key）

```bash
# 1. 验证配置
python3 -c "from resume_cli.config import get_settings; print('API Key:', '✅' if get_settings().has_api_key else '❌')"

# 2. parse 命令
./resume-cli parse examples/resume.pdf
# 期望: JSON 输出，包含 "content": "张三\n电话: 138-0013-8000\n..."

# 3. extract 命令（真实 AI 调用）
./resume-cli extract examples/resume.pdf
# 期望: AI 返回准确的结构化 JSON
# {
#   "name": "张三",
#   "phone": "138-0013-8000",
#   "email": "zhangsan@example.com",
#   "education": [...],
#   "skills": ["Python", "Go", ...]
# }

# 4. score 命令（真实 AI 调用）
./resume-cli score examples/resume.pdf --jd examples/jd.txt
# 期望: 输出评分 JSON
# {
#   "overall_score": 90,
#   "skill_score": 95,
#   "experience_score": 85,
#   "education_score": 90,
#   "comment": "候选人在全栈开发和 AI 方向的技能非常强...",
#   "interview_questions": [...]
# }
```

### 错误处理验证

| 测试场景 | 命令 | 期望结果 |
|---------|------|---------|
| 文件不存在 | `./resume-cli parse nonexistent.pdf` | ❌ 错误: 文件不存在 |
| 非 PDF 文件 | `./resume-cli parse examples/jd.txt` | ❌ 错误: 不是 PDF 格式 |
| JD 文件不存在 | `./resume-cli score examples/resume.pdf --jd no.txt` | ❌ JD 文件错误: 文件不存在 |
| 未配置 API Key | 清空 .env 后执行 extract | ❌ 提示配置 OPENAI_API_KEY |
| Mock 模式 | `./resume-cli extract examples/resume.pdf --mock` | ✅ 正常输出预设数据 |

### 一键演示

```bash
make demo-all    # 依次执行 parse → extract(mock) → score(mock)
```

### 测试套件

```bash
make test        # 运行 48 个测试用例
```

期望结果：`48 passed in ~5 minutes`

| 测试文件 | 用例数 | 覆盖模块 |
|---------|--------|---------|
| `test_pdf_parser.py` | 9 | PDF 解析 + 错误处理 |
| `test_jd_parser.py` | 6 | JD 文件读取 |
| `test_ai_client.py` | 11 | JSON 解析 + 修复 |
| `test_schemas.py` | 7 | Pydantic 数据模型 |
| `test_cli.py` | 15 | CLI 集成测试 |

### 验证清单

逐项确认：

- [ ] `./resume-cli --version` 显示版本号
- [ ] `./resume-cli --help` 显示三个子命令
- [ ] `./resume-cli parse examples/resume.pdf` 输出 JSON
- [ ] `./resume-cli parse nonexistent.pdf` 提示文件不存在
- [ ] `./resume-cli extract examples/resume.pdf --mock` 输出结构化 JSON
- [ ] `./resume-cli extract examples/resume.pdf` 调用 AI 并返回准确结果
- [ ] `./resume-cli score examples/resume.pdf --jd examples/jd.txt --mock` 输出评分
- [ ] `./resume-cli score examples/resume.pdf --jd examples/jd.txt` 真实 AI 评分
- [ ] `--output` 选项可保存结果到文件
- [ ] `make demo-all` 一键演示全部命令
- [ ] `make test` 全部测试通过
- [ ] 日志输出到 stderr（不污染 JSON stdout）

## 📋 CLI 命令说明

### 1. `parse` - 解析 PDF 简历

```bash
resume-cli parse <pdf_path> [--output <file>] [--raw]
```

| 参数 | 说明 |
|------|------|
| `pdf_path` | PDF 简历文件路径（必填） |
| `--output, -o` | 将结果保存到文件 |
| `--raw` | 只输出纯文本（不带 JSON 包装） |

**示例：**
```bash
resume-cli parse ./resume.pdf
resume-cli parse ./resume.pdf --output parsed.json
resume-cli parse ./resume.pdf --raw
```

### 2. `extract` - AI 结构化信息提取

```bash
resume-cli extract <pdf_path> [--output <file>] [--mock]
```

| 参数 | 说明 |
|------|------|
| `pdf_path` | PDF 简历文件路径（必填） |
| `--output, -o` | 将结果保存到文件 |
| `--mock` | 使用模拟数据（无需 API Key） |

**示例：**
```bash
resume-cli extract ./resume.pdf --mock
resume-cli extract ./resume.pdf --output result.json
```

### 3. `score` - JD 匹配评分

```bash
resume-cli score <pdf_path> --jd <jd_path> [--output <file>] [--mock]
```

| 参数 | 说明 |
|------|------|
| `pdf_path` | PDF 简历文件路径（必填） |
| `--jd` | JD 岗位描述文件路径（必填） |
| `--output, -o` | 将结果保存到文件 |
| `--mock` | 使用模拟数据（无需 API Key） |

**示例：**
```bash
resume-cli score ./resume.pdf --jd ./jd.txt
resume-cli score ./resume.pdf --jd ./jd.txt --mock --output score.json
```

## 📝 示例输入和输出

### parse 命令

**输入：** `examples/resume.pdf`（张三的简历）

**输出：**
```json
{
  "file": "examples/resume.pdf",
  "pages": 1,
  "file_size": "2.4 KB",
  "text_length": 814,
  "content": "张三\n电话: 138-0013-8000\n..."
}
```

### extract 命令

**输出：**
```json
{
  "name": "张三",
  "phone": "138-0013-8000",
  "email": "zhangsan@example.com",
  "city": "北京",
  "education": [
    {
      "school": "北京大学",
      "major": "计算机科学与技术",
      "degree": "硕士",
      "graduation_time": "2023年6月"
    }
  ],
  "skills": ["Python", "Go", "JavaScript", "TypeScript", "React", ...]
}
```

### score 命令

**输出：**
```json
{
  "overall_score": 82,
  "skill_score": 88,
  "experience_score": 80,
  "education_score": 75,
  "comment": "候选人具备较好的全栈开发基础...",
  "interview_questions": [
    "请介绍一个你主导过的全栈项目。",
    "你是否有调用大模型 API 的实际经验？"
  ]
}
```

## ✅ 已实现功能

### 核心功能
- [x] `parse` 命令 — PDF 文本提取
- [x] `extract` 命令 — AI 结构化信息提取
- [x] `score` 命令 — JD 匹配评分
- [x] `--help` 自动帮助文档
- [x] 文件不存在/非 PDF/空 PDF 等错误处理

### 加分项
- [x] `--output` 保存结果到文件
- [x] `--mock` 模式（无需 API Key 即可演示）
- [x] JSON 格式错误自动修复（末尾逗号、单引号、markdown 代码块等）
- [x] 日志输出（stderr，不污染 stdout）
- [x] Dockerfile
- [x] Makefile
- [x] 单元测试 + 集成测试

## 📁 项目结构

```
TalentLens-AI/
├── resume-cli              # CLI 入口脚本
├── requirements.txt        # Python 依赖
├── Makefile                # 常用命令
├── Dockerfile              # Docker 配置
├── .env.example            # 环境变量模板
├── resume_cli/             # 主包
│   ├── __init__.py         # 版本号
│   ├── main.py             # Typer 主应用
│   ├── config.py           # 配置管理
│   ├── commands/           # CLI 命令层
│   │   ├── parse.py        #   parse 命令
│   │   ├── extract.py      #   extract 命令
│   │   └── score.py        #   score 命令
│   ├── core/               # 核心业务逻辑
│   │   ├── pdf_parser.py   #   PDF 解析
│   │   ├── ai_client.py    #   AI 调用 + JSON 解析
│   │   ├── jd_parser.py    #   JD 文件读取
│   │   └── prompts.py      #   Prompt 模板 + Mock 数据
│   ├── models/             # 数据模型
│   │   └── schemas.py      #   Pydantic 模型
│   └── utils/              # 工具
│       └── logger.py       #   日志配置
├── tests/                  # 测试
│   ├── test_pdf_parser.py
│   ├── test_jd_parser.py
│   ├── test_ai_client.py
│   ├── test_schemas.py
│   └── test_cli.py
├── examples/               # 示例文件
│   ├── resume.pdf
│   └── jd.txt
└── doc/                    # 开发文档
    ├── 操作验证流程.md        # 完整验证指南
    ├── step1-项目骨架搭建.md
    ├── step2-parse命令实现.md
    ├── step3-extract命令实现.md
    ├── step4-score命令实现.md
    └── step5-加分项功能.md
```

## 🧪 测试

```bash
# 运行全部测试
make test

# 或直接运行
python -m pytest tests/ -v
```

## 🐳 Docker

```bash
# 构建
make docker-build

# 运行（Mock 模式）
docker run --rm resume-cli extract /app/examples/resume.pdf --mock
```

## ⚠️ 已知问题或未完成内容

1. **AI 模型需真实 API Key**：除 `--mock` 模式外，需配置真实 API Key 才能获得实际结果
2. **扫描件 PDF 不支持**：仅支持文本型 PDF，不支持纯图片扫描件（需要 OCR）
3. **Prompt 可进一步优化**：当前 Prompt 已可用，但针对不同格式的简历可进一步调优
4. **暂不支持批量处理**：每次只能处理一份简历

## 📄 License

本项目为笔试题作品，仅供招聘评估使用。
