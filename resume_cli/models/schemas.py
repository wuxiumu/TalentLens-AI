"""
数据模型模块

使用 Pydantic 定义义 AI 提取和评分结果的结构化数据模型。
"""

from typing import Optional
from pydantic import BaseModel, Field


class Education(BaseModel):
    """教育经历"""
    school: str = Field(default="", description="学校名称")
    major: str = Field(default="", description="专业")
    degree: str = Field(default="", description="学历")
    graduation_time: str = Field(default="", description="毕业时间")


class ResumeData(BaseModel):
    """简历结构化数据"""
    name: str = Field(default="", description="姓名")
    phone: str = Field(default="", description="电话")
    email: str = Field(default="", description="邮箱")
    city: str = Field(default="", description="所在城市")
    education: list[Education] = Field(default_factory=list, description="教育经历")
    skills: list[str] = Field(default_factory=list, description="技能列表")


class ScoreResult(BaseModel):
    """JD 匹配评分结果"""
    overall_score: int = Field(ge=0, le=100, description="综合评分")
    skill_score: int = Field(ge=0, le=100, description="技能匹配评分")
    experience_score: int = Field(ge=0, le=100, description="经验匹配评分")
    education_score: int = Field(ge=0, le=100, description="教育背景评分")
    comment: str = Field(default="", description="综合评语")
    interview_questions: list[str] = Field(
        default_factory=list,
        description="建议面试问题"
    )
