import openai
import streamlit as st
import duckdb
import os
from dotenv import dotenv_values
import json

# Load API key from environment variables
config = dotenv_values(".env")
api_key = config['OPENAI_API_KEY']
if not api_key:
    st.error("OpenAI API key not found. Please set it in your environment variables.")
    st.stop()

# Path to prompts file
PROMPTS_FILE = 'prompts.json'

# Dictionary containing metadata about each table in the database, including the purpose of each table and descriptions of columns
additional_info = {
    "papers": {
        "purpose": "Master Data of all papers in our database. One row is one paper.",
        "columns": {
            "article_id": "unique identifier for an article; used in many other tables as well; can be used for joining data with data from other tables",
            "citekey": "Some tables only have a citekey and no article_id, then you can use the citeley to join the tables (stays the same though different runs)",
            "abstract": "text paragraph with the complete abstract of a research article",
            "journal_akronym": "abbreviation of the journal name",
            "citation_count": "how often was the paper cited from papers in our database",
        }
    },
    "sentences": {
        "purpose": "All individual sentences of every paper in the database. one row is one sentence.",
        "columns": {
            "article_id": "can be used for joining with other tables",
            "sentence_id": "unique sentence_id for each individual sentence",
            "section_id": "Can be used to join with section table to get the name of the section name",
            "last_section_title": "section name",
            "last_subsection_title": "subsection name",
            "section_nr": "section counter for each article (starts with 0 (or 1) for each article)",
            "para_id": "can be used to join with paragraph table",
            "sentence_type": "refers to different sections in the paper (abstract, etc.) but is not as detailed as last_section_title",
            "sentence_original": "The text of the sentence",
        }
    },
    "paragraphs": {
        "purpose": "All individual paragraphs of every paper in the database. one row is one paragraph. one paragraph can have multiple sentences.",
        "columns": {
            "para_id": "unique para_id for each individual paragraph"
        }
    },
    "entities": {
        "purpose": "All individual entities from the ontology that we found in any paper of the database entity (see column 'entity', not 'ent_id'). One row is one appearance of an entity in an article. If 'survey' appears multiple times in a paper, we get multiple rows.",
        "columns": {
            "ent_id": "the ent_id from an entity in the IS Ontology, see",
            "entity": "The synonym that was used in a text (not the direct name of an ent_id, but a synonym for an ent_id - see table synonyms), e.g. entity='platform strategy', ent_id='digital platform'",
            "sentence": "modified sentence where we replaced acronyms with the full name"
        }
    },
    "ontology": {
        "purpose": "All individual ent_ids from the IS Ontology. one row is for one ent_id",
        "columns": {
            "ent_id": "that is a unique entity (key term) in the IS Ontology, e.g., survey, case study, etc.",
            "definition": "definition for an ent_id (generated with GPT 4)",
            "label": "top level descriptions of an ontology branch"
        }
    },
    "citations": {
        "purpose": "All individual citations from our database. If an author of an article cites another paper somewhere in the text, we create an entry in this table. one row is one individual citation",
        "columns": {
            "reference_citekey": "what article is cited? This is the citekey in table sources",
            "paper_citekey": "links to table papers"
        }
    },
    "sources": {
        "purpose": "All individual sources that come from the reference section of papers in our database. one row is one source",
        "columns": {
            "citekey": "the reference_citekey from table citations",
            "para_id": "unique para_id for each individual paragraph"
        }
    },
    "authors": {
        "purpose": "All authors of the papers in the database. One row is one author",
        "columns": {
            "author_position": "the position of the author in the author list",
            "full_name": "full name of the author",
            "institutions": "institution of the author",
        }
    },
    "keywords": {
        "purpose": "All individual keywords from the papers in the database. One row is one keyword",
        "columns": {
            "article_id": "the article_id which maps to table papers",
            "keyword": "the keyword"
        }
    },
    "subsections": {
        "purpose": "All individual subsections of every paper in the database. One row is one subsection.",
        "columns": {
            "section_id": "unique section_id for each individual section",
            "section_nr": "section counter for each article (starts with 0 (or 1) for each article)",
            "section_title": "title of the section",
            "subsection_title": "title of the subsection"
        }
    },
    "synonyms": {
        "purpose": "All synonyms for the ent_ids in the IS Ontology. One row is one synonym.",
        "columns": {
            "ent_id": "the ent_id from the IS Ontology",
            "synonym": "a synonym for an ent_id"
        }
    }
}

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

