"""
配置加载测试

覆盖 .env 行尾注释、export 前缀，以及模板占位符不当成已配置。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from resume_cli.config import (  # noqa: E402
    _load_dotenv,
    _parse_env_value,
    get_settings,
    reset_settings,
)


ENV_KEYS = (
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "OPENAI_MODEL",
    "LOG_LEVEL",
    "REQUEST_TIMEOUT",
)


def _clear_env(monkeypatch):
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    reset_settings()


class TestParseEnvValue:
    """单行值解析"""

    def test_inline_comment(self):
        assert _parse_env_value("sk-live-key          # 必填：API Key") == "sk-live-key"

    def test_quoted_value_keeps_hash(self):
        assert _parse_env_value('"sk-abc#def" # 注释') == "sk-abc#def"

    def test_single_quotes(self):
        assert _parse_env_value("'gpt-4o-mini'") == "gpt-4o-mini"


class TestLoadDotenv:
    """从文件加载"""

    def test_readme_style_file(self, tmp_path, monkeypatch):
        """README 环境变量示例（行尾注释）可以原样放进 .env"""
        _clear_env(monkeypatch)
        env_file = tmp_path / ".env"
        env_file.write_text(
            "\n".join([
                "OPENAI_API_KEY=sk-live-key          # 必填：API Key",
                "OPENAI_BASE_URL=https://example.invalid/v1    # 可选：API 地址",
                "OPENAI_MODEL=gpt-4o-mini                     # 可选：模型名称",
                "LOG_LEVEL=DEBUG                               # 可选：日志级别",
                "REQUEST_TIMEOUT=60                           # 可选：超时秒数",
            ]),
            encoding="utf-8",
        )

        _load_dotenv(str(env_file))
        reset_settings()
        settings = get_settings()

        assert settings.openai_api_key == "sk-live-key"
        assert settings.openai_base_url == "https://example.invalid/v1"
        assert settings.openai_model == "gpt-4o-mini"
        assert settings.log_level == "DEBUG"
        assert settings.request_timeout == 60
        assert settings.has_api_key is True
        reset_settings()

    def test_export_prefix(self, tmp_path, monkeypatch):
        _clear_env(monkeypatch)
        env_file = tmp_path / ".env"
        env_file.write_text("export OPENAI_API_KEY=sk-from-export\n", encoding="utf-8")

        _load_dotenv(str(env_file))
        assert os.environ["OPENAI_API_KEY"] == "sk-from-export"
        reset_settings()

    def test_does_not_override_existing_env(self, tmp_path, monkeypatch):
        _clear_env(monkeypatch)
        monkeypatch.setenv("OPENAI_API_KEY", "from-environment")
        env_file = tmp_path / ".env"
        env_file.write_text("OPENAI_API_KEY=from-file\n", encoding="utf-8")

        _load_dotenv(str(env_file))
        assert os.environ["OPENAI_API_KEY"] == "from-environment"
        reset_settings()


class TestApiKeyPresence:
    """密钥是否算已配置"""

    def test_placeholder_is_not_configured(self, monkeypatch):
        _clear_env(monkeypatch)
        monkeypatch.setenv("OPENAI_API_KEY", "sk-your-api-key-here")
        reset_settings()
        assert get_settings().has_api_key is False
        reset_settings()

    def test_blank_is_not_configured(self, monkeypatch):
        _clear_env(monkeypatch)
        monkeypatch.setenv("OPENAI_API_KEY", "   ")
        reset_settings()
        assert get_settings().has_api_key is False
        reset_settings()

    def test_real_key_is_configured(self, monkeypatch):
        _clear_env(monkeypatch)
        monkeypatch.setenv("OPENAI_API_KEY", "sk-live-key")
        reset_settings()
        assert get_settings().has_api_key is True
        reset_settings()
