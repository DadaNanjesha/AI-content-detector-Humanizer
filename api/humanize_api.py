from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import re

# Import processing helpers from the existing Streamlit page
from pages.humanize_text import (
    extract_citations,
    restore_citations,
    minimal_rewriting,
    preserve_linebreaks_rewrite,
    count_words,
    count_sentences,
)


DESCRIPTION = (
    """
AI Text Humanizer API

This API provides server-side access to the project's text humanization pipeline. It accepts
AI-generated text and returns an enhanced, more natural, human-like version while preserving
academic citations and structure. The endpoint exposes options to control synonym replacement
intensity and the frequency of added academic transitions.
"""
)

tags_metadata = [
    {
        "name": "humanize",
        "description": "Endpoints for transforming AI-generated text into human-like prose.",
    }
]

app = FastAPI(
    title="AI Text Humanizer API",
    version="0.2",
    description=DESCRIPTION,
    openapi_tags=tags_metadata,
)


class HumanizeRequest(BaseModel):
    text: str = Field(..., description="The input text to humanize. Must be non-empty.")
    p_syn: Optional[float] = Field(0.2, ge=0.0, le=1.0, description="Synonym replacement intensity (0.0-1.0)")
    p_trans: Optional[float] = Field(0.2, ge=0.0, le=1.0, description="Academic transition insertion probability (0.0-1.0)")
    preserve_linebreaks: Optional[bool] = Field(True, description="Whether to preserve original line breaks")

    class Config:
        schema_extra = {
            "example": {
                "text": "Recent studies (Smith et al., 2020) show promising results. It can't be ignored.",
                "p_syn": 0.3,
                "p_trans": 0.2,
                "preserve_linebreaks": True,
            }
        }


class HumanizeResponse(BaseModel):
    humanized_text: str = Field(..., description="The transformed human-like text result")
    orig_word_count: int
    orig_sentence_count: int
    new_word_count: int
    new_sentence_count: int
    words_added: int
    sentences_added: int

    class Config:
        schema_extra = {
            "example": {
                "humanized_text": "Moreover, Recent studies (Smith et al., 2020) show promising results. It cannot be ignored.",
                "orig_word_count": 11,
                "orig_sentence_count": 2,
                "new_word_count": 13,
                "new_sentence_count": 3,
                "words_added": 2,
                "sentences_added": 1,
            }
        }


@app.get("/health", tags=["humanize"], summary="Health check")
def health():
    """Returns OK when the service is healthy.

    Useful for simple uptime checks.
    """
    return {"status": "ok"}


@app.post(
    "/humanize",
    response_model=HumanizeResponse,
    tags=["humanize"],
    summary="Humanize input text",
    response_description="The transformed text and basic metrics",
)
def humanize(req: HumanizeRequest):
    """Transform AI-generated text into human-like prose.

    The endpoint will:
    - Preserve and protect citation strings (e.g., APA style) while rewriting
    - Optionally preserve original line breaks
    - Expand contractions, replace synonyms, and optionally add academic transitions

    Provide `p_syn` and `p_trans` to tune intensity of synonym replacement and
    transition insertion respectively (values between 0.0 and 1.0).
    """
    text = req.text or ""
    if not text.strip():
        raise HTTPException(status_code=400, detail="`text` must be a non-empty string")

    # Original stats
    orig_wc = count_words(text)
    orig_sc = count_sentences(text)

    # Protect citations
    no_refs_text, placeholders = extract_citations(text)

    # Choose rewrite mode
    if req.preserve_linebreaks:
        rewritten = preserve_linebreaks_rewrite(no_refs_text, p_syn=req.p_syn, p_trans=req.p_trans)
    else:
        rewritten = minimal_rewriting(no_refs_text, p_syn=req.p_syn, p_trans=req.p_trans)

    # Restore citations and normalize spacing similar to Streamlit page
    final_text = restore_citations(rewritten, placeholders)
    final_text = re.sub(r"[ \t]+([.,;:!?])", r"\1", final_text)
    final_text = re.sub(r"(\()[ \t]+", r"\1", final_text)
    final_text = re.sub(r"[ \t]+(\))", r"\1", final_text)
    final_text = re.sub(r"[ \t]{2,}", " ", final_text)
    final_text = re.sub(r"``\s*(.+?)\s*''", r'"\1"', final_text)

    new_wc = count_words(final_text)
    new_sc = count_sentences(final_text)

    return {
        "humanized_text": final_text,
        "orig_word_count": orig_wc,
        "orig_sentence_count": orig_sc,
        "new_word_count": new_wc,
        "new_sentence_count": new_sc,
        "words_added": new_wc - orig_wc,
        "sentences_added": new_sc - orig_sc,
    }


# if __name__ == "__main__":
#     # Quick developer run: python api/humanize_api.py
#     import uvicorn

#     uvicorn.run("api.humanize_api:app", host="127.0.0.1", port=8000, reload=True)
