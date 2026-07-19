"""Quiz orchestration service — ties together the full RAG pipeline."""

from services.search_service import search_sports_content
from services.vector_service import store_documents, query_relevant_context
from services.llm_service import generate_quiz


def generate_sports_quiz(sport: str, difficulty: str, num_questions: int = 5) -> dict:
    """
    Full RAG pipeline to generate a sports quiz.

    Steps:
        1. Search the web for fresh sports content via Tavily
        2. Store the results in ChromaDB for future retrieval
        3. Query ChromaDB for the most relevant context
        4. Build a prompt and call Gemini to generate quiz JSON
        5. Return the validated quiz

    Args:
        sport: The sport to generate questions about
        difficulty: easy, medium, or hard
        num_questions: Number of questions to generate (default 5)

    Returns:
        Dict with 'questions' list, 'sport', and 'difficulty' metadata
    """
    print(f"\n{'='*60}")
    print(f"[Pipeline] Generating {difficulty} {sport} quiz ({num_questions} questions)")
    print(f"{'='*60}")

    # Step 1: Search the web for fresh content
    print("\n[Step 1] Searching web for sports content...")
    search_results = search_sports_content(sport, difficulty)

    # Step 2: Store search results in ChromaDB
    print("[Step 2] Storing results in vector database...")
    if search_results:
        store_documents(sport, search_results)

    # Step 3: Query ChromaDB for relevant context
    print("[Step 3] Retrieving relevant context...")
    difficulty_queries = {
        "easy": f"{sport} popular facts famous players basic rules",
        "medium": f"{sport} records statistics notable events history",
        "hard": f"{sport} obscure trivia rare records lesser-known facts deep history",
    }
    query = difficulty_queries.get(difficulty, f"{sport} trivia facts")
    context = query_relevant_context(sport, query, n_results=5)

    # Step 4: Generate quiz using Gemini
    print("[Step 4] Generating quiz with LLM...")
    quiz_data = generate_quiz(sport, difficulty, context, num_questions)

    # Step 5: Attach metadata and return
    quiz_data["sport"] = sport
    quiz_data["difficulty"] = difficulty
    quiz_data["total_questions"] = len(quiz_data["questions"])

    print(f"\n[Pipeline] ✅ Quiz generated successfully!")
    return quiz_data
