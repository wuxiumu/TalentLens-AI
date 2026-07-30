"""
score 命令 - 简历与 JD 匹配评分

用法:
    resume-cli score <pdf_path> --jd <jd_path>
    resume-cli score <pdf_path> --jd <jd_path> --mock
    resume-cli score <pdf_path> --jd <jd_path> --output result.json
"""

import json
from typing import Optional

import typer

from resume_cli.core.pdf_parser import extract_text_from_pdf, PDFError
from resume_cli.core.jd_parser import read_jd_file, JDError
from resume_cli.core.ai_client import call_ai_json, AIError, AIConfigError
from resume_cli.core.prompts import (
    SCORE_SYSTEM_PROMPT,
    SCORE_USER_PROMPT,
    MOCK_SCORE_RESULT,
)
from resume_cli.models.schemas import ScoreResult
from resume_cli.utils.logger import get_logger

logger = get_logger(__name__)


def score_resume(
    pdf_path: str = typer.Argument(help="PDF 简历文件路径"),
    jd: str = typer.Option(..., "--jd", help="JD 岗位描述文件路径"),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="将结果保存到文件"
    ),
    mock: bool = typer.Option(
        False, "--mock", help="使用模拟数据（无需 API Key）"
    ),
):
    """
    输入一份简历和一份岗位描述文件，调用 AI 进行匹配评分。

    输出包含：综合评分、技能/经验/教育子维度评分、评语、面试建议问题。

    示例:
        resume-cli score ./resume.pdf --jd ./jd.txt
        resume-cli score ./resume.pdf --jd ./jd.txt --mock
        resume-cli score ./resume.pdf --jd ./jd.txt --output score.json
    """
    try:
        # Step 1: 解析 PDF 简历
        logger.info(f"正在解析简历: {pdf_path}")
        resume_text = extract_text_from_pdf(pdf_path)
        logger.info(f"简历解析完成，文本长度: {len(resume_text)} 字符")

        # Step 2: 读取 JD 文件
        logger.info(f"正在读取 JD 文件: {jd}")
        jd_text = read_jd_file(jd)
        logger.info(f"JD 读取完成，文本长度: {len(jd_text)} 字符")

        # Step 3: 调用 AI 评分
        if mock:
            logger.info("使用 Mock 模式，跳过 AI 调用")
            result_data = MOCK_SCORE_RESULT.copy()
        else:
            logger.info("正在调用 AI 模型进行匹配评分...")
            user_prompt = SCORE_USER_PROMPT.format(
                resume_text=resume_text,
                jd_text=jd_text,
            )
            result_data = call_ai_json(SCORE_SYSTEM_PROMPT, user_prompt)
            logger.info("AI 评分完成")

        # Step 4: Pydantic 校验
        try:
            validated = ScoreResult(**result_data)
            result_dict = validated.model_dump()
        except Exception as e:
            logger.warning(f"Pydantic 校验失败，使用原始数据: {e}")
            result_dict = result_data

        # Step 5: 输出结果
        output_text = json.dumps(result_dict, ensure_ascii=False, indent=2)

        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(output_text)
            typer.echo(f"✅ 评分结果已保存到: {output}")
        else:
            typer.echo(output_text)

    except AIConfigError as e:
        typer.echo(f"❌ 配置错误: {e}", err=True)
        raise typer.Exit(code=1)
    except AIError as e:
        typer.echo(f"❌ AI 调用失败: {e}", err=True)
        raise typer.Exit(code=1)
    except PDFError as e:
        typer.echo(f"❌ PDF 处理错误: {e}", err=True)
        raise typer.Exit(code=1)
    except JDError as e:
        typer.echo(f"❌ JD 文件错误: {e}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        logger.exception(f"未知错误: {e}")
        typer.echo(f"❌ 未知错误: {e}", err=True)
        raise typer.Exit(code=1)
