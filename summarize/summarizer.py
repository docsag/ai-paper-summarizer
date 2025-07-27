
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

PROMPT_TEMPLATE = """You are a science communicator. Given the following section from a scientific paper,
write a layperson-friendly summary. Avoid jargon, explain concepts clearly, and keep it concise.

SECTION TYPE: {section_name}

TEXT:
"""{section_text}"""

SUMMARY:
"""

def summarize_section(section_name, section_text, model="gpt-4"):
    prompt = PROMPT_TEMPLATE.format(section_name=section_name, section_text=section_text)
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that simplifies scientific content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=500
        )
        return response.choices[0].message['content'].strip()
    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return ""
