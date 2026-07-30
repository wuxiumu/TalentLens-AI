"""
extract 命令 - 调用 AI 模型提取简历结构化信息

用法:
    resume-cli extract <pdf_path>
    resume-cli extract <pdf_path> --mock
    resume-cli extract <pdf_path> --output result.json
"""

import json
from typing import Optional

import typer

from resume_cli.core.pdf_parser import extract_text_from_pdf, PDFError
from resume_cli.core.ai_client import call_ai_json, AIError, AIConfigError
from resume_cli.core.prompts import (
    EXTRACT_SYSTEM_PROMPT,
    EXTRACT_USER_PROMPT,
    MOCK_EXTRACT_RESULT,
)
from resume_cli.models.schemas import ResumeData
from resume_cli.utils.logger import get_logger

logger = get_logger(__name__)


def extract_info(
    pdf_path: str = typer.Argument(help="PDF 简历文件路径"),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="将结果保存到文件"
    ),
    mock: bool = typer.Option(
        False, "--mock", help="使用模拟数据（无需 API Key）"
    ),
):
    """
    调用 AI 模型从简历中提取结构化信息。

    提取字段包括: 姓名、电话、邮箱、城市、教育经历、技能列表。

    示例:
        resume-cli extract ./resume.pdf
        resume-cli extract ./resume.pdf --mock
        resume-cli extract ./resume.pdf --output result.json
    """
    try:
        # Step 1: 解析 PDF 文本
        logger.info(f"正在解析 PDF: {pdf_path}")
        resume_text = extract_text_from_pdf(pdf_path)
        logger.info(f"PDF 解析完成，文本长度: {len(resume_text)} 字符")

        # Step 2: 调用 AI 提取信息
        if mock:
            logger.info("使用 Mock 模式，跳过 AI 调用")
            result_data = MOCK_EXTRACT_RESULT.copy()
        else:
            logger.info("正在调用 AI 模型提取信息...")
            user_prompt = EXTRACT_USER_PROMPT.format(resume_text=resume_text)
            result_data = call_ai_json(EXTRACT_SYSTEM_PROMPT, user_prompt)
            logger.info("AI 信息提取完成")

        # Step 3: 使用 Pydantic 校验结果
        try:
            validated = ResumeData(**result_data)
            result_dict = validated.model_dump()
        except Exception as e:
            logger.warning(f"Pydantic 校验失败，使用原始数据: {e}")
            result_dict = result_data

        # Step 4: 输出结果
        output_text = json.dumps(result_dict, ensure_ascii=False, indent=2)

        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(output_text)
            typer.echo(f"✅ 提取结果已保存到: {output}")
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
    except Exception as e:
        logger.exception(f"未知错误: {e}")
        typer.echo(f"❌ 未知错误: {e}", err=True)
        raise typer.Exit(code=1)
