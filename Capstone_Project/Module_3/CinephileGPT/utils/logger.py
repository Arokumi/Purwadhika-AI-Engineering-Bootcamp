import streamlit as st

def log(message: str):
    if "console" not in st.session_state:
        st.session_state.console = []
    st.session_state.console.append(str(message))
    print(message)
