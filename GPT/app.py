import openai
import streamlit as st
import duckdb
from dotenv import load_dotenv
import os

env_path = "C:/Users/fredd/text-project/.env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key

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

def main_app():
    if not api_key:
        st.error("OpenAI API key not found. Please set it in the .env file.")
    else:
        conn = duckdb.connect(database='isrecon_all.duckdb')
        current_schema = conn.execute("SELECT current_schema()").fetchone()

        def fetch_schema_info():
            tables = conn.execute("SHOW TABLES").fetchall()
            schema_info = {}
            for table in tables:
                table_name = table[0]
                columns = conn.execute(f"DESCRIBE main.{table_name}").fetchall()
                schema_info[table_name] = [column[0] for column in columns]
            return schema_info
        
        schema_info = fetch_schema_info()

        st.title("Natural Language to SQL Query Transformer using GPT-3.5 Turbo")
        st.text("-------------------------------------------------------------------------------")
        subheader_css = """
        <style>
            .st-eb {
                font-size: 16px;
            }
        </style>
        """
        st.markdown(subheader_css, unsafe_allow_html=True)

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
                    Do not include any non SQL related characters."""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "You are an SQL expert."}, {"role": "user", "content": enhanced_prompt}],
                max_tokens=150,
                temperature=1,
                stop=["#", ";"]
            )
            sql_query = response.choices[0].message['content'].strip()
            sql_start = sql_query.lower().find("select")
            if sql_start != -1:
                sql_query = sql_query[sql_start:]
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

        def summarize_results(results, base_prompt, query):
            summary = " \n\n"
            full_prompt = f"{base_prompt} {query}"
            # Summarize the content
            content_summary_prompt = f"""You have the results:\n\n{results.to_string(index=False)} to the {full_prompt} query which were
                                    generated via a DuckDB database, please tell me how these results compare to what you know about this certain topic
                                    without this additional information. Be mindful when writing your response and consider what was asked for in the
                                    prompt, if it is asking for quantitaive data just give a short sentence summarizing the results. If qualitative
                                    data is what is being asked, give a summary of the provided data. Limit your  response to 300 characters if qualitative 
                                    and one sentence if quantitative."""
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a summarization expert."},
                    {"role": "user", "content": content_summary_prompt}
                ],
                max_tokens=300,
                stop=["#", ";"]
            )
            content_summary = response.choices[0].message['content'].strip()
            
            summary += f"\n\n{content_summary}"
            return summary

        base_prompt = "Generate a SQL query to of the following input. Only generate SQL query."
        if st.button('Generate SQL query'):
            if len(query) > 0:
                sql_query, result = prompt_to_sql_execution(base_prompt, query, schema_info)
                st.write("Generated SQL Query:")
                st.code(sql_query, language='sql')
                
                st.subheader("Part 2: Query Results")
                if isinstance(result, str):
                    st.error(result)
                else:
                    if result.empty:
                        st.warning("No results found.")
                    else:
                        st.dataframe(result)
                        summary = summarize_results(result, base_prompt, query)
                        st.subheader("Part 3: Summary of Results")
                        st.write(summary)
