from openai import OpenAI
import json

from config.config import settings

from writer.schema import CriticFeedback

# logging.basicConfig(
#     level="INFO"
# )

# logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=settings.openai_api_key
)

SYSTEM_PROMPT = """You are a technical documentation reviewer.

    Evaluate the documentation for its section type: installation, getting_started, or features.

    Requirements:

    installation:
    - Numbered steps
    - At least one code block
    - Prerequisites mentioned (if applicable)
    - Installation command present

    getting_started:
    - Minimal working example
    - Beginner-friendly language
    - Shows the shortest path to something working

    features:
    - Uses headers to separate features
    - Each feature has a brief explanation
    - Includes usage examples when applicable

    Be strict but concise.

    Return ONLY valid JSON:

    {
    "passed": true,
    "notes": "Brief explanation of missing requirements or quality issues. If all requirements are met, state why it passes."
    }
    """
def review_draft(section: str, draft: str) ->CriticFeedback:
    

    draft_content = f"Section Name: {section} \n{draft}"
    messages = [
        {"role":"system", "content":SYSTEM_PROMPT},
        {"role":"user", "content": draft_content}
    ]

    response = client.chat.completions.create(
        model='gpt-5-mini',
        messages=messages,
        response_format={"type": "json_object"}
    )
    try:
        raw = response.choices[0].message.content
        data = json.loads(raw)
        return CriticFeedback(
            passed=data["passed"],
            notes=data["notes"]
        )
    except Exception:
        return CriticFeedback(
            passed=True,
            notes="Could not parse critic response"
        )

