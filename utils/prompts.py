"""
utils/prompts.py
-----------------
All prompt templates for VidNote AI — Gemini.
Kept separate from API logic so they can be tuned independently.
Includes improved prompt engineering with detailed instructions.
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
        language:            Desired output language (English / Hindi / Kannada, etc.).
        transcript_language: The ISO-639-1 code of the transcript's language.
        length:              Detail level — "Brief", "Standard", or "Detailed".
    """
    length_guide = {
        "Brief":    "Write concise, bullet-heavy notes. Keep each section short.",
        "Standard": "Write balanced notes with moderate detail in each section.",
        "Detailed": "Write comprehensive, thorough notes. Include all significant details, sub-topics, and nuances.",
    }.get(length, "Write detailed notes.")

    lang_instruction = ""
    if transcript_language not in ("en", language[:2].lower()):
        lang_instruction = (
            f"\nIMPORTANT: The transcript is in '{transcript_language}'. "
            f"You MUST still generate the output in **{language}**. "
            "Translate any content as needed.\n"
        )

    return f"""You are an expert AI learning assistant and educator. Your task is to process the following YouTube video transcript and generate premium, well-structured study notes optimised for student learning.

Output Language: {language}
Detail Level: {length} — {length_guide}
{lang_instruction}
Structure your output using the sections below. Do NOT skip any section — write "N/A" if it truly does not apply.
Use clean Markdown formatting with proper headers, bullet points, and tables.

## 📋 Executive Summary
Write a high-level overview (2-3 paragraphs) covering:
- The main topic and why it matters
- What the viewer will learn
- The overall conclusion or insight

## 🔑 Key Points
List the **7-10 most critical takeaways** as concise bullet points. Each point should be actionable or memorable.

## 📝 Detailed Notes
Provide a structured breakdown using ### subheadings for each major topic or section of the video. Include:
- All significant details, explanations, and sub-topics
- Step-by-step processes if applicable
- Important warnings or caveats

## 💡 Important Concepts & Definitions
Present key terms in a markdown table:
| Concept | Definition | Example |
|---------|------------|---------|

## 📌 Examples & Analogies
List every specific example, case study, code snippet, or analogy from the video. Explain each briefly and why it matters.

## 🔗 Connections & Real-World Applications
Explain how the concepts connect to real-world use cases, careers, or other subjects.

## ✅ Final Takeaways
Write the **3-5 most important things a student MUST remember** in bold, memorable statements.

## 📚 Recommended Next Steps
Suggest 3-5 logical next topics or skills to learn after mastering this content.

---
Transcript:
{transcript}
"""


def get_quiz_prompt(transcript: str) -> str:
    """
    Returns the prompt for generating a 10-question multiple-choice quiz.
    """
    return f"""You are an expert educator and assessment designer. Generate a high-quality 10-question multiple-choice quiz based on the following transcript.

Requirements:
- Mix of factual recall, conceptual understanding, and application questions
- 4 options per question (A, B, C, D) — plausible distractors only, no obvious wrong answers
- Each question must have a clear correct answer and a helpful explanation
- Vary difficulty: 3 easy, 4 medium, 3 hard

You MUST output ONLY a raw JSON array with the following structure (no markdown, no backticks):
[
  {{
    "question": "Question text here?",
    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
    "answer": "A) Option 1",
    "explanation": "Short explanation of why this is correct and why others are wrong."
  }}
]

Transcript:
{transcript}
"""


def get_flashcards_prompt(transcript: str) -> str:
    """
    Returns the prompt for generating 15 flashcards.
    """
    return f"""You are an expert educator specialising in spaced repetition learning. Generate 15 high-quality flashcards based on the following transcript.

Requirements:
- Cover the most important concepts, definitions, and facts
- Front (question) should be concise and clear
- Back (answer) should be complete but concise (1-3 sentences max)
- Mix of definition cards, concept cards, and application cards

You MUST output ONLY a raw JSON array with the following structure (no markdown, no backticks):
[
  {{
    "question": "What is [concept]?",
    "answer": "Complete answer here."
  }}
]

Transcript:
{transcript}
"""


def get_interview_prompt(transcript: str) -> str:
    """
    Returns the prompt for generating 15 interview questions (5 Beginner, 5 Intermediate, 5 Advanced).
    """
    return f"""You are a senior technical interviewer and educator. Generate 15 interview questions based on the following transcript for someone preparing for interviews on this topic.

Requirements:
- 5 Beginner: foundational knowledge, definitions, basic understanding
- 5 Intermediate: conceptual depth, comparisons, practical applications
- 5 Advanced: system design, trade-offs, edge cases, expert-level reasoning
- Each answer should be comprehensive — what an interviewer would expect to hear

You MUST output ONLY a raw JSON object with the following structure (no markdown, no backticks):
{{
  "Beginner": [
    {{ "question": "Question text?", "answer": "Detailed suggested answer." }}
  ],
  "Intermediate": [
    {{ "question": "Question text?", "answer": "Detailed suggested answer." }}
  ],
  "Advanced": [
    {{ "question": "Question text?", "answer": "Detailed suggested answer." }}
  ]
}}

Transcript:
{transcript}
"""


