import asyncio
from agentic.rag_agent import run_rag_query

async def test():
    question = "Where is the database connection configured?"
    result = await run_rag_query(question)
    print("Answer:\n", result)

if __name__ == "__main__":
    asyncio.run(test())