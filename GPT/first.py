import openai
from dotenv import dotenv_values
import duckdb
import streamlit as st

config = dotenv_values(".env")
api_key = config['OPENAI_API_KEY']

conn = duckdb.connect(database='isrecon_all.duckdb')
current_schema = conn.execute("SELECT current_schema()").fetchone()

openai.api_key = api_key

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

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": enhanced_prompt
            }
        ],
        temperature=0,
        max_tokens=1024,
        top_p=1,
        n=1,
        stop=None,
    )

    sql_query = response['choices'][0]['message']['content'].strip().replace("```", "").strip()
    
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

def first_page():
    st.title("Natural Language to SQL Query Transformer without prompt")
    st.text("-------------------------------------------------------------------------------")
    st.subheader("Part 1: Convert natural language to SQL queries")

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

if __name__ == "__main__":
    first_page()
