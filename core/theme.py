import streamlit as st
import json



class Theme:

    @staticmethod
    def load(self):

        with open("cfg/theme.json", "r") as f:
            return json.load(f)
    

    @staticmethod
    def apply(self):

        theme = self.load()

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