from pydantic import BaseModel, Field
from typing import List, Optional


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5000)
    limit: int = Field(default=5, ge=1, le=20)


class ProjectData(BaseModel):
    id: str = Field(..., max_length=100)
    type: str = Field(..., max_length=50)
    title: str = Field(..., min_length=1, max_length=200)
    date_range: Optional[str] = Field(default=None, max_length=100)
    skills: List[str] = Field(default=[], max_length=30)
    industry: List[str] = Field(default=[], max_length=10)
    tags: List[str] = Field(default=[], max_length=20)
    content: str = Field(..., min_length=1, max_length=10000)


class GenerateRequest(BaseModel):
    job_description: str = Field(..., min_length=10, max_length=5000)
    num_bullets: int = Field(default=3, ge=1, le=10)
    experience_ids: List[str] = Field(default=[], max_length=20)


class LinkedInParseRequest(BaseModel):
    experiences_text: Optional[str] = Field(default=None, max_length=15000)
    projects_text: Optional[str] = Field(default=None, max_length=15000)
    volunteering_text: Optional[str] = Field(default=None, max_length=15000)


class BatchExperienceRequest(BaseModel):
    experiences: List[ProjectData] = Field(..., max_length=25)
