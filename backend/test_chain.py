from test_embeddings import vectorstore  # our previous FAISS test
from chains.question_chain import generate_questions_for_jd

# Example JD
jd_chunk = """
Looking for a software engineer experienced with FastAPI,
Python backend development, and deploying scalable AI chat systems.
"""

# Retrieve top 4 resume chunks
retrieved_chunks = vectorstore.similarity_search(jd_chunk, k=4)

# Generate questions
questions_json = generate_questions_for_jd(jd_chunk, retrieved_chunks)

print("Generated Interview Questions:")
print(questions_json)