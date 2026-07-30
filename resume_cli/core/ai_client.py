"""
AI 客户端模块

封装 OpenAI API 调用，支持 JSON 响应解析和错误处理。
兼容 OpenAI API 及所有兼容接口（通过 OPENAI_BASE_URL 配置）。
"""

import json
from typing import Optional

from openai import OpenAI, APIError, APIConnectionError, RateLimitError, APITimeoutError

from resume_cli.config import get_settings
from resume_cli.utils.logger import get_logger

logger = get_logger(__name__)


class AIError(Exception):
    """AI 调用相关错误基类"""
    pass


class AIConfigError(AIError):
    """AI 配置错误（如缺少 API Key）"""
    pass


class AIResponseError(AIError):
    """AI 响应解析错误"""
    pass


def _get_client() -> OpenAI:
    """获取 OpenAI 客户端实例"""
    settings = get_settings()
    if not settings.has_api_key:
        raise AIConfigError(
            "未配置 OPENAI_API_KEY 环境变量。\n"
            "请设置: export OPENAI_API_KEY='your-api-key'\n"
            "或使用 --mock 模式进行演示（无需 API Key）"
        )
    return OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        timeout=settings.request_timeout,
    )


def call_ai(
    system_prompt: str,
    user_prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.1,
) -> str:
    """
    调用 AI 模型，返回文本响应

    Args:
        system_prompt: 系统提示词
        user_prompt: 用户提示词
        model: 模型名称（默认使用配置中的模型）
        temperature: 温度参数（0-1，越低越确定）

    Returns:
        AI 返回的文本内容

    Raises:
        AIConfigError: API Key 未配置
        AIError: API 调用失败
    """
    settings = get_settings()
    client = _get_client()
    use_model = model or settings.openai_model

    logger.debug(f"调用 AI 模型: {use_model}")
    logger.debug(f"System prompt: {system_prompt[:100]}...")
    logger.debug(f"User prompt length: {len(user_prompt)} chars")

    try:
        response = client.chat.completions.create(
            model=use_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )

        content = response.choices[0].message.content
        if not content:
            raise AIError("AI 返回内容为空")

        logger.debug(f"AI 响应长度: {len(content)} chars")
        logger.debug(f"Token 用量: {response.usage}")
        return content.strip()

    except AIConfigError:
        raise
    except APIConnectionError as e:
        raise AIError(f"无法连接 AI 服务，请检查网络或 OPENAI_BASE_URL 设置: {e}")
    except RateLimitError as e:
        raise AIError(f"AI 服务请求频率超限，请稍后重试: {e}")
    except APITimeoutError as e:
        raise AIError(f"AI 服务请求超时（{settings.request_timeout}s），请稍后重试: {e}")
    except APIError as e:
        raise AIError(f"AI 服务返回错误: {e}")
    except Exception as e:
        raise AIError(f"调用 AI 服务时发生未知错误: {e}")


def call_ai_json(
    system_prompt: str,
    user_prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.1,
) -> dict:
    """
    调用 AI 模型并解析 JSON 响应

    自动处理常见的 JSON 格式问题（markdown 代码块包裹等）。

    Args:
        system_prompt: 系统提示词
        user_prompt: 用户提示词
        model: 模型名称
        temperature: 温度参数

    Returns:
        解析后的 JSON 字典

    Raises:
        AIConfigError: API Key 未配置
        AIResponseError: JSON 解析失败
        AIError: API 调用失败
    """
    raw_text = call_ai(system_prompt, user_prompt, model, temperature)

    logger.debug(f"AI 原始响应:\n{raw_text[:500]}")

    # 尝试解析 JSON
    result = _parse_json_response(raw_text)
    return result


def _parse_json_response(text: str) -> dict:
    """
    从 AI 响应中解析 JSON

    支持以下格式:
    - 纯 JSON
    - Markdown 代码块包裹的 JSON: ```json ... ```
    - 前后有额外文本的 JSON

    Args:
        text: AI 返回的原始文本

    Returns:
        解析后的字典

    Raises:
        AIResponseError: 无法解析出有效 JSON
    """
    # 1. 直接尝试解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. 尝试提取 markdown 代码块中的 JSON
    import re
    code_block_pattern = re.compile(r'```(?:json)?\s*\n?(.*?)\n?\s*```', re.DOTALL)
    match = code_block_pattern.search(text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # 3. 尝试找到第一个 { 和最后一个 } 之间的内容
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        try:
            return json.loads(text[first_brace:last_brace + 1])
        except json.JSONDecodeError:
            pass

    # 4. 修复常见问题后重试
    repaired = _repair_json(text)
    if repaired:
        return repaired

    raise AIResponseError(
        f"无法从 AI 响应中解析出有效 JSON。\n"
        f"原始响应（前 300 字符）:\n{text[:300]}"
    )


def _repair_json(text: str) -> Optional[dict]:
    """
    尝试修复常见的 JSON 格式错误

    修复内容:
    - 末尾多余逗号: {"a": 1,} → {"a": 1}
    - 单引号 → 双引号
    - 缺少引号的键名
    - 注释行（// ...）

    Returns:
        修复后的字典，或 None（无法修复）
    """
    import re

    repaired = text

    # 提取 JSON 片段
    first_brace = repaired.find('{')
    last_brace = repaired.rfind('}')
    if first_brace != -1 and last_brace > first_brace:
        repaired = repaired[first_brace:last_brace + 1]

    # 移除注释行
    repaired = re.sub(r'//.*$', '', repaired, flags=re.MULTILINE)

    # 移除末尾逗号 (在 } 或 ] 前)
    repaired = re.sub(r',\s*([\]}])', r'\1', repaired)

    # 单引号替换为双引号（简单情况）
    repaired = repaired.replace("'", '"')

    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        return None
