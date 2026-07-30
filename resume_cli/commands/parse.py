"""
parse 命令 - 读取 PDF 简历并提取文本内容

用法:
    resume-cli parse <pdf_path>
    resume-cli parse <pdf_path> --output result.txt
"""

import json
import sys
from typing import Optional

import typer

from resume_cli.core.pdf_parser import (
    extract_text_from_pdf,
    get_pdf_info,
    PDFError,
    FileNotFoundError_,
    NotPDFError,
    PDFReadError,
    EmptyPDFError,
)
from resume_cli.utils.logger import get_logger

logger = get_logger(__name__)


def parse_pdf(
    pdf_path: str = typer.Argument(help="PDF 简历文件路径"),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="将结果保存到文件"
    ),
    raw: bool = typer.Option(False, "--raw", help="只输出纯文本，不显示额外信息"),
):
    """
    读取本地 PDF 简历并提取文本内容。

    示例:
        resume-cli parse ./resume.pdf
        resume-cli parse ./resume.pdf --output parsed.txt
    """
    try:
        # 提取文本
        text = extract_text_from_pdf(pdf_path)

        if raw:
            # 纯文本模式：直接输出，不加任何修饰
            if output:
                with open(output, "w", encoding="utf-8") as f:
                    f.write(text)
                typer.echo(f"✅ 文本已保存到: {output}")
            else:
                typer.echo(text)
            return

        # 默认模式：显示文件信息 + 文本内容
        info = get_pdf_info(pdf_path)

        result = {
            "file": pdf_path,
            "pages": info["page_count"],
            "file_size": info["file_size_human"],
            "text_length": len(text),
            "content": text,
        }

        output_text = json.dumps(result, ensure_ascii=False, indent=2)

        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(output_text)
            typer.echo(f"✅ 解析结果已保存到: {output}")
        else:
            typer.echo(output_text)

    except FileNotFoundError_ as e:
        typer.echo(f"❌ 错误: {e}", err=True)
        raise typer.Exit(code=1)
    except NotPDFError as e:
        typer.echo(f"❌ 错误: {e}", err=True)
        raise typer.Exit(code=1)
    except PDFReadError as e:
        typer.echo(f"❌ 错误: {e}", err=True)
        raise typer.Exit(code=1)
    except EmptyPDFError as e:
        typer.echo(f"❌ 错误: {e}", err=True)
        raise typer.Exit(code=1)
    except PDFError as e:
        typer.echo(f"❌ PDF 处理错误: {e}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        logger.exception(f"未知错误: {e}")
        typer.echo(f"❌ 未知错误: {e}", err=True)
        raise typer.Exit(code=1)
