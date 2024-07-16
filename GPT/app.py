import openai
import streamlit as st
import duckdb
from dotenv import load_dotenv
import os

# Load environment variables from the .env file located at the specified path
env_path = "C:/Users/Vic/LLM-interface/.env"
load_dotenv(dotenv_path=env_path)

# Get the OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Column explanations
column_explanations = {
    "journal_akronym": "The acronym of the journal in which the paper was published.",
    "article_id": "A unique identifier for each article.",
    "citekey": "A citation key used to reference the article.",
    "abstract": "A brief summary of the article.",
    "journal_akronym": "The acronym of the journal where the article was published.",
    "citation_count": "The number of times the article has been cited by other papers.",
    "sentence_id": "A unique identifier for each sentence in the article.",
    "section_id": "A unique identifier for each section in the article.",
    "sentence_original": "The original text of the sentence.",
    # Add more explanations as needed
}

if not api_key:
    st.error("OpenAI API key not found. Please set it in the .env file.")
else:
    # Initialize the OpenAI client
    client = openai.OpenAI(api_key=api_key)

    st.title("LLM Interface for Databases")
    st.text("Team members: Jessica, Sarah, Raza, Viktor, Freddy ")

    subheader_css = """
    <style>
        .st-eb {
            font-size: 16px;
        }
    </style>
    """
    st.markdown(subheader_css, unsafe_allow_html=True)

    st.text("-------------------------------------------------------------------------------")
    st.text("--- A Text, Web and Social Media Analytics Lab Project ---")
    st.text("-------------------------------------------------------------------------------")

    st.subheader("Part 1: Convert natural language to SQL queries")

    page_bg_css = """
    <style>
        body {
            background-color: #7F00FF;
        }
    </style>
    """
    st.markdown(page_bg_css, unsafe_allow_html=True)

    query = st.text_area('Enter your text to generate SQL query', '')

    def generate_sql(query):
        prompt = (
            f"You are an SQL expert. Translate the following natural language query to a syntactically correct SQL query, "
            f"using the given schema. Ensure that the correct types of fields and functions are used:\n"
            f"Schema:\n"
            f"Table Papers: article_id (INTEGER), citekey (TEXT), abstract (TEXT), journal_akronym (TEXT), citation_count (INTEGER)\n"
            f"Table Sentences: article_id (INTEGER), sentence_id (INTEGER), section_id (INTEGER), last_section_title (TEXT), last_subsection_title (TEXT), section_nr (INTEGER), "
            f"para_id (INTEGER), sentence_type (TEXT), sentence_original (TEXT)\n"
            f"Table Paragraphs: para_id (INTEGER)\n"
            f"Table Entities: ent_id (INTEGER), entity (TEXT), sentence (TEXT)\n"
            f"Table Ontology: ent_id (INTEGER), definition (TEXT), label (TEXT)\n"
            f"Table Citations: citekey (TEXT), reference_citekey (TEXT), paper_citekey (TEXT)\n"
            f"Table Sources: citekey (TEXT), para_id (INTEGER)\n\n"
            f"Query:\n"
            f"{query}\n"
            f"SQL:"
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are an SQL expert."}, {"role": "user", "content": prompt}],
            max_tokens=150,
            stop=["#", ";"]
        )
        sql_query = response.choices[0].message.content.strip()
        sql_start = sql_query.lower().find("select")
        if sql_start != -1:
            sql_query = sql_query[sql_start:]
        return sql_query

    def clean_sql_query(sql_query):
        sql_query = sql_query.strip()
        sql_query = sql_query.replace("\n", " ")
        sql_query = sql_query.replace("`", "")
        return sql_query

    def execute_sql(sql_query):
        conn = duckdb.connect(database=r'C:\Users\Vic\LLM-interface\GPT\isrecon_AIS11_vs_2.duckdb')
        try:
            result_df = conn.execute(sql_query).fetchdf()
            return result_df
        except duckdb.CatalogException as e:
            return f"Catalog error: {e}"
        except duckdb.ParserException as e:
            return f"Syntax error in SQL query: {e}"
        except duckdb.BinderException as e:
            return f"Binder error: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"
        finally:
            conn.close()

    def summarize_results(results):
        summary = "The query results provide the following information:\n\n"
        summary += "Columns:\n"
        
        # Describe each column
        for column in results.columns:
            explanation = column_explanations.get(column, "No explanation available.")
            summary += f"- **{column}**: {explanation}\n"
        
        # Summarize the content
        content_summary_prompt = f"Provide a detailed summary of the following data:\n\n{results.to_string(index=False)}"
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a summarization expert."},
                {"role": "user", "content": content_summary_prompt}
            ],
            max_tokens=300,
            stop=["#", ";"]
        )
        content_summary = response.choices[0].message.content.strip()
        
        summary += f"\nDetailed Summary:\n{content_summary}"
        return summary

    if st.button('Generate SQL query'):
        if len(query) > 0:
            sql_query = generate_sql(query)
            st.write("Generated SQL Query:")
            st.code(sql_query, language='sql')
            
            cleaned_sql_query = clean_sql_query(sql_query)
            st.write("Cleaned SQL Query:")
            st.code(cleaned_sql_query, language='sql')
            
            st.subheader("Part 2: Query Results")
            st.write(f"Executing SQL Query: {cleaned_sql_query}")
            result = execute_sql(cleaned_sql_query)
            if isinstance(result, str):
                st.error(result)
            else:
                if result.empty:
                    st.warning("No results found.")
                else:
                    st.dataframe(result)
                    summary = summarize_results(result)
                    st.subheader("Summary of Results")
                    st.write(summary)