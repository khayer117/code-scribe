import json
import logging
import re

import requests

from app.config import settings

logger = logging.getLogger(__name__)

_EXTRACTION_PROMPT = """\
You are a medical coding assistant specializing in ICD-10-PCS procedure coding.
Analyze the doctor's note below and extract the key procedure details.

Return a JSON object with exactly these fields:
{{
  "procedure_name": "the primary surgical or procedural intervention",
  "body_site": "the anatomical body part or organ involved",
  "approach": "surgical approach (Open, Laparoscopic, Endoscopic, Percutaneous, etc.)",
  "device": "any device, implant, graft, or stapler used — 'None' if not applicable",
  "qualifier": "additional qualifier such as destination site or laterality — 'None' if not applicable",
  "query": "a concise search phrase combining procedure, site, and approach for code matching"
}}

Doctor's Note:
{note}

Return ONLY valid JSON. No explanation, no markdown fences."""


def extract_procedure_info(note_content: str) -> dict:
    prompt = _EXTRACTION_PROMPT.format(note=note_content)
    try:
        resp = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.1},
            },
            timeout=settings.OLLAMA_TIMEOUT,
        )
        resp.raise_for_status()
        raw = resp.json().get("response", "{}")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                return json.loads(match.group())
            logger.warning("Could not parse Ollama response as JSON")
            return {"query": note_content[:500], "parse_error": True}
    except requests.exceptions.Timeout:
        raise RuntimeError(
            f"Ollama request timed out after {settings.OLLAMA_TIMEOUT}s. Is Ollama running?"
        )
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            f"Cannot connect to Ollama at {settings.OLLAMA_BASE_URL}. "
            "Start it with: ollama serve"
        )
    except Exception as exc:
        logger.error("Ollama extraction error: %s", exc)
        raise RuntimeError(f"Extraction failed: {exc}")
