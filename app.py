import streamlit as st, json


# APP CONFIG
st.set_page_config(layout="wide")

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}

[data-testid="stToolbar"] {
    display: none;
}
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.set_page_config(
    page_title="Mon App Desktop",
    page_icon="🚀",
    layout="centered"
)


with open("cfg/theme.json", "r") as f:
    theme = json.load(f)


css = f"""
<style>

.stApp {{
    background-color: {theme["background"]};
    color: {theme["text"]};
}}

.stButton > button {{
    background-color: {theme["primary"]};
    color: white;
    border-radius: 10px;
    border: none;
}}

.stButton > button:hover {{
    background-color: {theme["primaryHover"]};
}}

section[data-testid="stSidebar"] {{
    background-color: {theme["sidebar"]};
}}

</style>
"""

st.markdown(css, unsafe_allow_html=True)
