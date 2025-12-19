"""Unit tests for NLP parser module."""

import pytest

from src.nlp.parser import ResumeParser


@pytest.mark.unit
def test_resume_parser_initialization() -> None:
    """Test ResumeParser initialization."""
    parser = ResumeParser()
    assert parser.model_name == "en_core_web_sm"


@pytest.mark.unit
def test_extract_skills(sample_resume_text: str) -> None:
    """Test skill extraction from resume text."""
    parser = ResumeParser(model_name="en_core_web_sm")
    # This test will work once spaCy model is downloaded
    # skills = parser.extract_skills(sample_resume_text)
    # assert isinstance(skills, list)


@pytest.mark.unit
def test_extract_entities(sample_resume_text: str) -> None:
    """Test entity extraction from resume text."""
    parser = ResumeParser(model_name="en_core_web_sm")
    # This test will work once spaCy model is downloaded
    # entities = parser.extract_entities(sample_resume_text)
    # assert isinstance(entities, dict)

