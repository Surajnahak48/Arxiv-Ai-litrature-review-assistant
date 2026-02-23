# import os
# import asyncio
# from dotenv import load_dotenv
# from typing import List, Dict, TypedDict

# import arxiv
# from langchain_openai import ChatOpenAI
# from langchain.tools import tool
# from langgraph.graph import StateGraph, END

# # ---------------------------------------------------
# # Environment
# # ---------------------------------------------------
# load_dotenv()

# llm = ChatOpenAI(
#     model="deepseek-reasoner",                 # ✅ DeepSeek model
#     api_key=os.getenv("DEEPSEEK_API_KEY"),
#     base_url="https://api.deepseek.com/v1", # ✅ DeepSeek endpoint
#     temperature=0
# )

# # ---------------------------------------------------
# # Tool: arXiv Search
# # ---------------------------------------------------
# @tool
# def arxiv_search(query: str, max_results: int = 5) -> List[Dict]:
#     """
#     Search arXiv and return a compact list of papers.
#     """
#     client = arxiv.Client()
#     search = arxiv.Search(
#         query=query,
#         max_results=max_results,
#         sort_by=arxiv.SortCriterion.Relevance,
#     )

#     papers = []
#     for result in client.results(search):
#         papers.append({
#             "title": result.title,
#             "author": [a.name for a in result.authors],
#             "published": result.published.strftime("%Y-%m-%d"),
#             "summary": result.summary,
#             "pdf_url": result.pdf_url,
#         })

#     return papers


# # ---------------------------------------------------
# # Graph State
# # ---------------------------------------------------
# class ResearchState(TypedDict):
#     task: str
#     papers: List[Dict]
#     final_report: str


# # ---------------------------------------------------
# # Node 1: Researcher
# # ---------------------------------------------------
# async def researcher_node(state: ResearchState) -> ResearchState:
#     task = state["task"]

#     prompt = f"""
#     Given the topic below, create the best arXiv search query.
#     Topic: {task}
#     """

#     query = await llm.ainvoke(prompt)

#     papers = arxiv_search.invoke({
#         "query": query.content,
#         "max_results": 5
#     })

#     return {
#         "task": task,
#         "papers": papers
#     }


# # ---------------------------------------------------
# # Node 2: Summarizer
# # ---------------------------------------------------
# async def summarizer_node(state: ResearchState) -> ResearchState:
#     papers = state["papers"]

#     prompt = f"""
#     You are an expert researcher.

#     Write a literature-review style report in Markdown:

#     1. Start with a 2–3 sentence introduction.
#     2. One bullet per paper with:
#        - Title (Markdown link)
#        - Authors
#        - Problem tackled
#        - Key contribution
#     3. End with a single-sentence takeaway.

#     Papers:
#     {papers}
#     """

#     response = await llm.ainvoke(prompt)

#     return {
#         **state,
#         "final_report": response.content
#     }


# # ---------------------------------------------------
# # Build Graph
# # ---------------------------------------------------
# graph = StateGraph(ResearchState)

# graph.add_node("researcher", researcher_node)
# graph.add_node("summarizer", summarizer_node)

# graph.set_entry_point("researcher")
# graph.add_edge("researcher", "summarizer")
# graph.add_edge("summarizer", END)

# app = graph.compile()


# # ---------------------------------------------------
# # Run
# # ---------------------------------------------------
# async def run():
#     task = "Conduct a literature review on Autogen and return exactly 5 papers"

#     result = await app.ainvoke({"task": task})

#     print("\n===== FINAL REPORT =====\n")
#     print(result["final_report"])


# if __name__ == "__main__":
#     asyncio.run(run())
