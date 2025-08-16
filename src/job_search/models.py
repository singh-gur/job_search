#!/usr/bin/env python
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class Project(BaseModel):
    """Model for project entry"""

    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")
    technologies: List[str] = Field(
        default_factory=list, description="Technologies used"
    )


class Experience(BaseModel):
    """Model for work experience entry"""

    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    duration: str = Field(..., description="Employment duration (e.g., '2021-2024')")
    description: str = Field(..., description="Job description and achievements")
    projects: List[Project] = Field(
        default_factory=list, description="List of projects worked on"
    )


class Education(BaseModel):
    """Model for education entry"""

    degree: str = Field(..., description="Degree title")
    school: str = Field(..., description="Educational institution name")
    year: str = Field(..., description="Graduation year or year range")


class UserProfile(BaseModel):
    """Model for user profile containing all personal and professional information"""

    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="Current location")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    skills: List[str] = Field(
        default_factory=list, description="List of technical skills"
    )
    experience: List[Experience] = Field(
        default_factory=list, description="Work experience history"
    )
    education: List[Education] = Field(
        default_factory=list, description="Educational background"
    )
    certifications: List[str] = Field(
        default_factory=list, description="Professional certifications"
    )
    summary: Optional[str] = Field(None, description="Professional summary")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Jane Smith",
                "email": "jane.smith@email.com",
                "phone": "+1-555-0123",
                "location": "San Francisco, CA",
                "linkedin": "linkedin.com/in/janesmith",
                "skills": ["Python", "React", "Node.js", "AWS", "Docker"],
                "experience": [
                    {
                        "title": "Senior Full Stack Developer",
                        "company": "Tech Innovations Inc",
                        "duration": "2021-2024",
                        "description": "Led development of scalable web applications",
                        "projects": [
                            {
                                "name": "E-commerce Platform",
                                "description": "Built scalable e-commerce platform with React and Node.js",
                                "technologies": [
                                    "React",
                                    "Node.js",
                                    "PostgreSQL",
                                    "AWS",
                                ],
                            },
                            {
                                "name": "Real-time Analytics Dashboard",
                                "description": "Developed real-time data visualization dashboard",
                                "technologies": [
                                    "React",
                                    "D3.js",
                                    "WebSocket",
                                    "Redis",
                                ],
                            },
                        ],
                    }
                ],
                "education": [
                    {
                        "degree": "Bachelor of Science in Computer Science",
                        "school": "Stanford University",
                        "year": "2019",
                    }
                ],
                "certifications": ["AWS Certified Solutions Architect"],
                "summary": "Experienced full-stack developer with 5+ years experience",
            }
        }


class JobSearchParams(BaseModel):
    """Model for job search parameters"""

    search_term: str = Field(
        default="Software Developer", description="Job title or search term"
    )
    location: str = Field(default="Remote", description="Job location")
    results_wanted: int = Field(
        default=10, ge=1, le=100, description="Number of job results to retrieve"
    )
    fine_tune_search_string: Optional[str] = Field(
        None,
        description="Additional search criteria for LLM-based fine-tuning of results",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "search_term": "Senior Full Stack Developer",
                "location": "San Francisco",
                "results_wanted": 15,
                "fine_tune_search_string": "startups with good work-life balance and remote-first culture",
            }
        }


class JobSearchConfig(BaseModel):
    """Complete configuration for job search including user profile and search parameters"""

    user_profile: UserProfile
    job_search_params: JobSearchParams

    class Config:
        json_schema_extra = {
            "example": {
                "user_profile": {
                    "name": "Jane Smith",
                    "email": "jane.smith@email.com",
                    "skills": ["Python", "React"],
                    "experience": [],
                    "education": [],
                },
                "job_search_params": {
                    "search_term": "Software Developer",
                    "location": "Remote",
                    "results_wanted": 10,
                },
            }
        }
