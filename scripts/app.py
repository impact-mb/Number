import streamlit as st
from data_loader import load_generic_file, DataAnalyzer
from asp_loader import load_asp_file
from dashboard_ui import Dashboard
from cumulative_ui import render_cumulative_tabulation
from delivery_insights import render_session_attendance_by_date
from map_visualization import render_india_map

def main():
    st.set_page_config(page_title="Magic Dashboard", layout="wide", initial_sidebar_state="expanded")
    st.markdown("""
        <h1 style='text-align: center;'>Magic Dashboard</h1>
        <p style='text-align: center;'>
            <a href='https://www.magicbus.org/' target='_blank'>Visit Magic Bus Website</a>
        </p>
    """, unsafe_allow_html=True)

    uploaded_planner = st.sidebar.file_uploader("Upload Annual Session Planner", type=["xlsx"])
    planner_data = None

    nav_col1, nav_col2, nav_col3 = st.columns(3)
    with nav_col1:
        delivery_btn = st.button("📒 Delivery Dashboard", type="primary")
    with nav_col2:
        cumulative_btn = st.button("📊 Cumulative Report", type="primary")
    with nav_col3:
        delivery_data_btn = st.button("📁 Delivery Data[Dump]", type="primary")

    if 'nav_page' not in st.session_state:
        st.session_state['nav_page'] = 'delivery_data'

    if delivery_btn:
        st.session_state['nav_page'] = 'delivery'
    elif cumulative_btn:
        st.session_state['nav_page'] = 'cumulative'
    elif delivery_data_btn:
        st.session_state['nav_page'] = 'delivery_data'

    nav_option = st.session_state['nav_page']

    if uploaded_planner:
        planner_data = load_asp_file(uploaded_planner)

    if nav_option == "cumulative":
        st.warning("Cumulative report requires both Delivery Details and Planner files uploaded in the Delivery Data tab.")

    elif nav_option == "delivery_data":
        st.subheader("Upload Delivery Data File (Excel/CSV, Max 10MB)")
        additional_file = st.file_uploader("Upload Excel or CSV", type=["xlsx", "csv"], key="additional_delivery")

        if additional_file:
            if additional_file.size > 10 * 1024 * 1024:
                st.error("❌ File size exceeds 10MB limit.")
            else:
                try:
                    additional_df = load_generic_file(additional_file)
                    if not additional_df.empty:
                        st.success(f"✅ File '{additional_file.name}' loaded successfully.")
                        analyzer2 = DataAnalyzer(additional_df)
                        cleaned_df = analyzer2.remove_duplicates()

                        st.markdown("### 🔍 Preview of Uploaded Delivery Data")
                        if st.checkbox("Show full dataset"):
                            st.dataframe(cleaned_df)
                        else:
                            st.dataframe(cleaned_df.head(10))

                        st.markdown("### 📊 Basic Statistics")
                        st.json({
                            "Rows": len(cleaned_df),
                            "Columns": len(cleaned_df.columns),
                            "Duplicate Records Removed": analyzer2.duplicate_count
                        })

                        render_session_attendance_by_date(cleaned_df)
                        render_india_map(cleaned_df)

                    else:
                        st.warning("The uploaded file seems empty or unsupported.")
                except Exception as e:
                    st.error(f"❌ Failed to process file: {str(e)}")
        else:
            st.warning("Please upload a Delivery Details file to begin.")


    elif nav_option == "delivery":
        st.subheader("Upload Delivery File")
        delivery_file = st.file_uploader("Upload Excel or CSV", type=["xlsx", "csv"], key="main_delivery_upload")
        if delivery_file:
            delivery_data = load_generic_file(delivery_file)
            analyzer = DataAnalyzer(delivery_data)
            cleaned_data = analyzer.remove_duplicates()
            Dashboard(cleaned_data, analyzer, asp_df=planner_data).render()

if __name__ == "__main__":
    main()