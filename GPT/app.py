import openai
import streamlit as st
import duckdb

openai.api_key = st.secrets["pass"]

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
    model_engine = "gpt-3.5-turbo"
    prompt = (
        f"You are an SQL expert. Translate the following natural language query to a syntactically correct SQL query, "
        f"using the given schema:\n"
        f"Schema:\n"
        f"Table Papers: article_id, citekey, abstract, journal_akronym, citation_count\n"
        f"Table Sentences: article_id, sentence_id, section_id, last_section_title, last_subsection_title, section_nr, "
        f"para_id, sentence_type, sentence_original\n"
        f"Table Paragraphs: para_id\n"
        f"Table Entities: ent_id, entity, sentence\n"
        f"Table Ontology: ent_id, definition, label\n"
        f"Table Citations: citekey, reference_citekey, paper_citekey\n"
        f"Table Sources: citekey, para_id\n\n"
        f"Query:\n"
        f"{query}\n"
        f"SQL:"
    )
    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=[
            {"role": "system", "content": "You are an SQL expert."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        stop=["#", ";"]
    )
    sql_query = response.choices[0].message['content'].strip()
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
    conn = duckdb.connect(database=r'C:\Users\fredd\text-project\database\isrecon_AIS11_vs_2.duckdb')
    try:
        result_df = conn.execute(sql_query).fetchdf()
        return result_df
    except duckdb.CatalogException as e:
        return f"An error occurred: {e}"
    except duckdb.ParserException as e:
        return f"Syntax error in SQL query: {e}"
    except Exception as e:
        return f"An error occurred: {e}"
    finally:
        conn.close()

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
