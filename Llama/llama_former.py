from groq import Groq
import streamlit as st
import duckdb
from dotenv import dotenv_values
import os
import json

# Load environment variables
config = dotenv_values(".env")
api_key = config.get('GROQ_API_KEY', '')

# File paths
PROMPTS_FILE = 'prompts.json'

# Additional information about tables
additional_info = {
    "papers": {
        "purpose": "Master Data of all papers in our database. One row is one paper.",
        "columns": {
            "article_id": "unique identifier for an article; used in many other tables as well; can be used for joining data with data from other tables",
            "citekey": """Some tables only have a citekey and no article_id, then you can use the citeley to join the tables 
                (stays the same though different runs)""",
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
        "purpose": """All individual entities from the ontology that we found in any paper of the database entity (see column 'entity', not 'ent_id'). 
                    One row is one appearance of an entity in an article. 
                    If 'survey' appears multiple times in a paper, we get multiple rows.""",
        "columns": {
            "ent_id": "the ent_id from an entity in the IS Ontology, see",
            "entity": """The synonym that was used in a text (not the direct name of an ent_id, but a synonym for an ent_id - see table synonyms),
                 e.g. entity='platform strategy', ent_id='digital platform'""",
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
        "purpose": """All individual citations from our database. If an author of an article cites another paper somewhere in the text, we create an entry in this table.
                    one row is one individual citation""",
        "columns": {
            "reference_citekey": "what article is cited? This is the citekey in table sources",
            "paper_citekey": "links to table papers"
        }
    },
    "sources": {
        "purpose": """All individual sources that come from the reference section of papers in our database. one row is one source""",
        "columns": {
            "citekey": "the reference_citekey from table citations",
            "para_id": "unique para_id for each individual paragraph"
        }
    }
}

def load_prompts():
    """Load prompts from a JSON file."""
    if os.path.exists(PROMPTS_FILE):
        with open(PROMPTS_FILE, 'r') as f:
            return json.load(f)
    return {"llama": [], "chatgpt": [], "simple_gpt": []}

def save_prompts(prompts):
    """Save prompts to a JSON file."""
    with open(PROMPTS_FILE, 'w') as f:
        json.dump(prompts, f, indent=4)

def llama_app():
    # Connect to DuckDB
    conn = duckdb.connect(database='isrecon_all.duckdb')
    groq = Groq(api_key=api_key)

    def fetch_schema_info():
        """Fetch schema information from the DuckDB database."""
        try:
            tables = conn.execute("SHOW TABLES").fetchall()
            schema_info = {}
            for table in tables:
                table_name = table[0]
                columns = conn.execute(f"DESCRIBE {table_name}").fetchall()
                schema_info[table_name] = {
                    "columns": {column[0]: "" for column in columns}
                }
                # Add additional info if available
                if table_name in additional_info:
                    schema_info[table_name]["purpose"] = additional_info[table_name].get("purpose", "No purpose available")
                    schema_info[table_name]["columns"].update(additional_info[table_name].get("columns", {}))
            return schema_info
        except Exception as e:
            st.error(f"Error fetching schema information: {e}")
            return None

    schema_info = fetch_schema_info()
    st.title("Natural Language to SQL Query Transformer using Llama3-70b-8192")
    st.text("-------------------------------------------------------------------------------")

    query = st.text_area('Enter your text to generate SQL query', '')

    def generate_sql(prompt, schema_info):
        """Generate SQL query using Groq."""
        schema_info_str = "\n".join(
            [f"Table '{table}': Purpose: {info.get('purpose', 'N/A')}\nColumns: {', '.join([f'{col}: {desc}' for col, desc in info['columns'].items()])}" 
             for table, info in schema_info.items()])
        enhanced_prompt = f"{schema_info_str}\n\nGenerate a SQL query to {prompt}, and do not include any non-SQL related characters. Simply output the SQL query."

        try:
            response = groq.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "user", "content": enhanced_prompt}
                ],
                temperature=0,
                max_tokens=1024,
                top_p=1,
                stream=True,
                stop=None,
            )
            sql_query = ""
            for chunk in response:
                sql_query += chunk.choices[0].delta.content or ""

            sql_query = sql_query.replace("```", "").strip()

            # Remove any non-SQL preamble
            lines = sql_query.split('\n')
            for i, line in enumerate(lines):
                if "SELECT" in line.upper():
                    sql_query = "\n".join(lines[i:])
                    break

            return sql_query
        except Exception as e:
            st.error(f"Error generating SQL query: {e}")
            return ""

    def execute_sql(sql_query):
        """Execute the SQL query and return the result."""
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
        """Summarize the query results using Groq."""
        if isinstance(results, str):
            return results  # If the result is an error message, just return it
        
        content_summary_prompt = f"Provide a detailed summary of the following data:\n\n{results.to_string(index=False)}"
        
        try:
            response = groq.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": "You are a summarization expert."},
                    {"role": "user", "content": content_summary_prompt}
                ],
                max_tokens=300,
                stop=["#", ";"]
            )
            content_summary = response.choices[0].message.content.strip()
            return f"\n\n{content_summary}"
        except Exception as e:
            st.error(f"Error summarizing results: {e}")
            return "Error summarizing results."

    if st.button('Generate SQL query'):
        if len(query) > 0:
            # Generate SQL query
            sql_query = generate_sql(query, schema_info)
            st.write("Generated SQL Query:")
            st.code(sql_query, language='sql')
            
            if sql_query:
                # Execute SQL query and summarize results
                result = execute_sql(sql_query)
                summary = summarize_results(result)
                
                # Save the prompt, SQL query, results, and summary
                prompts = load_prompts()
                new_entry = {
                    "prompt": query,
                    "sql_query": sql_query,
                    "results": result.to_dict() if not isinstance(result, str) else result,
                    "summary": summary
                }
                prompts["llama"].append(new_entry)
                save_prompts(prompts)
                
                # Display the results
                st.subheader("Part 2: Query Results")
                if isinstance(result, str):
                    st.error(result)
                else:
                    if result.empty:
                        st.warning("No results found.")
                    else:
                        st.dataframe(result)  # Display the results as an interactive table
                        st.subheader("Part 3: Summary of Results")
                        st.write(summary)
        else:
            st.write("Please enter a query description.")

if __name__ == "__main__":
    llama_app()
