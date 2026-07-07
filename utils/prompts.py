"""
utils/prompts.py
-----------------
All prompt templates for Gemini.
Kept separate from API logic so they can be tuned independently.
"""


def get_notes_prompt(
    transcript: str,
    language: str = "English",
    transcript_language: str = "en",
    length: str = "Detailed",
) -> str:
    """
    Returns the prompt for generating structured study notes from a transcript.

    Args:
        transcript:          The raw transcript text.
        language:            Desired output language (English / Hindi / Kannada).
        transcript_language: The ISO-639-1 code of the transcript's language.
        length:              Detail level — "Brief", "Standard", or "Detailed".
    """
    lang_instruction = ""
    if transcript_language != "en":
        lang_instruction = (
            f"\nIMPORTANT: The transcript is in '{transcript_language}'. "
            f"You MUST still generate the output in **{language}**. "
            "Translate any content as needed.\n"
        )

    return f"""You are an expert AI learning assistant. Your task is to process the following YouTube video transcript and generate comprehensive, well-structured study notes.

Output Language: {language}
Detail Level: {length}
{lang_instruction}
Structure your output using the following markdown sections.  
Do NOT skip any section — write "N/A" if a section truly does not apply.

## 📋 Executive Summary
Provide a high-level summary of the video in 2-3 paragraphs. Cover the main topic, why it matters, and what the viewer will learn.

## 🔑 Key Points
List the 5-10 most important takeaways as bullet points.

## 📝 Detailed Notes
Provide a thorough breakdown of the content, organised with subheadings (### ) for each major topic or section of the video. Include all significant details.

## 💡 Important Concepts & Definitions
Present key terms and concepts in a table format:
| Concept | Definition |
|---------|-----------|

## 📌 Examples & Analogies
Highlight specific examples, case studies, or analogies used in the video. Explain each briefly.

## ✅ Final Takeaways
Summarise the 3-5 most important things a student should remember.

---
Transcript:
{transcript}
"""


def get_quiz_prompt(transcript: str) -> str:
    """
    Returns the prompt for generating a 10-question multiple-choice quiz.
    """
    return f"""You are an expert AI learning assistant. Generate a 10-question multiple-choice quiz based on the following transcript.
You MUST output raw JSON format with the following structure:
[
  {{
    "question": "Question text here?",
    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
    "answer": "A) Option 1",
    "explanation": "Short explanation here."
  }}
]

Transcript:
{transcript}
"""


def get_flashcards_prompt(transcript: str) -> str:
    """
    Returns the prompt for generating 15 flashcards.
    """
    return f"""You are an expert AI learning assistant. Generate 15 flashcards based on the following transcript.
You MUST output raw JSON format with the following structure:
[
  {{
    "question": "Question text here",
    "answer": "Answer text here"
  }}
]

Transcript:
{transcript}
"""


def get_interview_prompt(transcript: str) -> str:
    """
    Returns the prompt for generating 15 interview questions (5 Beginner, 5 Intermediate, 5 Advanced).
    """
    return f"""You are an expert AI learning assistant. Generate 15 interview questions based on the following transcript.
Include 5 Beginner, 5 Intermediate, and 5 Advanced questions.
You MUST output raw JSON format with the following structure:
{{
  "Beginner": [
    {{ "question": "Question text?", "answer": "Suggested answer." }}
  ],
  "Intermediate": [
    {{ "question": "Question text?", "answer": "Suggested answer." }}
  ],
  "Advanced": [
    {{ "question": "Question text?", "answer": "Suggested answer." }}
  ]
}}

Transcript:
{transcript}
"""


def get_practice_prompt(transcript: str) -> str:
    """
    Returns the prompt for generating Practice questions (Easy, Medium, Hard).
    """
    return f"""You are an expert AI learning assistant. Generate practice questions based on the following transcript.
Include Easy, Medium, and Hard practice questions.
You MUST output raw JSON format with the following structure:
{{
  "Easy": [
    {{ "question": "Question text?", "solution": "Step-by-step solution." }}
  ],
  "Medium": [
    {{ "question": "Question text?", "solution": "Step-by-step solution." }}
  ],
  "Hard": [
    {{ "question": "Question text?", "solution": "Step-by-step solution." }}
  ]
}}

Transcript:
{transcript}
"""
