from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

# -----------------------------
# System & user prompts
# -----------------------------
SYSTEM_PROMPT = """
You are a hiring manager conducting a real interview.

Your task is to generate interview questions that test whether
the candidate truly understands and can defend the experience
listed on their resume, in relation to the job description.

Rules:
- Questions must reference the candidate's experience implicitly or explicitly
- Avoid generic questions
- Prefer follow-up and depth-probing questions
- Output must be realistic and role-specific
"""

QUESTION_PROMPT_TEMPLATE = """
Job description:
{job_description}

Relevant resume context:
{resume_context}

Generate 5 interview questions that a real interviewer would ask.

Return JSON with this schema:
[
  {{
    "category": "Technical | Behavioral | Role-Specific",
    "question": "string"
  }}
]
"""

# -----------------------------
# Core function to call LLM
# -----------------------------
def generate_questions_for_jd(jd_chunk: str, resume_chunks: list) -> str:
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.4
    )

    # Convert Document objects to strings if needed
    resume_texts = [chunk.page_content if hasattr(chunk, "page_content") else str(chunk) for chunk in resume_chunks]
    resume_context = "\n\n".join(resume_texts)

    prompt = QUESTION_PROMPT_TEMPLATE.format(
        job_description=jd_chunk,
        resume_context=resume_context
    )

    # Call LLM with proper message format
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt)
    ]
    response = llm.invoke(messages)

    # Extract content from AIMessage object
    if hasattr(response, 'content'):
        return response.content
    elif isinstance(response, str):
        return response
    else:
        # Fallback: try to convert to string
        return str(response)

