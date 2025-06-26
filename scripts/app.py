import streamlit as st
from data_loader import load_data, DataAnalyzer
from asp_loader import load_asp_file
from dashboard_ui import Dashboard
from cumulative_ui import render_cumulative_tabulation

def main():
    st.set_page_config(page_title="Impact KPI Dashboard", layout="wide", initial_sidebar_state="expanded")

    st.markdown("<h1 style='text-align: center;'>Impact KPI Dashboard</h1>", unsafe_allow_html=True)

    # File Uploaders
    uploaded_delivery = st.sidebar.file_uploader("Upload Delivery Details Excel File", type=["xlsx"])
    uploaded_planner = st.sidebar.file_uploader("Upload Annual Session Planner", type=["xlsx"])

    delivery_data = None
    planner_data = None
    analyzer = None

    if uploaded_delivery:
        delivery_data = load_data(uploaded_delivery)
        analyzer = DataAnalyzer(delivery_data)
        delivery_data = analyzer.remove_duplicates()

    if uploaded_planner:
        planner_data = load_asp_file(uploaded_planner)

    # Navigation Buttons
    nav_col1, nav_col2 = st.columns([1, 1])
    with nav_col1:
        delivery_btn = st.button("Delivery Dashboard")
    with nav_col2:
        cumulative_btn = st.button("Cumulative Report")

    # Track navigation state
    if 'nav_page' not in st.session_state:
        st.session_state['nav_page'] = 'delivery'

    if delivery_btn:
        st.session_state['nav_page'] = 'delivery'
    elif cumulative_btn:
        st.session_state['nav_page'] = 'cumulative'

    nav_option = st.session_state['nav_page']

    # Page Rendering
    if nav_option == "delivery" and delivery_data is not None:
        Dashboard(delivery_data, analyzer, asp_df=planner_data).render()
    elif nav_option == "cumulative":
        if planner_data is not None and delivery_data is not None:
            render_cumulative_tabulation(planner_data, delivery_data)
        else:
            st.warning("Please upload both Delivery Details and Annual Session Planner to view the Cumulative Report.")

if __name__ == "__main__":
    main()
