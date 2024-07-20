import streamlit as st
import json
import os
import pandas as pd

PROMPTS_FILE = 'prompts.json'

def load_prompts():
    if os.path.exists(PROMPTS_FILE):
        with open(PROMPTS_FILE, 'r') as f:
            return json.load(f)
    return {"llama": [], "chatgpt": [], "simple_gpt": []}

def save_prompts(prompts):
    with open(PROMPTS_FILE, 'w') as f:
        json.dump(prompts, f, indent=4)

def display_results(results):
    """Display results as a table if possible."""
    if isinstance(results, dict):
        df = pd.DataFrame(results)
        st.dataframe(df)
    else:
        st.write(results)

def prompt_saver_page():
    st.title("Prompt Saver")

    # Load prompts
    prompts = load_prompts()
    
    st.subheader("Saved Prompts")
    
    if st.button('Refresh'):
        prompts = load_prompts()
    
    # Display prompts for each category
    for category, prompt_list in prompts.items():
        st.subheader(f"{category.capitalize()} Prompts")
        if not prompt_list:
            st.write("No prompts saved.")
        else:
            for idx, item in enumerate(prompt_list):
                if isinstance(item, str):  # For categories with only strings
                    st.write(f"{idx + 1}. {item}")
                elif isinstance(item, dict):  # For categories with prompts and queries
                    st.write(f"{idx + 1}.")
                    st.write(f"**Prompt:** {item.get('prompt', 'N/A')}")
                    st.write(f"**SQL Query:** {item.get('sql_query', 'N/A')}")
                    st.write(f"**Results:**")
                    results = item.get('results', 'No results')
                    display_results(results)
                    st.write(f"**Summary:** {item.get('summary', 'N/A')}")
    
    # Clear all prompts functionality without confirmation
    if st.button('Clear All Prompts'):
        prompts = {"llama": [], "chatgpt": [], "simple_gpt": []}
        save_prompts(prompts)
        st.success("All prompts cleared.")

    # Optionally, you might want to add functionality to delete individual prompts by number
    if st.checkbox("Enable individual prompt deletion by number"):
        category = st.selectbox("Select category to delete from", list(prompts.keys()))
        if prompts[category]:
            prompt_indices = list(range(len(prompts[category])))
            prompt_to_delete_index = st.selectbox("Select prompt number to delete", prompt_indices, format_func=lambda x: f"Prompt {x + 1}")
            if st.button("Delete Selected Prompt"):
                prompts[category].pop(prompt_to_delete_index)
                save_prompts(prompts)
                st.success("Prompt deleted.")
        else:
            st.write("No prompts to delete.")

if __name__ == "__main__":
    prompt_saver_page()
