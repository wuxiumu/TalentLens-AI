"""
PDF 解析模块单元测试
"""

import os
import pytest
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from resume_cli.core.pdf_parser import (
    extract_text_from_pdf,
    get_pdf_info,
    FileNotFoundError_,
    NotPDFError,
    PDFReadError,
    EmptyPDFError,
)

# 测试文件路径
EXAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")
TEST_PDF = os.path.join(EXAMPLES_DIR, "resume.pdf")


class TestExtractTextFromPDF:
    """extract_text_from_pdf 函数测试"""

    def test_valid_pdf(self):
        """测试正常 PDF 文件解析"""
        text = extract_text_from_pdf(TEST_PDF)
        assert isinstance(text, str)
        assert len(text) > 0
        assert "张三" in text
        assert "Python" in text

    def test_file_not_found(self):
        """测试文件不存在"""
        with pytest.raises(FileNotFoundError_, match="文件不存在"):
            extract_text_from_pdf("/nonexistent/path/resume.pdf")

    def test_not_pdf_extension(self):
        """测试非 PDF 扩展名"""
        jd_file = os.path.join(EXAMPLES_DIR, "jd.txt")
        if os.path.exists(jd_file):
            with pytest.raises(NotPDFError, match="不是 PDF 格式"):
                extract_text_from_pdf(jd_file)

    def test_fake_pdf(self, tmp_path):
        """测试伪装 PDF（扩展名 .pdf 但内容不是 PDF）"""
        fake_pdf = tmp_path / "fake.pdf"
        fake_pdf.write_text("this is not a pdf content")
        with pytest.raises(NotPDFError, match="文件头不是 PDF 格式"):
            extract_text_from_pdf(str(fake_pdf))

    def test_corrupted_pdf(self, tmp_path):
        """测试损坏的 PDF 文件"""
        corrupted = tmp_path / "corrupted.pdf"
        corrupted.write_bytes(b"%PDF-1.4\ncorrupted content here")
        with pytest.raises((PDFReadError, EmptyPDFError)):
            extract_text_from_pdf(str(corrupted))

    def test_empty_pdf(self, tmp_path):
        """测试空白 PDF（只有空白页，无文本）"""
        import fitz
        empty_pdf = tmp_path / "empty.pdf"
        doc = fitz.open()
        doc.new_page()  # 空白页
        doc.save(str(empty_pdf))
        doc.close()
        with pytest.raises(EmptyPDFError, match="文本为空"):
            extract_text_from_pdf(str(empty_pdf))

    def test_directory_path(self):
        """测试路径为目录"""
        with pytest.raises((FileNotFoundError_, NotPDFError)):
            extract_text_from_pdf(EXAMPLES_DIR)


class TestGetPdfInfo:
    """get_pdf_info 函数测试"""

    def test_valid_pdf_info(self):
        """测试获取正常 PDF 信息"""
        info = get_pdf_info(TEST_PDF)
        assert "page_count" in info
        assert "file_size_bytes" in info
        assert "file_size_human" in info
        assert info["page_count"] >= 1
        assert info["file_size_bytes"] > 0

    def test_human_readable_size(self):
        """测试文件大小格式化"""
        from resume_cli.core.pdf_parser import _human_readable_size
        assert _human_readable_size(500) == "500.0 B"
        assert "KB" in _human_readable_size(2048)
        assert "MB" in _human_readable_size(2 * 1024 * 1024)
