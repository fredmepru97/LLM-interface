import streamlit as st
import json
import os
import pandas as pd

PROMPTS_FILE = 'prompts.json'

def load_prompts():
    """Load prompts from a JSON file."""
    if os.path.exists(PROMPTS_FILE):
        with open(PROMPTS_FILE, 'r') as f:
            return json.load(f)
    return {"gpt3.5_zero_shot": [], "gpt3.5_one_shot": [], "gpt3.5_two_shot": [], "gpt4_zero_shot": [], "gpt4_one_shot": [], "gpt4_two_shot": [], "llama_zero_shot": [], "llama_one_shot": []}

def save_prompts(prompts):
    """Save prompts to a JSON file."""
    with open(PROMPTS_FILE, 'w') as f:
        json.dump(prompts, f, indent=4)

def display_results(results):
    """Display results as a table if possible."""
    if isinstance(results, dict):
        df = pd.DataFrame(results)
        st.dataframe(df)
    else:
        st.write(results)

def prompts_page():
    st.title("Prompt Saver")

    prompts = load_prompts()
    
    st.subheader("Saved Prompts")
    
    if st.button('Refresh'):
        prompts = load_prompts()
    
    for category, prompt_list in prompts.items():
        with st.expander(f"{category.capitalize()} Prompts", expanded=False):
            if not prompt_list:
                st.write("No prompts saved.")
            else:
                prompt_list = prompt_list[::-1]
                for idx, item in enumerate(prompt_list):
                    st.write(f"### Prompt {idx + 1}")
                    if isinstance(item, str):  
                        st.write(item)
                    elif isinstance(item, dict):  
                        st.write(f"**Prompt:** {item.get('prompt', 'N/A')}")
                        st.write(f"**SQL Query:** {item.get('sql_query', 'N/A')}")
                        st.write(f"**Results:**")
                        results = item.get('results', 'No results')
                        display_results(results)
                        st.write(f"**Summary:** {item.get('summary', 'N/A')}")

    if st.button('Clear All Prompts'):
        prompts = {"gpt3.5_zero_shot": [], "gpt3.5_one_shot": [], "gpt3.5_two_shot": [], "gpt4_zero_shot": [], "gpt4_one_shot": [], "gpt4_two_shot": [], "llama_zero_shot": [], "llama_one_shot": []}
        save_prompts(prompts)
        st.success("All prompts cleared.")

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
    prompts_page()
