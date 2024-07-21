import streamlit as st
from Llama.llama_zero_shot import llama_zero_shot_app
from Llama.llama_one_shot import llama_one_shot_app
from GPT.gpt_zero_shot import gpt_zero_shot_app
from GPT.gpt_one_shot import gpt_one_shot_app

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home Page", "GPT", "Llama"])

    if page == "Home Page":
        st.title("Welcome to our home page!")
        st.text("-------------------------------------------------------------------------------")
        st.text("-------------- A Text, Web and Social Media Analytics Lab Project -------------")
        st.text("-------------- Team members: Jessica, Sarah, Raza, Victor, Freddy -------------")
        st.text("-------------------------------------------------------------------------------")
        st.write(" ")
        st.write("Our project uses GPT and LLama to convert natural language to SQL queries to later query a Duckdb database.")
        st.write("- You can navigate to the GPT page to use GPT-3.5 Turbo to generate SQL queries.")
        st.write("- You can navigate to the LLama page to use LLama to generate SQL queries.")
        st.write("- You can navigate to the Simple GPT page to use GPT-3.5 Turbo to generate SQL queries without a connection to our database.")
        st.write("- You can navigate to the Simple LLama page to use LLama to generate SQL queries without a connection to our database.")
        st.text(" ")
        st.text("-------------------------------------------------------------------------------")
        st.text("---------------------------------- July 2024 ----------------------------------")
        
    elif page == "GPT":
            gpt_zero_shot_app()
            gpt_one_shot_app()
    elif page == "Llama":
            llama_zero_shot_app()
            llama_one_shot_app()

if __name__ == "__main__":
    main()
