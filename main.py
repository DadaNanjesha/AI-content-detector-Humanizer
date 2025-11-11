# main.py
import streamlit as st
from pages.ai_detection import show_pdf_detection_page
from pages.humanize_text import show_humanize_page

def main():
    st.set_page_config(page_title="Multi-Page App: PDF & Text Humanizer",
                       layout="wide", initial_sidebar_state="collapsed")

    # Initialize the current page in session_state if not present
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Main"

    # Display the chosen page
    if st.session_state["current_page"] == "PDF Detection & Annotation":
        show_pdf_detection_page()
    elif st.session_state["current_page"] == "Humanize AI Text":
        show_humanize_page()
    else:
        show_main_page()


def show_main_page():
    st.title("📊 AI Content Detector & Humanizer")
    st.markdown("---")

    st.markdown("""
    ## Welcome to the AI Text Tools Suite!
    
    This application provides two powerful tools to help you work with AI-generated content:
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔍 PDF Detection & Annotation")
        st.markdown("""
        - **Upload PDF documents** and analyze AI-generated content
        - **Classify each sentence** as AI-written or human-written
        - **Download annotated PDFs** with color-coded highlighting
        - **Visualize detection results** with interactive charts
        """)

        if st.button("Go to PDF Detection →", type="primary", use_container_width=True):
            st.session_state["current_page"] = "PDF Detection & Annotation"
            st.rerun()

    with col2:
        st.subheader("✍️ Humanize AI Text")
        st.markdown("""
        - **Transform AI-generated text** into natural human-like content
        - **Improve readability** and flow of your text
        - **Maintain original meaning** while enhancing style
        - **Support for various content types** (articles, emails, reports)
        """)

        if st.button("Go to Text Humanizer →", type="primary", use_container_width=True):
            st.session_state["current_page"] = "Humanize AI Text"
            st.rerun()

    st.markdown("---")
    st.markdown("""
    ### How to Get Started:
    1. Choose one of the tools above based on your needs
    2. Upload your PDF document or paste your AI-generated text
    3. Let our AI algorithms process your content
    4. Download or copy the enhanced results
    
    **Note**: All processing happens securely in your browser - your data remains private.
    """)

if __name__ == "__main__":
    main()
