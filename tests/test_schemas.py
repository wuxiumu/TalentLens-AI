"""
数据模型单元测试
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from resume_cli.models.schemas import ResumeData, ScoreResult, Education


class TestResumeData:
    """ResumeData 模型测试"""

    def test_valid_data(self):
        """测试正常数据"""
        data = ResumeData(
            name="张三",
            phone="138-0000-0000",
            email="test@example.com",
            city="北京",
            education=[
                Education(school="北大", major="CS", degree="硕士", graduation_time="2023年6月")
            ],
            skills=["Python", "Go"],
        )
        assert data.name == "张三"
        assert len(data.education) == 1
        assert len(data.skills) == 2

    def test_empty_data(self):
        """测试空数据（全部默认值）"""
        data = ResumeData()
        assert data.name == ""
        assert data.phone == ""
        assert data.education == []
        assert data.skills == []

    def test_from_dict(self):
        """测试从字典创建"""
        raw = {
            "name": "李四",
            "phone": "139-0000-0000",
            "email": "lisi@test.com",
            "city": "上海",
            "education": [],
            "skills": ["JavaScript"],
        }
        data = ResumeData(**raw)
        assert data.name == "李四"
        assert data.skills == ["JavaScript"]

    def test_model_dump(self):
        """测试序列化"""
        data = ResumeData(name="王五", skills=["Python"])
        dumped = data.model_dump()
        assert isinstance(dumped, dict)
        assert dumped["name"] == "王五"


class TestScoreResult:
    """ScoreResult 模型测试"""

    def test_valid_scores(self):
        """测试正常评分"""
        result = ScoreResult(
            overall_score=82,
            skill_score=88,
            experience_score=80,
            education_score=75,
            comment="候选人表现良好",
            interview_questions=["问题1", "问题2"],
        )
        assert result.overall_score == 82
        assert len(result.interview_questions) == 2

    def test_boundary_scores(self):
        """测试边界分数"""
        # 最低分
        result_min = ScoreResult(
            overall_score=0, skill_score=0, experience_score=0, education_score=0
        )
        assert result_min.overall_score == 0

        # 最高分
        result_max = ScoreResult(
            overall_score=100, skill_score=100, experience_score=100, education_score=100
        )
        assert result_max.overall_score == 100

    def test_score_out_of_range(self):
        """测试超范围分数"""
        with pytest.raises(Exception):
            ScoreResult(overall_score=101, skill_score=0, experience_score=0, education_score=0)

        with pytest.raises(Exception):
            ScoreResult(overall_score=-1, skill_score=0, experience_score=0, education_score=0)
