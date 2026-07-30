"""
JD 文件处理模块单元测试
"""

import os
import pytest
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from resume_cli.core.jd_parser import (
    read_jd_file,
    JDFileNotFoundError,
    JDEmptyError,
    JDError,
)

EXAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")


class TestReadJDFile:
    """read_jd_file 函数测试"""

    def test_valid_jd(self):
        """测试正常 JD 文件读取"""
        jd_path = os.path.join(EXAMPLES_DIR, "jd.txt")
        content = read_jd_file(jd_path)
        assert isinstance(content, str)
        assert len(content) > 0
        assert "全栈" in content

    def test_file_not_found(self):
        """测试 JD 文件不存在"""
        with pytest.raises(JDFileNotFoundError, match="文件不存在"):
            read_jd_file("/nonexistent/path/jd.txt")

    def test_empty_jd(self, tmp_path):
        """测试空 JD 文件"""
        empty_jd = tmp_path / "empty_jd.txt"
        empty_jd.write_text("")
        with pytest.raises(JDEmptyError, match="内容为空"):
            read_jd_file(str(empty_jd))

    def test_whitespace_only_jd(self, tmp_path):
        """测试只有空白字符的 JD 文件"""
        ws_jd = tmp_path / "ws_jd.txt"
        ws_jd.write_text("   \n\n   \t  \n")
        with pytest.raises(JDEmptyError, match="内容为空"):
            read_jd_file(str(ws_jd))

    def test_directory_path(self):
        """测试路径为目录"""
        with pytest.raises(JDError, match="不是文件"):
            read_jd_file(EXAMPLES_DIR)

    def test_utf8_content(self, tmp_path):
        """测试 UTF-8 编码内容"""
        utf8_jd = tmp_path / "utf8_jd.txt"
        utf8_jd.write_text("Python 开发工程师\n要求：3年经验", encoding="utf-8")
        content = read_jd_file(str(utf8_jd))
        assert "Python" in content
        assert "3年" in content
