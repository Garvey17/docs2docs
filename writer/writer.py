from openai import OpenAI
from typing import Literal
from organiser.schema import ClassifiedContent, OrganisedDocs
from config.config import settings
import logging
from writer.schema import DocSection
from writer.critic import review_draft

logging.basicConfig(
    level="INFO"
)

logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=settings.openai_api_key
)

BASE_SYSTEM_PROMPT = """
You are an expert technical documentation writer.

Your task is to transform raw documentation content into clean,
well-structured markdown.

Requirements:
- Preserve technical accuracy.
- Remove repetition.
- Use concise language.
- Use proper markdown formatting.
- Include code blocks when relevant.
- Do not invent information.
- Only use information present in the provided content.
"""

SECTION_PROMPTS = {
    "installation": """
Write a concise installation guide.

Requirements:
- Start with a short introduction.
- Cover prerequisites.
- Cover installation commands.
- Cover required configuration.
- Use numbered steps.
- Put all commands in code blocks.
- End with a verification step if available.
""",

    "getting_started": """
Write a concise getting started guide for new users.

Requirements:
- Assume the software is already installed.
- Focus on the smallest path to success.
- Explain only the essential concepts.
- Include a minimal working example.
- Keep explanations beginner-friendly.
- Use numbered steps.
- Put code in code blocks.
""",

    "features": """
Write a concise features overview.

Requirements:
- Group related features together.
- Create a section for each feature.
- Explain what the feature does.
- Explain when it should be used.
- Include a brief usage example when available.
- Use markdown headers to separate features.
- Avoid installation instructions.
"""
}

REVISION_SYSTEM_PROMPT = """
            You are a one shot revision system for a system that converts documentation websites into downloadable documents containing majorly installation guides, getting_started instructions and features
            you will be given the draft that failed the critic
            you will also be given the notes that the critic system provided

            Please fix only the identified issues. Do not change sections that are already correct.
            """

def build_system_prompt(section: str) -> str:
    return(
        BASE_SYSTEM_PROMPT
        +
        "\n\n"
        +
        SECTION_PROMPTS[section]
    )

def generate_draft(section: Literal["installation", "getting_started", "features"], contents: list[ClassifiedContent]) -> str:
    if not contents:
        logger.info('Empty content passed to func: generate_draft')
        return ""
    combined_content = ""

    for content in contents:
        page_content = content.raw_text
        title = content.source_title

        combined_content = combined_content + f"\n\n-------Source: {title}------\n\n{page_content}"
    
    SYSTEM_PROMPT = build_system_prompt(section)
    combined_content = combined_content[:6000] #words cap at 3000 words for predictable api pricing
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": combined_content}
    ]

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=messages
    )

    return response.choices[0].message.content

def write_section(organised:OrganisedDocs) -> list[DocSection]:
    result: list[DocSection] =[]

    section_map ={
        "installation": organised.installation,
        "getting_started": organised.getting_started,
        "features": organised.features
    }

    for section_name, content in section_map.items():
        if not content:
            logger.info(f'Skipping empty section : {section_name}')
            continue
        #call generate_draft function
        draft = generate_draft(section_name, content)

        feedback = review_draft(section_name, draft)

        revision_count = 0
        if not feedback.passed:
            messages = [
                {"role":"system", "content":REVISION_SYSTEM_PROMPT},
                {"role": "user", "content": f"Draft:\n\n{draft}\n\nIssues to fix:\n\n{feedback.notes}"}
            ]
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=messages
            )

            draft = response.choices[0].message.content
            
            revision_count = 1
        
        result.append(DocSection(
            section=section_name,
            content=draft,
            revision_count=revision_count
        ))
    return result


