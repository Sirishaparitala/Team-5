"""Google Gemini LLM service for generating quiz questions."""

import json
import re
from google import genai
from config import Config


_client = None


def _get_client() -> genai.Client:
    """Lazy-initialize the Gemini client."""
    global _client
    if _client is None:
        _client = genai.Client(api_key=Config.GEMINI_API_KEY)
    return _client


QUIZ_PROMPT_TEMPLATE = """You are an expert sports quiz master. Generate exactly {num_questions} multiple-choice quiz questions about {sport}.

**Difficulty Level**: {difficulty}
- Easy: Well-known facts, popular players, basic rules, famous events
- Medium: Statistics, records, notable but less famous events, rule nuances
- Hard: Obscure trivia, historical deep-cuts, rare records, lesser-known players

**Context Information** (use this to ground your questions in facts):
{context}

**CRITICAL RULES**:
1. Every question MUST be factually accurate and verifiable.
2. There must be exactly ONE correct answer per question.
3. Wrong options must be plausible but clearly incorrect.
4. Explanations must cite the factual basis for the correct answer.
5. Do NOT repeat questions from previous generations.
6. Questions should cover diverse topics within the sport (history, rules, records, players, events).

**Output Format**: Return ONLY valid JSON (no markdown, no code fences) matching this exact schema:
{{
  "questions": [
    {{
      "id": 1,
      "question": "The question text?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A",
      "explanation": "Explanation of why this is correct, grounded in facts."
    }}
  ]
}}
"""


def generate_quiz(
    sport: str,
    difficulty: str,
    context: str,
    num_questions: int = 5,
) -> dict:
    """
    Generate a quiz using Google Gemini with RAG context.

    Returns a dict with a 'questions' key containing the list of MCQs.
    """
    client = _get_client()

    prompt = QUIZ_PROMPT_TEMPLATE.format(
        num_questions=num_questions,
        sport=sport,
        difficulty=difficulty.capitalize(),
        context=context if context else "No additional context available. Use your built-in knowledge.",
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        raw_text = response.text.strip()

        # Strip markdown code fences if the LLM wraps them anyway
        raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
        raw_text = re.sub(r"\s*```$", "", raw_text)

        quiz_data = json.loads(raw_text)

        # Validate structure
        if "questions" not in quiz_data:
            raise ValueError("LLM response missing 'questions' key")

        for i, q in enumerate(quiz_data["questions"]):
            q["id"] = i + 1  # Ensure sequential IDs
            required = ["question", "options", "correct_answer", "explanation"]
            for key in required:
                if key not in q:
                    raise ValueError(f"Question {i + 1} missing '{key}'")
            if len(q["options"]) != 4:
                raise ValueError(f"Question {i + 1} must have exactly 4 options")

        print(f"[LLM] Generated {len(quiz_data['questions'])} questions")
        return quiz_data

    except json.JSONDecodeError as e:
        print(f"[LLM] JSON parse error: {e}")
        print(f"[LLM] Raw response: {raw_text[:500]}")
        raise ValueError(f"Failed to parse LLM response as JSON: {e}")
    except Exception as e:
        print(f"[LLM] Error: {e}")
        raise
