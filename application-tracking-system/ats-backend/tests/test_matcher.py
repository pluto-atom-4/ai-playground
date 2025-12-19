"""Unit tests for matching engine module."""

import pytest

from src.nlp.matcher import MatchingEngine


@pytest.mark.unit
def test_matching_engine_initialization() -> None:
    """Test MatchingEngine initialization."""
    engine = MatchingEngine()
    assert engine._vectorizer is None
    assert engine._tfidf_matrix is None


@pytest.mark.unit
def test_calculate_match_score(sample_resume_text: str, sample_job_description: str) -> None:
    """Test match score calculation."""
    engine = MatchingEngine()
    score = engine.calculate_match_score(sample_resume_text, sample_job_description)
    assert isinstance(score, float)
    assert 0 <= score <= 100


@pytest.mark.unit
def test_extract_missing_skills(sample_resume_text: str, sample_job_description: str) -> None:
    """Test missing and matched skills extraction."""
    engine = MatchingEngine()
    missing_skills, matched_skills = engine.extract_missing_skills(
        sample_resume_text, sample_job_description
    )
    assert isinstance(missing_skills, list)
    assert isinstance(matched_skills, list)


@pytest.mark.unit
def test_rank_candidates(sample_candidates: list[dict], sample_job_description: str) -> None:
    """Test candidate ranking."""
    engine = MatchingEngine()
    ranked = engine.rank_candidates(sample_candidates, sample_job_description)

    assert len(ranked) == len(sample_candidates)
    assert all("match_score" in c for c in ranked)
    assert ranked[0]["match_score"] >= ranked[-1]["match_score"]

