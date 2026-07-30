# Step 5: 加分项功能

**日期**: 2026-07-30
**状态**: ✅ 完成

## 加分项清单

| 加分项 | 状态 | 实现位置 |
|--------|------|----------|
| `--output result.json` 保存结果 | ✅ | parse / extract / score 均支持 |
| `--mock` 模式 | ✅ | extract / score 支持 |
| JSON 格式错误自动修复 | ✅ | `core/ai_client.py` → `_repair_json()` |
| 简单日志输出 | ✅ | `utils/logger.py` |
| Dockerfile | ✅ | `Dockerfile` |
| Makefile | ✅ | `Makefile` |

## 新增文件

| 文件 | 说明 |
|------|------|
| `Dockerfile` | Docker 镜像构建文件（python:3.12-slim 基础镜像） |
| `.dockerignore` | Docker 构建忽略文件 |
| `.gitignore` | Git 忽略规则 |
| `.env.example` | 环境变量配置模板 |
| `Makefile` | 常用命令快捷入口 |

## Makefile 命令一览

```bash
make help           # 显示所有可用命令
make install        # 安装依赖
make demo-parse     # 演示 parse 命令
make demo-extract   # 演示 extract 命令（Mock）
make demo-score     # 演示 score 命令（Mock）
make demo-all       # 演示全部命令
make test           # 运行测试
make lint           # 语法检查
make docker-build   # 构建 Docker 镜像
make clean          # 清理临时文件
make gen-test-files # 生成测试文件
```

## Docker 使用方式

```bash
# 构建镜像
docker build -t resume-cli .

# 运行 parse
docker run --rm -v $(pwd)/examples:/app/examples resume-cli parse /app/examples/resume.pdf

# 运行 extract（Mock）
docker run --rm -v $(pwd)/examples:/app/examples resume-cli extract /app/examples/resume.pdf --mock

# 运行 score（Mock）
docker run --rm -v $(pwd)/examples:/app/examples resume-cli score /app/examples/resume.pdf --jd /app/examples/jd.txt --mock
```

## JSON 自动修复能力

`_repair_json()` 函数可处理以下常见问题：

1. **末尾多余逗号**: `{"a": 1,}` → `{"a": 1}`
2. **单引号**: `{'a': 1}` → `{"a": 1}`
3. **注释行**: 自动移除 `// comment`
4. **markdown 代码块**: 自动提取 ```json ... ``` 中的内容
5. **前后多余文字**: 自动定位 `{...}` JSON 部分

## 验证结果

```bash
$ make demo-all
# ✅ 三个命令全部成功执行

$ make lint
# ✅ 语法检查通过
```

## 下一步

→ Step 6: 测试与 README 文档