# Main function to handle user input, generate SQL queries, execute them, and display results
def gpt3_zero_shot_app():
    if not api_key:
        st.error("OpenAI API key not found. Please set it in the .env file.")
    else:
        # Establish a connection to the DuckDB database
        conn = duckdb.connect(database='isrecon_all.duckdb')
        current_schema = conn.execute("SELECT current_schema()").fetchone()
        client = openai.OpenAI(api_key=api_key)

        # Function to fetch schema information from the database
        def fetch_schema_info():
            try:
                tables = conn.execute("SHOW TABLES").fetchall()
                schema_info = {}
                for table in tables:
                    table_name = table[0]
                    columns = conn.execute(f"DESCRIBE {table_name}").fetchall()
                    schema_info[table_name] = {
                        "columns": {column[0]: "" for column in columns}
                    }
                    if table_name in additional_info:
                        schema_info[table_name]["purpose"] = additional_info[table_name].get("purpose", "No purpose available")
                        schema_info[table_name]["columns"].update(additional_info[table_name].get("columns", {}))
                return schema_info
            except Exception as e:
                st.error(f"Error fetching schema information: {e}")
                return None

        schema_info = fetch_schema_info()
        st.title("Natural Language to SQL Query Transformer using GPT-3.5 Turbo")
        st.text("-------------------------------------------------------------------------------")
        st.subheader("Zero-Shot: Convert natural language to SQL queries with zero-shot prompting")

        # User input for generating SQL query
        query = st.text_area('Enter your text to generate SQL query', '', key='gpt3.5_zero_shot_query')

        # Combine schema information with the user prompt to create an enhanced prompt for the LLM
        def generate_sql(prompt, schema_info):
            schema_info_str = "\n".join(
                [f"Table '{table}': Purpose: {info.get('purpose', 'N/A')}\nColumns: {', '.join([f'{col}: {desc}' for col, desc in info['columns'].items()])}" 
                for table, info in schema_info.items()])
            enhanced_prompt = f"""
                    {schema_info_str}\n\n
                    You have been given the schema of a DuckDB database. 
                    Generate a SQL query to this statement: {prompt}.
                    Consider all possible ways within the database tables to get the correct answer from.
                    You are allowed to use multiple tables in the SQL query.
                    Do not include any non SQL related characters."""
            
            # Generate SQL query using the GPT-3.5 model
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "You are an SQL expert."}, {"role": "user", "content": enhanced_prompt}],
                max_tokens=500,
                temperature=0,
                stop=["#", ";"]
            )
            sql_query = response.choices[0].message.content.strip()
            sql_start = sql_query.lower().find("select")
            if sql_start != -1:
                sql_query = sql_query[sql_start:]
            sql_query = sql_query.strip()
            sql_query = sql_query.replace("\n", " ")
            sql_query = sql_query.replace("`", "")

            # List of keywords to insert line breaks
            keywords = [" FROM ", " WHERE "," JOIN ", " INNER JOIN ", " LEFT JOIN ", " RIGHT JOIN ", " ON ", " AND ", " OR ", " GROUP BY ", " ORDER BY ", " LIMIT "]
            for keyword in keywords:
                sql_query = sql_query.replace(keyword, f"\n{keyword.strip()} ")

            return sql_query

            # Execute the generated SQL query on the DuckDB database
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

            # Function to generate a summary of the SQL query results  
        def summarize_results(results):
            if isinstance(results, str):
                return f"Error while executing the query: {results}"
            
            # Initialize an empty summary string
            summary = "\n\n"
            # Create a prompt for the summarry based on the SQL query results
            content_summary_prompt = f"Provide a detailed summary of the following data:\n\n{results.to_string(index=False)}"
            
            # Generate a summary using the GPT-3.5 model
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a summarization expert."},
                    {"role": "user", "content": content_summary_prompt}
                ],
                max_tokens=300,
                stop=["#", ";"]
            )

            # Extract the content of the summary from the response
            content_summary = response.choices[0].message.content.strip()
            
            # Append the generated summary to the summary string
            summary += f"\n\n{content_summary}"
            return summary

            # Button to trigger the SQL generation and execution process
        if st.button('Generate SQL query', key='gpt3.5_zero_shot_generate'):
            if len(query) > 0:
                prompts = load_prompts()
                sql_query = generate_sql(query, schema_info)
                result = execute_sql(sql_query)
                summary = summarize_results(result)

                new_entry = {
                    "prompt": query,
                    "sql_query": sql_query,
                    "results": result.to_dict() if not isinstance(result, str) else result,
                    "summary": summary
                }

                prompts["gpt3.5_zero_shot"].append(new_entry)
                save_prompts(prompts)

                st.write("Generated SQL Query:")
                st.code(sql_query, language='sql')
                
                st.subheader("GPT 3.5 Zero-Shot: Query Results")
                if isinstance(result, str):
                    st.error(result)
                else:
                    if result.empty:
                        st.warning("No results found.")
                    else:
                        st.dataframe(result)
                        st.subheader("GPT 3.5 Zero-Shot: Summary of Results")
                        st.write(summary)

# Main function to run the Streamlit app
def main():
    gpt3_zero_shot_app()

if __name__ == "__main__":
    main()
