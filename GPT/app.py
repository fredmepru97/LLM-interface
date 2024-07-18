import openai
import streamlit as st
import duckdb
from dotenv import load_dotenv
import os

# Load environment variables from the .env file located at the specified path
env_path = "/Users/muhammadraza/Documents/GitHub/LLM_interface/.env"
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
    conn = duckdb.connect(database='isrecon_all.duckdb')
    current_schema = conn.execute("SELECT current_schema()").fetchone()
    # Initialize the OpenAI client
    client = openai.OpenAI(api_key=api_key)

    def fetch_schema_info():
        tables = conn.execute("SHOW TABLES").fetchall()
        schema_info = {}
        for table in tables:
            table_name = table[0]
            columns = conn.execute(f"DESCRIBE main.{table_name}").fetchall()
            schema_info[table_name] = [column[0] for column in columns]
        return schema_info
    
    schema_info = fetch_schema_info()

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

    def generate_sql(prompt, schema_info):
        schema_info_str = "\n".join([f"Table '{table}': columns {', '.join(columns)}" for table, columns in schema_info.items()])
        enhanced_prompt = f"""
                {schema_info_str}\n\nGenerate a SQL query to {prompt}, alias the columns in the SELECT statement extremely precicely.
                Donot include any non SQL related characters."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are an SQL expert."}, {"role": "user", "content": enhanced_prompt}],
            max_tokens=150,
            temperature=1,
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

    def prompt_to_sql_execution(base_prompt, query, schema_info):
        full_prompt = f"{base_prompt} {query}"
        sql_query = generate_sql(full_prompt, schema_info)
        print(f"Generated SQL: {sql_query}")
        result = execute_sql(sql_query)
        return sql_query, result

    def summarize_results(results):
        summary = " \n\n"
        
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
        
        summary += f"\n\n{content_summary}"
        return summary

    if st.button('Generate SQL query'):
        if len(query) > 0:
            sql_query = generate_sql(query, schema_info)
            st.write("Generated SQL Query:")
            st.code(sql_query, language='sql')
            
            cleaned_sql_query = clean_sql_query(sql_query)
            
            st.subheader("Part 2: Query Results")
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