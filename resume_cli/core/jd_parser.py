"""
JD 文件处理模块

读取岗位描述（JD）文本文件，提供错误处理。
"""

import os
from resume_cli.utils.logger import get_logger

logger = get_logger(__name__)


class JDError(Exception):
    """JD 处理相关错误基类"""
    pass


class JDFileNotFoundError(JDError):
    """JD 文件不存在"""
    pass


class JDEmptyError(JDError):
    """JD 文件为空"""
    pass


def read_jd_file(jd_path: str) -> str:
    """
    读取 JD 文件内容

    Args:
        jd_path: JD 文件路径

    Returns:
        JD 文本内容

    Raises:
        JDFileNotFoundError: 文件不存在
        JDEmptyError: 文件内容为空
        JDError: 其他读取错误
    """
    logger.debug(f"读取 JD 文件: {jd_path}")

    if not os.path.exists(jd_path):
        raise JDFileNotFoundError(f"JD 文件不存在: {jd_path}")

    if not os.path.isfile(jd_path):
        raise JDError(f"JD 路径不是文件: {jd_path}")

    try:
        with open(jd_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except UnicodeDecodeError:
        # 尝试其他编码
        try:
            with open(jd_path, "r", encoding="gbk") as f:
                content = f.read().strip()
        except Exception as e:
            raise JDError(f"JD 文件编码无法识别: {jd_path}（{e}）")
    except PermissionError:
        raise JDError(f"JD 文件无读取权限: {jd_path}")
    except Exception as e:
        raise JDError(f"读取 JD 文件时出错: {jd_path}（{e}）")

    if not content:
        raise JDEmptyError(f"JD 文件内容为空: {jd_path}")

    logger.debug(f"JD 文件读取成功，长度: {len(content)} 字符")
    return content
