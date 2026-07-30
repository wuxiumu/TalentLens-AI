"""
CLI 集成测试

测试 CLI 命令的基本行为（使用 mock 模式）。
"""

import os
import sys
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI_PATH = os.path.join(PROJECT_ROOT, "resume-cli")
EXAMPLES_DIR = os.path.join(PROJECT_ROOT, "examples")


def run_cli(*args):
    """运行 CLI 命令并返回结果"""
    cmd = [CLI_PATH] + list(args)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    return result


class TestCLIHelp:
    """CLI --help 测试"""

    def test_main_help(self):
        """测试主帮助"""
        r = run_cli("--help")
        assert r.returncode == 0
        assert "parse" in r.stdout
        assert "extract" in r.stdout
        assert "score" in r.stdout

    def test_version(self):
        """测试版本号"""
        r = run_cli("--version")
        assert r.returncode == 0
        assert "resume-cli v" in r.stdout

    def test_parse_help(self):
        """测试 parse --help"""
        r = run_cli("parse", "--help")
        assert r.returncode == 0
        assert "pdf_path" in r.stdout.lower() or "PDF_PATH" in r.stdout

    def test_extract_help(self):
        """测试 extract --help"""
        r = run_cli("extract", "--help")
        assert r.returncode == 0

    def test_score_help(self):
        """测试 score --help"""
        r = run_cli("score", "--help")
        assert r.returncode == 0
        assert "--jd" in r.stdout


class TestParseCommand:
    """parse 命令集成测试"""

    def test_parse_valid_pdf(self):
        """测试解析正常 PDF"""
        r = run_cli("parse", os.path.join(EXAMPLES_DIR, "resume.pdf"))
        assert r.returncode == 0
        assert "张三" in r.stdout

    def test_parse_file_not_found(self):
        """测试文件不存在"""
        r = run_cli("parse", "nonexistent.pdf")
        assert r.returncode != 0
        assert "错误" in r.stderr or "不存在" in r.stderr

    def test_parse_not_pdf(self):
        """测试非 PDF 文件"""
        r = run_cli("parse", os.path.join(EXAMPLES_DIR, "jd.txt"))
        assert r.returncode != 0

    def test_parse_raw_mode(self):
        """测试 --raw 模式"""
        r = run_cli("parse", os.path.join(EXAMPLES_DIR, "resume.pdf"), "--raw")
        assert r.returncode == 0
        assert "张三" in r.stdout
        # raw 模式不应该有 JSON 格式
        assert '"file"' not in r.stdout


class TestExtractCommand:
    """extract 命令集成测试"""

    def test_extract_mock(self):
        """测试 Mock 模式"""
        r = run_cli("extract", os.path.join(EXAMPLES_DIR, "resume.pdf"), "--mock")
        assert r.returncode == 0
        assert "张三" in r.stdout
        assert "Python" in r.stdout

    def test_extract_file_not_found(self):
        """测试文件不存在"""
        r = run_cli("extract", "nonexistent.pdf", "--mock")
        assert r.returncode != 0

    def test_extract_no_api_key(self):
        """测试未配置 API Key（不用 mock）"""
        env = os.environ.copy()
        env.pop("OPENAI_API_KEY", None)
        r = subprocess.run(
            [sys.executable, CLI_PATH, "extract", os.path.join(EXAMPLES_DIR, "resume.pdf")],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            env=env,
        )
        assert r.returncode != 0


class TestScoreCommand:
    """score 命令集成测试"""

    def test_score_mock(self):
        """测试 Mock 模式"""
        r = run_cli(
            "score",
            os.path.join(EXAMPLES_DIR, "resume.pdf"),
            "--jd", os.path.join(EXAMPLES_DIR, "jd.txt"),
            "--mock",
        )
        assert r.returncode == 0
        assert "overall_score" in r.stdout
        assert "interview_questions" in r.stdout

    def test_score_missing_jd(self):
        """测试缺少 --jd 参数"""
        r = run_cli("score", os.path.join(EXAMPLES_DIR, "resume.pdf"))
        assert r.returncode != 0

    def test_score_jd_not_found(self):
        """测试 JD 文件不存在"""
        r = run_cli(
            "score",
            os.path.join(EXAMPLES_DIR, "resume.pdf"),
            "--jd", "nonexistent_jd.txt",
            "--mock",
        )
        assert r.returncode != 0
