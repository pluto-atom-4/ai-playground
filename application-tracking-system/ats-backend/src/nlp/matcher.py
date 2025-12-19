"""Candidate-Job Matching Engine using TF-IDF and Cosine Similarity."""

from typing import Optional

import numpy as np


class MatchingEngine:
    """
    Matching engine for ranking candidates against job descriptions.

    Uses TF-IDF and cosine similarity to calculate match scores between
    resume content and job descriptions.
    """

    def __init__(self) -> None:
        """Initialize the matching engine."""
        self._vectorizer = None
        self._tfidf_matrix = None

    @property
    def vectorizer(self):
        """Lazy load TfidfVectorizer."""
        if self._vectorizer is None:
            from sklearn.feature_extraction.text import TfidfVectorizer

            self._vectorizer = TfidfVectorizer(max_features=500, stop_words="english")
        return self._vectorizer

    def calculate_match_score(
        self, resume_text: str, job_description: str, max_score: float = 100.0
    ) -> float:
        """
        Calculate TF-IDF based match score between resume and job description.

        Args:
            resume_text: Full text of the resume
            job_description: Full text of the job description
            max_score: Maximum score value (default: 100)

        Returns:
            Match score between 0 and max_score
        """
        try:
            from sklearn.metrics.pairwise import cosine_similarity
        except ImportError as e:
            raise ImportError("scikit-learn is required for matching") from e

        # Vectorize texts
        documents = [resume_text, job_description]
        tfidf_matrix = self.vectorizer.fit_transform(documents)

        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        score = float(similarity[0][0]) * max_score

        return score

    def extract_missing_skills(
        self, resume_text: str, job_description: str, threshold: float = 0.01
    ) -> tuple[list[str], list[str]]:
        """
        Extract missing and matched skills between resume and job description.

        Args:
            resume_text: Full text of the resume
            job_description: Full text of the job description
            threshold: TF-IDF threshold for considering a word as a skill

        Returns:
            Tuple of (missing_skills, matched_skills)
        """
        documents = [resume_text, job_description]
        tfidf_matrix = self.vectorizer.fit_transform(documents)

        # Get feature names (words)
        feature_names = np.array(self.vectorizer.get_feature_names_out())

        # Get non-zero features from job description
        job_features = tfidf_matrix[1].nonzero()[1]
        resume_features = tfidf_matrix[0].nonzero()[1]

        job_words = set(feature_names[job_features])
        resume_words = set(feature_names[resume_features])

        missing_skills = list(job_words - resume_words)
        matched_skills = list(job_words & resume_words)

        return missing_skills, matched_skills

    def rank_candidates(
        self,
        candidates: list[dict],
        job_description: str,
        max_score: float = 100.0,
    ) -> list[dict]:
        """
        Rank multiple candidates against a job description.

        Args:
            candidates: List of candidate dictionaries with 'resume_text' key
            job_description: Full text of the job description
            max_score: Maximum score value (default: 100)

        Returns:
            List of candidates sorted by match score (highest first)
        """
        ranked_candidates = []

        for candidate in candidates:
            resume_text = candidate.get("resume_text", "")
            score = self.calculate_match_score(resume_text, job_description, max_score)
            missing_skills, matched_skills = self.extract_missing_skills(
                resume_text, job_description
            )

            ranked_candidate = {
                **candidate,
                "match_score": score,
                "missing_skills": missing_skills,
                "matched_skills": matched_skills,
            }
            ranked_candidates.append(ranked_candidate)

        # Sort by score in descending order
        ranked_candidates.sort(key=lambda x: x["match_score"], reverse=True)

        return ranked_candidates

