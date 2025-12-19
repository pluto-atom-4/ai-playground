"""NLP Resume Parser module for extracting text and entities from resumes."""

from typing import Optional


class ResumeParser:
    """
    Parser for extracting structured information from resume documents.

    This module handles:
    - PDF text extraction
    - Entity recognition (names, emails, phone numbers, etc.)
    - Skill extraction from resume content
    """

    def __init__(self, model_name: str = "en_core_web_sm") -> None:
        """
        Initialize the resume parser.

        Args:
            model_name: Name of the spaCy model to use for NLP tasks

        Raises:
            ValueError: If the spaCy model is not available
        """
        self.model_name = model_name
        self._nlp = None

    @property
    def nlp(self):
        """Lazy load spaCy model."""
        if self._nlp is None:
            try:
                import spacy

                self._nlp = spacy.load(self.model_name)
            except OSError as e:
                raise ValueError(
                    f"spaCy model '{self.model_name}' not found. "
                    f"Install it with: python -m spacy download {self.model_name}"
                ) from e
        return self._nlp

    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from a PDF resume.

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text from the PDF

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file is not a valid PDF
        """
        try:
            from PyPDF2 import PdfReader
        except ImportError as e:
            raise ImportError("PyPDF2 is required for PDF parsing") from e

        with open(file_path, "rb") as file:
            pdf_reader = PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text

    def extract_entities(self, text: str) -> dict:
        """
        Extract named entities from resume text.

        Args:
            text: Resume text content

        Returns:
            Dictionary containing extracted entities (PERSON, ORG, etc.)
        """
        doc = self.nlp(text)
        entities = {}
        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            entities[ent.label_].append(ent.text)

        return entities

    def extract_skills(self, text: str, custom_skills: Optional[list[str]] = None) -> list[str]:
        """
        Extract skills from resume text.

        Args:
            text: Resume text content
            custom_skills: Optional list of custom skill keywords to search for

        Returns:
            List of identified skills
        """
        # This is a basic implementation - can be enhanced with more sophisticated methods
        skills = custom_skills or []
        doc = self.nlp(text.lower())

        # Extract nouns that might be skills
        skill_keywords = set()
        for token in doc:
            if token.pos_ in ("NOUN", "PROPN"):
                skill_keywords.add(token.text)

        return list(skill_keywords)

