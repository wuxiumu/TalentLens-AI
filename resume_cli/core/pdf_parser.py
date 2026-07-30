"""
PDF 文件处理核心模块

使用 PyMuPDF (fitz) 提取 PDF 文本，提供完善的错误处理。
"""

import os
from typing import Optional

import fitz  # PyMuPDF

from resume_cli.utils.logger import get_logger

logger = get_logger(__name__)


class PDFError(Exception):
    """PDF 处理相关错误的基类"""
    pass


class FileNotFoundError_(PDFError):
    """文件不存在"""
    pass


class NotPDFError(PDFError):
    """文件不是 PDF 格式"""
    pass


class PDFReadError(PDFError):
    """PDF 无法读取"""
    pass


class EmptyPDFError(PDFError):
    """PDF 文本为空"""
    pass


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    从 PDF 文件中提取全部文本内容

    Args:
        pdf_path: PDF 文件路径

    Returns:
        提取的文本内容

    Raises:
        FileNotFoundError_: 文件不存在
        NotPDFError: 文件不是 PDF
        PDFReadError: PDF 无法读取
        EmptyPDFError: PDF 文本为空
    """
    logger.debug(f"开始处理文件: {pdf_path}")

    # 1. 检查文件是否存在
    if not os.path.exists(pdf_path):
        raise FileNotFoundError_(f"文件不存在: {pdf_path}")

    if not os.path.isfile(pdf_path):
        raise FileNotFoundError_(f"路径不是文件: {pdf_path}")

    # 2. 检查文件扩展名
    if not pdf_path.lower().endswith(".pdf"):
        raise NotPDFError(f"文件不是 PDF 格式（扩展名不是 .pdf）: {pdf_path}")

    # 3. 检查文件是否可读且确实是 PDF
    try:
        with open(pdf_path, "rb") as f:
            header = f.read(5)
            if header != b"%PDF-":
                raise NotPDFError(
                    f"文件头不是 PDF 格式（期望 '%PDF-'，实际: {header!r}）: {pdf_path}"
                )
    except PermissionError:
        raise PDFReadError(f"文件无读取权限: {pdf_path}")
    except IsADirectoryError:
        raise NotPDFError(f"路径是一个目录，不是文件: {pdf_path}")

    # 4. 使用 PyMuPDF 打开并提取文本
    doc = None
    try:
        doc = fitz.open(pdf_path)
        logger.debug(f"PDF 打开成功，共 {doc.page_count} 页")

        all_text = []
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text = page.get_text()
            if text:
                all_text.append(text)

        full_text = "\n".join(all_text).strip()

        # 5. 检查文本是否为空
        if not full_text:
            raise EmptyPDFError(
                f"PDF 文本为空，无法提取内容: {pdf_path}（可能是扫描件或图片 PDF）"
            )

        logger.debug(f"文本提取完成，共 {len(full_text)} 字符")
        return full_text

    except fitz.FileDataError as e:
        raise PDFReadError(f"PDF 文件损坏或无法读取: {pdf_path}（{e}）")
    except Exception as e:
        if isinstance(e, PDFError):
            raise
        raise PDFReadError(f"读取 PDF 时发生未知错误: {pdf_path}（{e}）")
    finally:
        if doc:
            doc.close()


def get_pdf_info(pdf_path: str) -> dict:
    """
    获取 PDF 文件的元信息

    Args:
        pdf_path: PDF 文件路径

    Returns:
        包含页数、文件大小等信息的字典
    """
    doc = fitz.open(pdf_path)
    try:
        file_size = os.path.getsize(pdf_path)
        return {
            "page_count": doc.page_count,
            "file_size_bytes": file_size,
            "file_size_human": _human_readable_size(file_size),
            "metadata": dict(doc.metadata) if doc.metadata else {},
        }
    finally:
        doc.close()


def _human_readable_size(size_bytes: int) -> str:
    """将字节数转为人类可读格式"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
