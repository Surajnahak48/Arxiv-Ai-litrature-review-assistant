import streamlit as st
import requests

st.title("📚 AI Literature Review Assistant")

topic = st.text_input("Research Topic")
papers = st.slider("Number of papers", 1, 10, 5)

if st.button("Generate"):
    res = requests.get("http://localhost:8000/review", params={
        "topic": topic,
        "papers": papers
    })
    st.markdown(res.json()["result"])

st.download_button(
    "📥 Download PDF",
    data=requests.get("http://localhost:8000/download", params={
        "topic": topic,
        "papers": papers
    }).content,
    file_name="review.pdf"
)
