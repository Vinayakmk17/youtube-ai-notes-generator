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
