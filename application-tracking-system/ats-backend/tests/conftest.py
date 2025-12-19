"""Conftest file for pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_resume_text() -> str:
    """Provide sample resume text for testing."""
    return """
    John Doe
    Email: john@example.com
    Phone: 555-1234
    
    EXPERIENCE:
    Senior Software Engineer at TechCorp (2020-2023)
    - Developed Python backend systems using FastAPI
    - Implemented machine learning models with scikit-learn
    - Database design with PostgreSQL
    
    SKILLS:
    - Python, FastAPI, Django
    - Machine Learning, NLP, spaCy
    - PostgreSQL, SQLAlchemy
    - Docker, Kubernetes
    """


@pytest.fixture
def sample_job_description() -> str:
    """Provide sample job description for testing."""
    return """
    Senior Python Developer
    
    We are looking for a Senior Python Developer with:
    - 5+ years of Python experience
    - FastAPI framework expertise
    - Machine Learning knowledge
    - PostgreSQL database skills
    - Experience with spaCy NLP library
    
    Responsibilities:
    - Develop scalable backend systems
    - Implement NLP features
    - Optimize database queries
    """


@pytest.fixture
def sample_candidates() -> list[dict]:
    """Provide sample candidate data for testing."""
    return [
        {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "resume_text": "Python developer with FastAPI and ML experience",
        },
        {
            "id": 2,
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@example.com",
            "resume_text": "Frontend developer with React and JavaScript skills",
        },
    ]

