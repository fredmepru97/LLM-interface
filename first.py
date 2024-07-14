import openai
import streamlit as st

openai.api_key = st.secrets["pass"]

st.title("LLM Interface for Databases")
st.text("Team members: Jessica, Sarah, Raza, Viktor, Freddy ")

subheader_css = """
<style>
    .st-eb {
        font-size: 16px;
    }
</style>
"""
st. text("-------------------------------------------------------------------------------")

st.markdown(subheader_css, unsafe_allow_html=True)
st.text("--- A Text, Web and Social Media Analytics Lab Project ---")

st. text("-------------------------------------------------------------------------------")
st.subheader("Part 1: Convert natural language to SQL queries")

page_bg_css = """
<style>
    body {
        background-color: #7F00FF;
    }
</style>
"""

st.markdown(page_bg_css, unsafe_allow_html=True)

#----------------------------------------------------------------------------------------------------------------------

# Text input
query = st.text_area('Enter your text to generate SQL query', '')

#----------------------------------------------------------------------------------------------------------------------

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
