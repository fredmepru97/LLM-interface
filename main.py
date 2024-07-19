import streamlit as st
from Llama.llama import llama_page
from GPT.first import first_page
from GPT.app import main_app

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home Page", "GPT", "Llama", "Simple GPT"])

    if page == "Home Page":
        st.title("Home Page")
        st.text("-------------------------------------------------------------------------------")
        st.text("-------------- A Text, Web and Social Media Analytics Lab Project -------------")
        st.text("-------------------------------------------------------------------------------")
        st.text("-------------- Team members: Jessica, Sarah, Raza, Viktor, Freddy -------------")
        st.text("-------------------------------------------------------------------------------")
        st.write("Welcome to our home page!")
        st.write("This is a project that uses GPT-3.5 Turbo and LLama to convert natural language to SQL queries.")
        st.write("- You can navigate to the GPT page to use GPT-3.5 Turbo to generate SQL queries.")
        st.write("- You can navigate to the LLama page to use LLama to generate SQL queries.")
        st.write("- You can navigate to the Simple GPT page to use GPT-3.5 Turbo to generate SQL queries without any connection to our database.")
        st.text("-------------------------------------------------------------------------------")
        st.text("---------------------------------- July 2024 ----------------------------------")
        
    elif page == "GPT":
        main_app()
    elif page == "Llama":
        llama_page()
    elif page == "Simple GPT":
        first_page()

if __name__ == "__main__":
    main()
