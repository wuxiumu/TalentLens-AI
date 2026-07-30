# Step 4: score 命令实现

**日期**: 2026-07-30
**状态**: ✅ 完成

## 目标

实现 `resume-cli score <pdf_path> --jd <jd_path>` 命令，读取简历和 JD，调用 AI 进行匹配评分。

## 实现内容

### 1. JD 文件处理：`resume_cli/core/jd_parser.py`

| 函数 | 功能 |
|------|------|
| `read_jd_file(jd_path)` | 读取 JD 文本，支持 UTF-8/GBK 编码自动检测 |

自定义异常：
- `JDFileNotFoundError` — 文件不存在
- `JDEmptyError` — 文件为空
- `JDError` — 其他读取错误

### 2. score 命令流程

```
1. 解析 PDF 简历 → resume_text
2. 读取 JD 文件 → jd_text
3. 构建 Prompt（简历 + JD）→ 调用 AI
4. Pydantic ScoreResult 校验 → 输出 JSON
```

### 3. Prompt 设计（score）

- 四维度评分：overall / skill / experience / education（0-100）
- 评分标准明确定义（90-100 非常匹配 → 0-59 匹配度低）
- 输出评语 + 3-5 个面试建议问题
- 严格 JSON 格式约束

### 4. 新增文件

| 文件 | 说明 |
|------|------|
| `core/jd_parser.py` | JD 文件读取 + 错误处理 |
| `commands/score.py` | score 命令实现 |

## 验证结果

### ✅ Mock 模式正常评分
```
$ resume-cli score examples/resume.pdf --jd examples/jd.txt --mock
→ 输出完整 JSON（overall_score: 82, skill_score: 88, ...）
```

### ✅ JD 文件不存在
```
$ resume-cli score examples/resume.pdf --jd nonexistent.txt --mock
→ ❌ JD 文件错误: JD 文件不存在: nonexistent.txt
```

### ✅ PDF 文件不存在
```
$ resume-cli score nonexistent.pdf --jd examples/jd.txt --mock
→ ❌ PDF 处理错误: 文件不存在: nonexistent.pdf
```

### ✅ JD 文件为空
```
$ resume-cli score examples/resume.pdf --jd /tmp/empty_jd.txt --mock
→ ❌ JD 文件错误: JD 文件内容为空: /tmp/empty_jd.txt
```

### ✅ --output 保存
```
$ resume-cli score examples/resume.pdf --jd examples/jd.txt --mock --output score.json
→ ✅ 评分结果已保存到: score.json
```

## 关键设计决策

1. **JD 编码容错**：先尝试 UTF-8，失败后尝试 GBK，兼容 Windows 系统文件
2. **PDF 错误先于 JD 错误**：先解析简历再读 JD，符合用户预期顺序
3. **评分结果 Pydantic 校验**：确保所有分数在 0-100 范围内
4. **面试问题数量 3-5 个**：Prompt 中明确要求，保证输出质量

## 至此，三个核心命令全部实现完成

| 命令 | 状态 | 功能 |
|------|------|------|
| `parse` | ✅ | PDF 文本提取 + 4 种错误处理 |
| `extract` | ✅ | AI 结构化信息提取 + Mock 模式 |
| `score` | ✅ | JD 匹配评分 + Mock 模式 |

## 下一步

→ Step 5: 加分项功能（已完成部分：`--output`、`--mock`、JSON 修复、日志）
