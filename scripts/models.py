"""Pydantic models describing the CV data schema.

These are the single source of truth for validation (used by validate.py).
The JSON Schemas under schemas/ are generated from these models and are used
only for editor autocompletion (YAML language server), not for validation.
"""
from __future__ import annotations

import datetime as dt
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class Profile(BaseModel):
    slug: str
    full_name: str
    headline: Optional[str] = None
    default_template: str = "moderncv"
    variants: list[str] = Field(default_factory=lambda: ["default"])


class PersonalInfo(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    summary: Optional[str] = None


class EducationItem(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: dt.date
    end_date: Optional[dt.date] = None
    description: Optional[str] = None


class ExperienceItem(BaseModel):
    company: str
    role: str
    start_date: dt.date
    end_date: Optional[dt.date] = None
    location: Optional[str] = None
    highlights: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class SkillCategory(BaseModel):
    category: str
    items: list[str] = Field(default_factory=list)


class Project(BaseModel):
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    tags: list[str] = Field(default_factory=list)


class Publication(BaseModel):
    title: str
    venue: Optional[str] = None
    year: Optional[int] = None
    url: Optional[str] = None


class Certification(BaseModel):
    name: str
    issuer: Optional[str] = None
    date: Optional[dt.date] = None
    url: Optional[str] = None


class Variant(BaseModel):
    name: str
    template: Optional[str] = None
    title: Optional[str] = None
    include_sections: list[str] = Field(
        default_factory=lambda: [
            "personal",
            "education",
            "experience",
            "skills",
            "projects",
            "publications",
            "certifications",
        ]
    )
    tags_filter: list[str] = Field(default_factory=list)
