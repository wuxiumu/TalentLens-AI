# Step 1: 项目骨架搭建

**日期**: 2026-07-30
**状态**: ✅ 完成

## 目标

搭建项目基础结构，确保 CLI 框架可启动、三个子命令注册正确。

## 技术选型

| 组件 | 选择 | 理由 |
|------|------|------|
| CLI 框架 | Typer | 基于类型提示，自动生成 --help，代码简洁 |
| PDF 解析 | PyMuPDF (fitz) | 速度快、文本提取质量高、社区活跃 |
| 数据模型 | Pydantic v2 | AI 返回 JSON 校验、类型安全 |
| AI 调用 | openai SDK | 兼容 OpenAI API 及所有兼容接口 |
| 终端美化 | rich | JSON 高亮输出（可选，不影响核心功能） |
| Python 版本 | 3.9+ | 系统自带，兼容性好 |

## 项目目录结构

```
TalentLens-AI/
├── resume-cli              # CLI 入口脚本（可执行）
├── requirements.txt        # 依赖清单
├── resume_cli/             # 主包
│   ├── __init__.py         # 版本号
│   ├── main.py             # Typer 主应用，注册命令
│   ├── config.py           # 配置管理（环境变量）
│   ├── commands/           # CLI 命令层
│   │   ├── parse.py        # parse 命令
│   │   ├── extract.py      # extract 命令
│   │   └── score.py        # score 命令
│   ├── core/               # 核心业务逻辑
│   ├── models/             # 数据模型
│   │   └── schemas.py      # Pydantic 模型定义
│   └── utils/              # 工具模块
│       └── logger.py       # 日志配置
├── tests/                  # 测试
├── examples/               # 示例文件
└── doc/                    # 开发文档
```

## 配置管理设计

通过环境变量加载配置，无需额外文件：

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `OPENAI_API_KEY` | - | AI 模型 API Key |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | API 基础地址 |
| `OPENAI_MODEL` | `gpt-4o-mini` | 使用的模型名 |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `REQUEST_TIMEOUT` | `60` | API 请求超时（秒） |

## 验证结果

```
$ ./resume-cli --help
# ✅ 显示三个子命令: parse / extract / score

$ ./resume-cli --version
# ✅ resume-cli v0.1.0

$ ./resume-cli parse --help
# ✅ 显示 PDF_PATH 参数

$ ./resume-cli score --help
# ✅ 显示 PDF_PATH + --jd 选项

$ ./resume-cli parse ./test.pdf
# ✅ [parse] PDF 路径: ./test.pdf

$ ./resume-cli score ./test.pdf --jd ./jd.txt
# ✅ [score] resume=./test.pdf, jd=./jd.txt
```

## 关键设计决策

1. **命令注册方式**: 使用 `app.command()` 直接注册函数，而非嵌套 `add_typer()`，避免命令路径多一层嵌套
2. **Shebang**: 使用 `/usr/bin/python3`（非 env），因为项目依赖安装在系统 Python 3.9 下
3. **日志输出到 stderr**: 避免污染 stdout 的 JSON 输出
4. **Pydantic 模型预定义**: 提前在 schemas.py 定义好 ResumeData 和 ScoreResult，后续 AI 调用可直接使用

## 下一步

→ Step 2: 实现 parse 命令（PDF 文本提取 + 错误处理）
