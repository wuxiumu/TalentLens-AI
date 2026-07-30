"""
生成测试用的 PDF 简历文件
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fitz  # PyMuPDF


def create_test_resume(output_path: str):
    """创建一个测试用的 PDF 简历"""
    doc = fitz.open()
    page = doc.new_page()

    # 文本内容
    text = """张三
电话: 138-0013-8000
邮箱: zhangsan@example.com
所在城市: 北京

教育经历
北京大学  计算机科学与技术  硕士  2023年6月
清华大学  软件工程  学士  2020年6月

专业技能
• Python（精通，5年开发经验）
• Go / Golang（熟练，2年开发经验）
• JavaScript / TypeScript / React / Vue
• PostgreSQL / MySQL / Redis
• Docker / Kubernetes / CI/CD
• RESTful API 设计 / GraphQL
• 大模型 API 调用（OpenAI / Claude API）
• 全栈开发（前后端均可独立交付）

工作经历
字节跳动 — 高级全栈工程师（2023.7 - 至今）
• 负责内部 AI 辅助编程平台的全栈开发，日活 5000+
• 后端使用 Go 实现微服务架构，前端使用 React + TypeScript
• 集成 OpenAI API 实现代码审查和自动补全功能
• 设计并实现基于 Redis 的会话缓存系统，QPS 提升 300%

阿里巴巴 — 前端工程师（2020.7 - 2023.6）
• 参与淘宝商家后台系统重构，使用 React + Ant Design
• 开发可视化数据看板，使用 ECharts 和 D3.js
• 推动前端工程化建设，引入 TypeScript 和单元测试

项目经历
AI 简历解析工具（个人项目）
• 使用 Python 实现 CLI 工具，支持 PDF 简历解析和 AI 信息提取
• 集成 OpenAI API 进行结构化信息提取和 JD 匹配评分

技术博客平台（个人项目）
• 基于 Next.js + MDX 的个人博客，支持暗色模式
• 部署在 Vercel，使用 ISR 实现增量静态生成
"""

    # 插入文本
    text_point = fitz.Point(50, 50)
    page.insert_textbox(
        fitz.Rect(50, 50, 545, 780),
        text,
        fontsize=10,
        fontname="china-s",  # 中文字体
        align=fitz.TEXT_ALIGN_LEFT,
    )

    doc.save(output_path)
    doc.close()
    print(f"✅ 测试简历已生成: {output_path}")


def create_test_jd(output_path: str):
    """创建一个测试用的 JD 文件"""
    content = """高级全栈工程师 - AI 方向

岗位职责：
1. 负责公司 AI 产品的前后端开发工作
2. 设计并实现高可用、高性能的 Web 应用
3. 与大模型算法团队协作，将 AI 能力集成到产品中
4. 优化系统架构，提升用户体验和系统稳定性

岗位要求：
1. 本科及以上学历，计算机相关专业优先
2. 3年以上全栈开发经验
3. 精通 Python 或 Go，熟悉至少一种前端框架（React/Vue）
4. 有大模型 API 调用经验者优先（OpenAI / Claude / 通义千问等）
5. 熟悉容器化部署（Docker / Kubernetes）
6. 良好的沟通能力，能独立完成技术方案设计和评审

加分项：
• 有 AI 产品开发经验
• 有开源项目贡献经验
• 熟悉 RAG、Agent 等大模型应用技术
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ 测试 JD 已生成: {output_path}")


if __name__ == "__main__":
    examples_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")
    os.makedirs(examples_dir, exist_ok=True)

    create_test_resume(os.path.join(examples_dir, "resume.pdf"))
    create_test_jd(os.path.join(examples_dir, "jd.txt"))
