# Step 3: extract 命令实现

**日期**: 2026-07-30
**状态**: ✅ 完成

## 目标

实现 `resume-cli extract <pdf_path>` 命令，调用 AI 模型从简历中提取结构化信息（JSON 格式）。

## 实现内容

### 1. AI 客户端模块：`resume_cli/core/ai_client.py`

| 函数 | 功能 |
|------|------|
| `call_ai(system, user)` | 调用 AI，返回文本 |
| `call_ai_json(system, user)` | 调用 AI，返回解析后的 JSON dict |
| `_parse_json_response(text)` | 从 AI 响应中解析 JSON |
| `_repair_json(text)` | 修复常见 JSON 格式错误 |

### 2. JSON 解析容错策略

```
1. 直接 json.loads() 解析
2. 提取 markdown 代码块 ```json ... ``` 中的 JSON
3. 提取第一个 { 到最后一个 } 之间的内容
4. 修复常见问题后重试（末尾逗号、单引号、注释行）
```

### 3. Prompt 设计：`resume_cli/core/prompts.py`

**extract 提取 Prompt 要点**：
- 严格 JSON Schema 约束
- 字段名、类型明确定义
- 缺失字段填空字符串/空数组，不猜测
- 要求只输出 JSON，不要附加文字

### 4. 数据校验：Pydantic `ResumeData`

AI 返回结果通过 Pydantic 模型校验，确保：
- 所有字段类型正确
- education 是数组，每项包含 school/major/degree/graduation_time
- skills 是字符串数组

### 5. Mock 模式

提供 `MOCK_EXTRACT_RESULT` 预设数据，无需 API Key 即可演示完整流程。

## 新增文件

| 文件 | 说明 |
|------|------|
| `core/ai_client.py` | OpenAI API 客户端 + JSON 解析 + 错误处理 |
| `core/prompts.py` | Prompt 模板 + Mock 数据 |
| `commands/extract.py` | extract 命令实现 |

## 验证结果

### ✅ Mock 模式正常输出
```
$ resume-cli extract examples/resume.pdf --mock
→ 输出完整 JSON（姓名、电话、邮箱、教育经历、技能列表）
```

### ✅ --output 保存正常
```
$ resume-cli extract examples/resume.pdf --mock --output result.json
→ ✅ 提取结果已保存到: result.json
```

### ✅ 文件不存在错误处理
```
$ resume-cli extract nonexistent.pdf --mock
→ ❌ PDF 处理错误: 文件不存在: nonexistent.pdf
```

### ✅ 未配置 API Key 时的友好提示
```
$ resume-cli extract examples/resume.pdf
→ ❌ 配置错误: 未配置 OPENAI_API_KEY 环境变量。
```

### ✅ 日志输出到 stderr（不污染 stdout JSON）
```
$ resume-cli extract examples/resume.pdf --mock 2>/dev/null
→ 输出纯 JSON，无日志行
```

## 关键设计决策

1. **AI 客户端与命令解耦**：`ai_client.py` 可被 extract/score 复用
2. **多层 JSON 解析容错**：应对 AI 常见的格式问题
3. **Prompt 集中管理**：便于调优和维护
4. **Pydantic 二次校验**：即使 AI 返回格式正确，也做类型安全检查
5. **Mock 模式优先**：让面试官无需配置 API Key 就能看到效果

## 下一步

→ Step 4: 实现 score 命令（JD 匹配评分）
