import openai
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

openai.api_key = api_key

def first_page():
    st.title("Unconnected Natural Language to SQL Query transformer using GPT-3.5 Turbo")
    st.text("-------------------------------------------------------------------------------")
    subheader_css = """
    <style>
        .st-eb {
            font-size: 16px;
        }
    </style>
    """
    st.markdown(subheader_css, unsafe_allow_html=True)
    st.subheader("Part 1: Convert natural language to SQL queries")

    page_bg_css = """
    <style>
        body {
            background-color: #7F00FF;
        }
    </style>
    """

    st.markdown(page_bg_css, unsafe_allow_html=True)

    # Text input
    query = st.text_area('Enter your text to generate SQL query', '')

    def generate_sql(query):
        model_engine = "gpt-3.5-turbo"
        prompt = (
            f"Translate the following natural language query to SQL:\n"
            f"{query}\n"
            f"SQL:"
        )
        response = openai.ChatCompletion.create(
            model=model_engine,
            messages=[
                {"role": "system", "content": "You are an SQL expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            stop=["#", ";"]
        )
        return response.choices[0].message['content'].strip()

    if st.button('Generate SQL query'):
        if len(query) > 0:
            Respo = generate_sql(query)
            st.write(Respo)
