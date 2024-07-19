from groq import Groq
from dotenv import dotenv_values
import duckdb
import streamlit as st

# Setting up credentials to LLama 
config = dotenv_values("/Users/muhammadraza/Documents/GitHub/LLM_interface/.env")
api_key = config['GROQ_API_KEY']

# Setting up the connection to the database with main as the schema
conn = duckdb.connect(database='isrecon_all.duckdb')
current_schema = conn.execute("SELECT current_schema()").fetchone()

groq = Groq(api_key=api_key)

# Function to fetch schema information
def fetch_schema_info():
    tables = conn.execute("SHOW TABLES").fetchall()
    schema_info = {}
    for table in tables:
        table_name = table[0]
        columns = conn.execute(f"DESCRIBE main.{table_name}").fetchall()
        schema_info[table_name] = [column[0] for column in columns]
    return schema_info

schema_info = fetch_schema_info()

def generate_sql(prompt, schema_info):
    schema_info_str = "\n".join([f"Table '{table}': columns {', '.join(columns)}" for table, columns in schema_info.items()])
    enhanced_prompt = f"{schema_info_str}\n\nGenerate a SQL query to {prompt}, and do not include any non SQL related characters."

    completion = groq.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {
                "role": "user",
                "content": enhanced_prompt
            }
        ],
        temperature=0,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    sql_query = ""
    for chunk in completion:
        sql_query += chunk.choices[0].delta.content or ""
    
    sql_query = sql_query.replace("```", "").strip()
    
    # Remove any non-SQL preamble
    lines = sql_query.split('\n')
    for i, line in enumerate(lines):
        if "SELECT" in line.upper():
            sql_query = "\n".join(lines[i:])
            break
    
    return sql_query

def execute_sql(sql_query):
    try:
        result = conn.execute(sql_query).fetchall()
        return result
    except Exception as e:
        return str(e)
    
def prompt_to_sql_execution(base_prompt, user_input, schema_info):
    full_prompt = f"{base_prompt} {user_input}"
    sql_query = generate_sql(full_prompt, schema_info)
    print(f"Generated SQL: {sql_query}")
    result = execute_sql(sql_query)
    return sql_query, result

def llama_page():
    st.title("Natural Language to SQL Query Transformer using LLama")
    st.text("-------------------------------------------------------------------------------")

    base_prompt = "Generate a SQL query to of the following input. Only generate SQL query."

    user_input = st.text_area("Describe what you want to do:", "")

    if st.button("Generate and Execute SQL Query"):
        if user_input:
            sql_query, result = prompt_to_sql_execution(base_prompt, user_input, schema_info)
            st.write(f"Generated SQL Query:")
            st.code(sql_query, language="sql")
            st.write(f"Query Result:")
            if isinstance(result, str):
                st.write(result)  # If result is an error message
            else:
                if len(result) > 0:
                    st.dataframe(result)
                else:
                    st.write("No results found.")
        else:
            st.write("Please enter a query description.")
