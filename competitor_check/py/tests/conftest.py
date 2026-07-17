"""Ensure the lightweight spaCy model used by the tests is available."""

import spacy


def _ensure_model(name: str = "en_core_web_sm") -> None:
    if not spacy.util.is_package(name):
        spacy.cli.download(name)  # type: ignore[attr-defined]


_ensure_model()
