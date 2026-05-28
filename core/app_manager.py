import streamlit as st

# from pages.login_page import LoginPage
# from pages.dashboard_page import DashboardPage


class AppManager:

    def __init__(self):

        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False

    def run(self):
        pass
        # if st.session_state.authenticated:

        #     DashboardPage().render()

        # else:

        #     LoginPage().render()