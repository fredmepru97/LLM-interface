import openai
import streamlit as st
from dotenv import load_dotenv
import os
import json

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

openai.api_key = api_key

# Path to the prompts file
PROMPTS_FILE = 'prompts.json'

def load_prompts():
    if os.path.exists(PROMPTS_FILE):
        with open(PROMPTS_FILE, 'r') as f:
            return json.load(f)
    return {"llama": [], "chatgpt": [], "simple_gpt": []}

def save_prompts(prompts):
    with open(PROMPTS_FILE, 'w') as f:
        json.dump(prompts, f, indent=4)

def first_page():
    st.title("Natural Language to SQL Query Transformer unconnected")
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
            sql_query = generate_sql(query)
            st.write("Generated SQL Query:")
            st.code(sql_query, language='sql')

            # Save the prompt and SQL query to prompts.json
            prompts = load_prompts()
            prompts["simple_gpt"].append({
                "prompt": query,
                "sql_query": sql_query
            })
            save_prompts(prompts)
        else:
            st.write("Please enter a query.")
