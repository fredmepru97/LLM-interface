import streamlit as st
from Llama.llama import llama_page
from GPT.first import first_page
from GPT.app import main_app

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "GPT", "Llama", "Simple GPT"])

    if page == "Home":
        st.title("Home Page")
        st.write("Welcome to our home page!")
        st.text("-------------------------------------------------------------------------------")
        st.text("--- A Text, Web and Social Media Analytics Lab Project ---")
        st.text("-------------------------------------------------------------------------------")
        st.text("Team members: Jessica, Sarah, Raza, Viktor, Freddy ")
        st.text("-------------------------------------------------------------------------------")
    elif page == "GPT":
        main_app()
    elif page == "Llama":
        llama_page()
    elif page == "Simple GPT":
        first_page()

if __name__ == "__main__":
    main()
