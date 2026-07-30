# Step 7: 真实 AI 调用验证

**日期**: 2026-07-30
**状态**: ✅ 完成

## 目标

配置真实 API Key 后，验证三个命令的完整 AI 调用流程。

## 配置变更

新增 `.env` 文件自动加载功能（`config.py`）：
- 自动查找项目根目录的 `.env` 文件
- 优先级：环境变量 > .env 文件 > 默认值
- 不覆盖已存在的环境变量
- 支持注释、引号、空行

## 测试结果

### ✅ extract 命令（真实 AI 调用）

```
$ resume-cli extract examples/resume.pdf
耗时: ~10 秒
结果: 完整准确的 JSON
```

**AI 提取结果**：
- `name`: 张三 ✅
- `phone`: 138-0013-8000 ✅
- `email`: zhangsan@example.com ✅
- `city`: 北京 ✅
- `education`: 2 条记录（北大硕士 + 清华学士）✅
- `skills`: 16 项技能（Python, Go, JS, TS, React, Vue, PostgreSQL, MySQL, Redis, Docker, Kubernetes, CI/CD, RESTful API 设计, GraphQL, 大模型 API 调用, 全栈开发）✅

### ✅ score 命令（真实 AI 调用）

```
$ resume-cli score examples/resume.pdf --jd examples/jd.txt
耗时: ~7 秒
结果: 合理评分 + 针对性评语 + 高质量面试问题
```

**AI 评分结果**：
| 维度 | 分数 | 评价 |
|------|------|------|
| overall | 90 | 非常匹配 |
| skill | 95 | 技能非常强 |
| experience | 85 | 经验略少但相关度高 |
| education | 90 | 教育背景优秀 |

**评语**：
> 候选人在全栈开发和 AI 方向的技能非常强，尤其是在 Python 和 Go 的应用上表现突出。虽然工作经验略少，但其在字节跳动的项目经历与岗位要求高度契合。

**面试问题**（AI 生成）：
1. 请详细描述您在字节跳动负责的 AI 辅助编程平台的开发过程。
2. 您如何优化系统架构以提升用户体验和系统稳定性？
3. 在与大模型算法团队协作时，您通常如何沟通和协调工作？
4. 请分享您在项目中使用 OpenAI API 的具体案例和遇到的挑战。
5. 您对容器化部署（Docker/Kubernetes）的理解和实践经验是什么？

### ✅ parse 命令

无需 AI，行为与之前一致。

### ✅ --output 保存功能

```
$ resume-cli score examples/resume.pdf --jd examples/jd.txt --output result.json
→ ✅ 评分结果已保存到: result.json
```

## 回归测试

| 测试集 | 结果 |
|--------|------|
| 单元测试（33 个） | ✅ 全部通过 |
| CLI 集成测试（14 个） | ✅ 全部通过 |
| 跳过（1 个） | `test_extract_no_api_key`（已有 API Key） |

## 性能观察

| 操作 | 耗时 | 说明 |
|------|------|------|
| PDF 解析 | < 0.1s | PyMuPDF 极快 |
| extract AI 调用 | ~10s | gpt-4o-mini，含网络延迟 |
| score AI 调用 | ~7s | gpt-4o-mini，含网络延迟 |

## 质量评估

### Prompt 效果

- **extract**: 100% 字段准确率，无遗漏无幻觉
- **score**: 评分合理（与简历质量匹配），评语针对性强，面试问题有深度

### 对比 Mock 数据

| 项目 | Mock 数据 | 真实 AI |
|------|-----------|---------|
| overall_score | 82 | 90 |
| skill_score | 88 | 95 |
| 评语质量 | 良好 | 更具体（提到 Python/Go/字节项目） |
| 面试问题 | 5 个 | 5 个（更具针对性） |

真实 AI 的评分更精准，评语和面试问题更贴合简历内容。

## 结论

✅ 全部功能在真实 AI 调用下工作正常
✅ 输出质量达到生产可用水平
✅ 项目已可提交
