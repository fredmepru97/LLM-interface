import streamlit as st
from Llama.llama_zero_shot import llama_zero_shot_app
from Llama.llama_one_shot import llama_one_shot_app
from GPT.gpt3_one_shot import gpt3_one_shot_app
from GPT.gpt3_few_shot import gpt3_few_shot_app
from GPT.gpt3_zero_shot import gpt3_zero_shot_app
from GPT.gpt4_zero_shot import gpt4_zero_shot_app
from GPT.gpt4_one_shot import gpt4_one_shot_app
from GPT.gpt4_few_shot import gpt4_few_shot_app
from prompt_saver import prompts_page

# Create a sidebar for navigation
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home Page", "GPT 3.5", "GPT 4", "Llama", "Saved Prompts"])

# Define the content for each page
    if page == "Home Page":
        st.title("Welcome to LLM Interface for Databases!") 
        st.text("-------------------------------------------------------------------------------")
        st.text("-------------- A Text, Web and Social Media Analytics Lab Project -------------")
        st.text("-------------- Team members: Jessica, Sarah, Raza, Victor, Freddy -------------")
        st.text("-------------------------------------------------------------------------------")
        st.write(" ")
        st.write("Our project uses GPT and LLama to convert natural language to SQL queries to later query a DuckDB database.")
        st.write("- You can navigate to the GPT 3 page to use GPT-3.5 Turbo to generate SQL queries using both zero-shot, one-shot and few-shot prompting strategies.")
        st.write("- You can navigate to the GPT 4 page to use GPT-4 to generate SQL queries using zero-shot, one-shot and few-shot prompting strategies.")
        st.write("- You can navigate to the Llama page to use Llama 70B to generate SQL queries using both zero-shot and one-shot prompting strategies.")
        st.write("- You can navigate to the Saved Prompts page to view, add, and delete used prompts.")
        st.text("-------------------------------------------------------------------------------")
        
    elif page == "GPT 3.5":
            # Load GPT-3.5 Turbo apps for zero-shot, one-shot, and two-shot prompting
            gpt3_zero_shot_app()
            gpt3_one_shot_app()
            gpt3_few_shot_app()
    elif page == "GPT 4":
            # Load GPT-4 apps for zero-shot, one-shot, and two-shot prompting
            gpt4_zero_shot_app()
            gpt4_one_shot_app()
            gpt4_few_shot_app()
    elif page == "Llama":
            # Load Llama apps for zero-shot and one-shot prompting
            llama_zero_shot_app()
            llama_one_shot_app()
    elif page == "Saved Prompts":
            # Load the Saved Prompts page
            prompts_page()

if __name__ == "__main__":
    main()