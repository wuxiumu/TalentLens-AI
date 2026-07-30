"""
Prompt 模板模块

集中管理所有 AI 调用的 Prompt，便于维护和调优。
"""

# =====================================================================
# 简历信息提取 Prompt
# =====================================================================

EXTRACT_SYSTEM_PROMPT = """你是一个专业的简历信息提取助手。你的任务是从简历文本中提取结构化信息，并以严格的 JSON 格式返回。

## 输出要求

1. 必须返回合法的 JSON 对象
2. 不要添加任何解释、说明或额外文字
3. 只输出 JSON，不要使用 markdown 代码块包裹
4. 如果某个字段在简历中未提及，使用空字符串 "" 或空数组 []
5. 所有字段名必须与下方 Schema 完全一致

## JSON Schema

```json
{
  "name": "姓名",
  "phone": "电话",
  "email": "邮箱",
  "city": "所在城市",
  "education": [
    {
      "school": "学校名称",
      "major": "专业",
      "degree": "学历（如：学士/硕士/博士/大专）",
      "graduation_time": "毕业时间（如：2023年6月）"
    }
  ],
  "skills": ["技能1", "技能2", "技能3"]
}
```

## 注意事项

- education 是一个数组，包含所有教育经历（按时间倒序）
- skills 只列出技能关键词，不要包含描述性文字
- 如果信息缺失，对应字段填空字符串或空数组，不要猜测"""

EXTRACT_USER_PROMPT = """请从以下简历文本中提取结构化信息：

---
{resume_text}
---

请严格按照 JSON Schema 输出，不要包含任何其他文字。"""


# =====================================================================
# JD 匹配评分 Prompt
# =====================================================================

SCORE_SYSTEM_PROMPT = """你是一个专业的招聘匹配评估助手。你的任务是根据候选人简历和岗位描述（JD），对候选人进行多维度匹配评分。

## 评分维度

1. **overall_score**（综合评分）：0-100 分，综合所有维度的整体评价
2. **skill_score**（技能匹配）：0-100 分，候选人技能与 JD 要求的匹配程度
3. **experience_score**（经验匹配）：0-100 分，候选人的工作经验与 JD 要求的相关性
4. **education_score**（教育匹配）：0-100 分，候选人的学历背景与 JD 要求的匹配程度

## 评分标准

- 90-100：非常匹配，几乎完全符合岗位要求
- 80-89：较好匹配，大部分要求符合，有少量不足
- 70-79：基本匹配，核心要求满足，但有明显短板
- 60-69：部分匹配，有一定相关性但差距较大
- 0-59：匹配度低，与岗位要求相差较远

## 输出要求

1. 必须返回合法的 JSON 对象
2. 不要添加任何解释、说明或额外文字
3. 只输出 JSON，不要使用 markdown 代码块包裹
4. comment 字段用 1-3 句话总结候选人的优势和不足
5. interview_questions 提供 3-5 个针对性面试问题

## JSON Schema

```json
{
  "overall_score": 82,
  "skill_score": 88,
  "experience_score": 80,
  "education_score": 75,
  "comment": "候选人的综合评价...",
  "interview_questions": [
    "面试问题1",
    "面试问题2",
    "面试问题3"
  ]
}
```"""

SCORE_USER_PROMPT = """请根据以下候选人简历和岗位描述进行匹配评分：

## 候选人简历
---
{resume_text}
---

## 岗位描述（JD）
---
{jd_text}
---

请严格按照 JSON Schema 输出评分结果，不要包含任何其他文字。"""


# =====================================================================
# Mock 数据
# =====================================================================

MOCK_EXTRACT_RESULT = {
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
        },
        {
            "school": "清华大学",
            "major": "软件工程",
            "degree": "学士",
            "graduation_time": "2020年6月"
        }
    ],
    "skills": [
        "Python", "Go", "JavaScript", "TypeScript",
        "React", "Vue", "PostgreSQL", "MySQL", "Redis",
        "Docker", "Kubernetes", "CI/CD",
        "RESTful API", "GraphQL", "OpenAI API", "Claude API"
    ]
}

MOCK_SCORE_RESULT = {
    "overall_score": 82,
    "skill_score": 88,
    "experience_score": 80,
    "education_score": 75,
    "comment": "候选人具备较好的全栈开发基础，技能与岗位要求较匹配，有丰富的 Python 和 Go 开发经验。但缺少明确的大模型应用开发经验描述，建议面试时深入了解。",
    "interview_questions": [
        "请介绍一个你主导过的全栈项目，从技术选型到上线部署的完整流程。",
        "你是否有调用大模型 API（如 OpenAI / Claude）的实际经验？请举例说明。",
        "你在字节跳动做的 AI 辅助编程平台，是如何处理模型响应延迟和并发问题的？",
        "请描述一下你对 RAG（检索增强生成）的理解，以及在实际项目中的应用经验。",
        "你如何看待 AI Agent 的发展趋势？你认为 Asterfire Go 平台的 ADAM 智能体可以如何改进？"
    ]
}
