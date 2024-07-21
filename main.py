import streamlit as st
from Llama.llama_zero_shot import llama_zero_shot_app
from Llama.llama_one_shot import llama_one_shot_app
from GPT.gpt_zero_shot import gpt_zero_shot_app
from GPT.gpt_one_shot import gpt_one_shot_app

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home Page", "GPT", "Llama"])

    if page == "Home Page":
        st.title("Welcome to LLM Interface for Databases!") 
        st.text("-------------------------------------------------------------------------------")
        st.text("-------------- A Text, Web and Social Media Analytics Lab Project -------------")
        st.text("-------------- Team members: Jessica, Sarah, Raza, Victor, Freddy -------------")
        st.text("-------------------------------------------------------------------------------")
        st.write(" ")
        st.write("Our project uses GPT and LLama to convert natural language to SQL queries to later query a DuckDB database.")
        st.write("- You can navigate to the GPT page to use GPT-3.5 Turbo to generate SQL queries using both zero-shot and one-shot prompting strategies.")
        st.write("- You can navigate to the GPT page to use Llama 3 70B to generate SQL queries using both zero-shot and one-shot prompting strategies.")
        st.text("-------------------------------------------------------------------------------")
        
    elif page == "GPT":
            gpt_zero_shot_app()
            gpt_one_shot_app()
    elif page == "Llama":
            llama_zero_shot_app()
            llama_one_shot_app()

if __name__ == "__main__":
    main()
