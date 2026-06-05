# app/utils/text_cleaner.py
# PURPOSE: Clean messy raw text from PDFs before sending to NLP models.
# Dirty text (weird symbols, extra spaces) gives worse match scores.

import re


def clean_text(text: str) -> str:
    """
    Normalize raw text step by step:
    1. Replace line breaks with spaces
    2. Collapse multiple spaces into one
    3. Remove non-ASCII symbols
    4. Lowercase so 'Python' and 'python' both match the same skill
    """
    if not text:
        return ""
    text = text.replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s\-\+\.#]", " ", text)
    return text.strip().lower()


def chunk_text(text: str, chunk_size: int = 120, overlap: int = 20) -> list:
    """
    Split a long document into smaller overlapping word chunks.

    WHY CHUNKING?
    One embedding for a 500-word resume loses detail.
    Chunking = the model reads it in 120-word "paragraphs"
    so each section (skills, experience, education) gets
    its own vector representation.

    overlap=20 means consecutive chunks share 20 words
    so we never cut a sentence in half and lose context.
    """
    words = text.split()
    if not words:
        return []
    chunks, start = [], 0
    while start < len(words):
        chunk = " ".join(words[start : start + chunk_size])
        chunks.append(chunk)
        start += max(chunk_size - overlap, 1)
    return chunks