"""
配置管理模块

通过环境变量加载配置，支持 .env 文件自动加载。

配置优先级: 环境变量 > .env 文件 > 默认值
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# .env.example 中的占位符，复制后未替换时不能当成可用密钥
_PLACEHOLDER_API_KEYS = frozenset({
    "sk-your-api-key-here",
})


def _load_dotenv(env_path: Optional[str] = None) -> None:
    """
    从 .env 文件加载环境变量（不覆盖已存在的环境变量）

    支持格式:
    - KEY=VALUE
    - export KEY=VALUE
    - KEY="VALUE" / KEY='VALUE'（引号内的 # 会保留）
    - KEY=VALUE  # 行尾注释
    - # 注释行
    - 空行

    Args:
        env_path: .env 文件路径，默认查找项目根目录下的 .env
    """
    if env_path is None:
        # 查找项目根目录（从当前文件向上找到 resume_cli 包的父目录）
        project_root = Path(__file__).resolve().parent.parent
        env_path = str(project_root / ".env")

    if not os.path.isfile(env_path):
        return

    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # 跳过空行和注释
                if not line or line.startswith("#"):
                    continue
                # 解析 KEY=VALUE，也接受 shell 里常见的 `export KEY=VALUE`
                if "=" not in line:
                    continue
                key, _, raw_value = line.partition("=")
                key = key.strip()
                if key.startswith("export "):
                    key = key[len("export "):].strip()
                value = _parse_env_value(raw_value)
                # 不覆盖已存在的环境变量
                if key and key not in os.environ:
                    os.environ[key] = value
    except Exception:
        # .env 加载失败不影响程序运行
        pass


def _parse_env_value(raw: str) -> str:
    """
    解析 .env 的值。

    支持引号，以及 README 示例里的行尾注释（`VALUE  # 说明`）。
    引号内的 # 会保留。
    """
    value = raw.strip()
    if not value:
        return value

    if value[0] in ('"', "'"):
        quote = value[0]
        end = value.find(quote, 1)
        if end != -1:
            return value[1:end]

    comment_at = value.find(" #")
    if comment_at != -1:
        value = value[:comment_at].rstrip()
    return value


def _is_placeholder_api_key(api_key: Optional[str]) -> bool:
    """模板里的占位符不算已配置。"""
    key = (api_key or "").strip()
    return key.lower() in _PLACEHOLDER_API_KEYS


# 模块导入时自动加载 .env
_load_dotenv()


@dataclass
class Settings:
    """应用配置"""

    # AI 模型配置
    openai_api_key: Optional[str] = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    # 日志级别
    log_level: str = "INFO"

    # 超时设置（秒）
    request_timeout: int = 60

    def __post_init__(self):
        """从环境变量加载配置"""
        if self.openai_api_key is None:
            self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.openai_base_url = os.environ.get("OPENAI_BASE_URL", self.openai_base_url)
        self.openai_model = os.environ.get("OPENAI_MODEL", self.openai_model)
        self.log_level = os.environ.get("LOG_LEVEL", self.log_level)
        timeout_str = os.environ.get("REQUEST_TIMEOUT")
        if timeout_str:
            self.request_timeout = int(timeout_str)

    @property
    def has_api_key(self) -> bool:
        """是否配置了可用的 API Key（空值和模板占位符视为未配置）"""
        key = (self.openai_api_key or "").strip()
        return bool(key) and not _is_placeholder_api_key(key)


# 全局配置单例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """获取全局配置（懒加载单例）"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """重置配置（用于测试）"""
    global _settings
    _settings = None
