import streamlit as st
from src.schema_introspection import get_connection, introspect_schema, load_hints
from src.sql_generator import generate_sql_with_retry
from src.safety import validate_sql
from src.executor import execute_sql
import pandas as pd

MAX_ROWS = 1000

st.set_page_config(page_title="TalkToData", layout="wide")
st.title("TalkToData: English to SQL")

st.markdown("Ask a question in plain English and get back a SQL query + results. No SQL knowledge required.")

@st.cache_resource
def get_db():
    return get_connection()

conn = get_db()

with st.sidebar:
    st.subheader("Database Schema")
    if st.checkbox("Show schema"):
        schema_text = introspect_schema(conn)
        st.code(schema_text, language="sql")

question = st.text_input("Ask your question:", placeholder="e.g., Which carrier has the most flights?")

if question:
    with st.spinner("Generating SQL..."):
        sql = generate_sql_with_retry(question, conn)
    
    st.subheader("Generated SQL")
    st.code(sql, language="sql")
    
    is_safe, reason = validate_sql(sql)
    if not is_safe:
        st.error(f"Safety check failed: {reason}")
    else:
        with st.spinner("Executing..."):
            success, result = execute_sql(sql, conn, max_rows=MAX_ROWS)
        
        if not success:
            st.error(f"Query failed: {result}")
        else:
            st.subheader("Results")
            if result:
                df = pd.DataFrame(result)
                st.dataframe(df, use_container_width=True)
                if len(result) == MAX_ROWS:
                    st.caption(f"Showing the first {MAX_ROWS} rows.")
            else:
                st.info("Query returned no results.")

st.divider()
st.caption("Powered by Claude + MySQL. See docs/accuracy_report.txt for accuracy metrics.")