def get_practice_prompt(transcript: str) -> str:
    """
    Returns the prompt for generating Practice questions (Easy, Medium, Hard).
    """
    return f"""You are an expert educator and problem designer. Generate practice questions based on the following transcript to help students develop hands-on skills.

Requirements:
- Easy (3 questions): Basic application of concepts, straightforward tasks
- Medium (3 questions): Multi-step problems requiring deeper understanding
- Hard (3 questions): Complex scenarios, design challenges, or open-ended problems
- Each solution must be detailed and step-by-step

You MUST output ONLY a raw JSON object with the following structure (no markdown, no backticks):
{{
  "Easy": [
    {{ "question": "Question text?", "solution": "Step-by-step solution here." }}
  ],
  "Medium": [
    {{ "question": "Question text?", "solution": "Step-by-step solution here." }}
  ],
  "Hard": [
    {{ "question": "Question text?", "solution": "Step-by-step solution here." }}
  ]
}}

Transcript:
{transcript}
"""


def get_study_planner_prompt(notes: str, video_title: str = "") -> str:
    """
    Returns the prompt for generating an AI study planner / learning roadmap.
    """
    return f"""You are an expert learning coach and curriculum designer.
Based on the following study notes{f' from the video "{video_title}"' if video_title else ''}, generate a comprehensive personalised study plan.

Output Language: English

You MUST output a well-formatted Markdown document with the following sections:

## 🗺️ Learning Roadmap
Create a visual 4-week learning roadmap with specific daily/weekly goals.
Format as a table:
| Week | Focus Area | Goals | Time (hrs) |
|------|-----------|-------|------------|

## 📚 Core Topics to Master
List the 5-8 essential topics from these notes in order of importance and dependency.
For each topic, include:
- **Topic name**: Brief description + why it matters + estimated study time

## 🎯 Next Topics to Explore
Suggest 5 advanced or related topics to explore AFTER mastering this content.
For each: name, brief description, and why it's a logical next step.

## 🎥 Recommended Video Types
Suggest 5 types of YouTube videos/content to search for to deepen understanding (give specific search queries).

## 📅 Daily Study Schedule Template
Create a 7-day study schedule template (1-2 hours/day):
| Day | Activity | Duration | Resources |
|-----|----------|----------|-----------|

## ⚡ Quick Revision Checklist
List 10 key checkpoints — things the student should be able to do/explain before moving on.

## 🏆 Milestone Project Ideas
Suggest 2-3 hands-on project ideas to solidify learning.

---
Study Notes:
{notes[:6000]}
"""


def get_mind_map_prompt(notes: str) -> str:
    """
    Returns the prompt for generating a structured mind map in Markdown.
    """
    return f"""You are an expert visual learning designer. Generate a comprehensive mind map from the following study notes.

Output the mind map as a structured Markdown outline using the following format:
- Use # for the central topic
- Use ## for main branches (4-6 max)
- Use ### for sub-branches
- Use - for leaf nodes (specific facts, concepts, examples)
- Add relevant emojis to make it visually engaging

The mind map should be hierarchical, comprehensive, and easy to scan.
Focus on the most important concepts and their relationships.

Example structure:
# 🎯 Central Topic
## 🔑 Main Branch 1
### Sub-Branch 1.1
- Detail
- Detail
### Sub-Branch 1.2
- Detail
## 🔑 Main Branch 2
...

Study Notes:
{notes[:5000]}
"""


def get_revision_notes_prompt(notes: str) -> str:
    """
    Returns the prompt for generating AI revision notes (condensed, exam-ready).
    """
    return f"""You are an expert educator specialising in exam preparation. Create ultra-concise revision notes from the following study notes.

Format the output as a premium revision sheet with:

## ⚡ Quick Summary (3 sentences max)
The absolute essence of this topic in 3 sentences.

## 🔑 Must-Know Concepts
5-7 concepts as: **Term**: One-line definition

## 📐 Key Formulas / Rules / Principles
List any formulas, rules, or principles. Format: **Name**: Formula/Rule

## ⚠️ Common Mistakes to Avoid
3-5 common misconceptions or errors students make.

## 🎯 Exam Tips
3-5 actionable tips for answering exam questions on this topic.

## 🔁 Spaced Repetition Cues
5 self-test questions with one-word/phrase answer clues:
Q: [Question] → A: [Clue]

Study Notes:
{notes[:5000]}
"""


def get_chat_prompt(notes: str, conversation_history: str, question: str, language: str = "English") -> str:
    """
    Returns the full prompt for the AI chat feature.
    """
    return f"""You are an expert AI tutor helping a student understand content from a YouTube video.
You have access to detailed study notes below. Answer all questions in a helpful, clear, and engaging manner.

Output Language: {language}
Guidelines:
- Keep answers concise but complete
- Use bullet points, numbered lists, and examples where helpful
- If the question is not related to the notes, gently redirect
- Use encouraging, friendly language

=== STUDY NOTES ===
{notes[:7000]}
=== END NOTES ===

=== CONVERSATION HISTORY ===
{conversation_history[-3000:] if len(conversation_history) > 3000 else conversation_history}
=== END HISTORY ===

Student's Question: {question}

AI Tutor's Answer:"""
