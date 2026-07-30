"""
AI 客户端模块单元测试

主要测试 JSON 解析和修复逻辑（不需要实际 API 调用）。
"""

import os
import pytest
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from resume_cli.core.ai_client import _parse_json_response, _repair_json, AIResponseError


class TestParseJSONResponse:
    """_parse_json_response 函数测试"""

    def test_pure_json(self):
        """测试纯 JSON 字符串"""
        result = _parse_json_response('{"name": "张三", "age": 25}')
        assert result == {"name": "张三", "age": 25}

    def test_json_in_code_block(self):
        """测试 markdown 代码块中的 JSON"""
        text = """这是一些说明文字。
```json
{"name": "李四", "skills": ["Python", "Go"]}
```
以上是结果。"""
        result = _parse_json_response(text)
        assert result["name"] == "李四"
        assert "Python" in result["skills"]

    def test_json_without_language_tag(self):
        """测试无语言标记的代码块"""
        text = """```
{"city": "北京"}
```"""
        result = _parse_json_response(text)
        assert result["city"] == "北京"

    def test_json_with_surrounding_text(self):
        """测试前后有文字的 JSON"""
        text = """好的，以下是提取结果：
{"email": "test@example.com"}
希望对你有帮助！"""
        result = _parse_json_response(text)
        assert result["email"] == "test@example.com"

    def test_invalid_json_raises_error(self):
        """测试完全无效的 JSON 抛出异常"""
        with pytest.raises(AIResponseError, match="无法.*解析"):
            _parse_json_response("this is not json at all")

    def test_trailing_comma(self):
        """测试末尾逗号修复"""
        text = '{"name": "王五", "skills": ["Python", "Go",]}'
        result = _parse_json_response(text)
        assert result["name"] == "王五"
        assert len(result["skills"]) == 2

    def test_nested_json(self):
        """测试嵌套 JSON"""
        text = """
```json
{
  "name": "赵六",
  "education": [
    {"school": "北大", "degree": "硕士"},
    {"school": "清华", "degree": "学士"}
  ]
}
```"""
        result = _parse_json_response(text)
        assert len(result["education"]) == 2
        assert result["education"][0]["school"] == "北大"


class TestRepairJSON:
    """_repair_json 函数测试"""

    def test_trailing_comma_fix(self):
        """测试末尾逗号修复"""
        result = _repair_json('{"a": 1, "b": 2,}')
        assert result is not None
        assert result["a"] == 1
        assert result["b"] == 2

    def test_single_quotes_fix(self):
        """测试单引号修复"""
        result = _repair_json("{'name': 'test'}")
        assert result is not None
        assert result["name"] == "test"

    def test_comment_removal(self):
        """测试注释移除"""
        text = """{
  // 这是注释
  "name": "test"
}"""
        result = _repair_json(text)
        assert result is not None
        assert result["name"] == "test"

    def test_unrepairable_returns_none(self):
        """测试无法修复的情况返回 None"""
        result = _repair_json("not json at all")
        assert result is None
