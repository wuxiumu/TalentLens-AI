"""
配置管理模块

通过环境变量加载配置，支持 .env 文件自动加载。

配置优先级: 环境变量 > .env 文件 > 默认值
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


def _load_dotenv(env_path: Optional[str] = None) -> None:
    """
    从 .env 文件加载环境变量（不覆盖已存在的环境变量）

    支持格式:
    - KEY=VALUE
    - KEY="VALUE"
    - KEY='VALUE'
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
                # 解析 KEY=VALUE
                if "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                # 移除引号
                if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                    value = value[1:-1]
                # 不覆盖已存在的环境变量
                if key and key not in os.environ:
                    os.environ[key] = value
    except Exception:
        # .env 加载失败不影响程序运行
        pass


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
        """是否配置了 API Key"""
        return bool(self.openai_api_key and self.openai_api_key.strip())


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
