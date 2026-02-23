import os
from typing import List, Dict, TypedDict, AsyncGenerator
from dotenv import load_dotenv
import arxiv

from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.graph import StateGraph, END

from backend.rag import add_to_memory, retrieve_context

load_dotenv()

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
    temperature=0
)

# ------------------ Tool ------------------
@tool
def arxiv_search(query: str, max_results: int) -> List[Dict]:
    """
    Search arXiv for academic papers related to a topic.
    """
    client = arxiv.Client()
    search = arxiv.Search(query=query, max_results=max_results)

    papers = []
    for r in client.results(search):
        papers.append({
            "title": r.title,
            "authors": [a.name for a in r.authors],
            "summary": r.summary,
            "pdf_url": r.pdf_url
        })
    return papers


# ------------------ State ------------------
class ResearchState(TypedDict):
    task: str
    paper_count: int
    papers: List[Dict]
    final_report: str


# ------------------ Nodes ------------------
async def researcher(state: ResearchState):
    query_prompt = f"Extract best arXiv query from: {state['task']}"
    query = await llm.ainvoke(query_prompt)

    papers = arxiv_search.invoke({
        "query": query.content,
        "max_results": state["paper_count"]
    })

    add_to_memory(papers)

    return {**state, "papers": papers}


async def summarizer(state: ResearchState):
    context = retrieve_context(state["task"])

    prompt = f"""
    You are an expert researcher.

    Context from memory:
    {context}

    Papers:
    {state['papers']}

    Write a markdown literature review.
    """

    response = await llm.ainvoke(prompt)
    return {**state, "final_report": response.content}


# ------------------ Graph ------------------
graph = StateGraph(ResearchState)
graph.add_node("researcher", researcher)
graph.add_node("summarizer", summarizer)
graph.set_entry_point("researcher")
graph.add_edge("researcher", "summarizer")
graph.add_edge("summarizer", END)

app = graph.compile()


# ------------------ Public APIs ------------------
async def run_review(task: str, paper_count: int) -> str:
    result = await app.ainvoke({"task": task, "paper_count": paper_count})
    return result["final_report"]


async def stream_review(task: str, paper_count: int) -> AsyncGenerator[str, None]:
    async for event in app.astream({"task": task, "paper_count": paper_count}):
        if "final_report" in event:
            yield event["final_report"]
