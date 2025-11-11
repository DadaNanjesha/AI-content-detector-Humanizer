# pages/pdf_detection.py
import streamlit as st
import pandas as pd
import altair as alt
from utils.pdf_utils import extract_text_from_pdf, generate_annotated_pdf, word_count
from utils.ai_detection_utils import classify_text_hf  # Defined in utils/ai_detection_utils.py
from io import BytesIO

def show_pdf_detection_page():
    # Navigation buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Back to Main", type="secondary"):
            st.session_state["current_page"] = "Main"
            st.rerun()
    with col2:
        if st.button("Switch to Humanize AI Text →", type="secondary"):
            st.session_state["current_page"] = "Humanize AI Text"
            st.rerun()

    st.title("🔍 PDF AI Content Detector & Annotator")

    st.markdown("""
    ### Transform Your PDF Analysis with AI-Powered Detection
    
    Upload any PDF document to automatically analyze and classify each sentence by its origin. 
    Our advanced AI detection system identifies whether text was written by humans, AI, or a combination of both, 
    providing you with clear, actionable insights about your document's authenticity.
    """)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        #### 📤 **Upload & Extract**
        - **Support for any PDF** - academic papers, reports, articles, documents
        - **Smart text extraction** - preserves formatting and structure
        - **Secure processing** - your files never leave your session
        - **200MB file limit** - handles most professional documents
        """)

    with col2:
        st.markdown("""
        #### 🤖 **AI Analysis & Classification**
        - **Sentence-level detection** - precise analysis of every sentence
        - **Four classification categories**:
          - 🟢 **Human-written** - Original human content
          - 🔵 **Human-written & AI-refined** - Human content with AI enhancement
          - 🟠 **AI-generated & AI-refined** - AI content with human editing
          - 🔴 **AI-generated** - Pure AI-generated text
        - **Real-time processing** - fast, accurate results
        """)

    with col3:
        st.markdown("""
        #### 📊 **Visualize & Download**
        - **Color-coded PDF annotations** - instant visual understanding
        - **Interactive charts** - see the distribution at a glance
        - **Detailed breakdown** - percentage analysis by category
        - **Download ready** - get your annotated PDF immediately
        """)

    st.markdown("---")

    st.markdown("""
    ### 🎯 **Perfect For:**
    - **Academic researchers** verifying paper authenticity
    - **Content managers** ensuring original content
    - **Educators** checking student submissions
    - **Publishers** maintaining content standards
    - **Business professionals** validating reports and documentation
    """)

    st.info("💡 **Pro Tip**: For best results, upload clean PDFs with selectable text. Scanned documents may require OCR processing first.")
    
    # Initialize session state keys if not present
    if "classification_map" not in st.session_state:
        st.session_state["classification_map"] = None
    if "percentages" not in st.session_state:
        st.session_state["percentages"] = None
    if "annotated_pdf" not in st.session_state:
        st.session_state["annotated_pdf"] = None
    if "original_pdf_text" not in st.session_state:
        st.session_state["original_pdf_text"] = ""
    if "pdf_processed" not in st.session_state:
        st.session_state["pdf_processed"] = False
    if "current_pdf_name" not in st.session_state:
        st.session_state["current_pdf_name"] = None

    st.subheader("📁 Upload Your PDF Document")
    uploaded_pdf = st.file_uploader("Choose a PDF file", type=[
                                    "pdf"], label_visibility="collapsed")
    st.caption("Drag and drop file here • Limit 200MB per file • PDF format only")

    # Reset processing state if a new file is uploaded
    if uploaded_pdf and not st.session_state.get("current_pdf_name") == uploaded_pdf.name:
        st.session_state["pdf_processed"] = False
        st.session_state["current_pdf_name"] = uploaded_pdf.name
        # Clear previous results
        st.session_state["classification_map"] = None
        st.session_state["percentages"] = None
        st.session_state["annotated_pdf"] = None
        st.session_state["original_pdf_text"] = ""

    if uploaded_pdf:
        # Only process if not already processed
        if not st.session_state["pdf_processed"]:
            pdf_bytes = uploaded_pdf.read()
            with st.spinner("📄 Extracting text from PDF..."):
                extracted = extract_text_from_pdf(pdf_bytes)
                st.session_state["original_pdf_text"] = extracted

            if not st.session_state["original_pdf_text"].strip():
                st.error(
                    "❌ No text could be extracted from this PDF. Please ensure it contains selectable text.")
                st.session_state["pdf_processed"] = False
                return

            with st.spinner("🤖 Analyzing content with AI detection..."):
                c_map, pcts = classify_text_hf(
                    st.session_state["original_pdf_text"])
                st.session_state["classification_map"] = c_map
                st.session_state["percentages"] = pcts

            with st.spinner("🎨 Generating annotated PDF..."):
                annotated = generate_annotated_pdf(
                    pdf_bytes, st.session_state["classification_map"])
                st.session_state["annotated_pdf"] = annotated

            # Mark as processed to avoid re-running
            st.session_state["pdf_processed"] = True
            st.rerun()  # Refresh to show results without processing messages
        else:
            # If already processed, just show the results
            st.success("✅ PDF analysis completed! Results are ready below.")

        # Display classification breakdown (only show if we have results)
        if st.session_state["percentages"]:
            st.subheader("📊 Detection Results Overview")

            # Create metrics row
            col1, col2, col3, col4 = st.columns(4)
            human_content = st.session_state["percentages"].get(
                "Human-written", 0)
            human_ai_refined = st.session_state["percentages"].get(
                "Human-written & AI-refined", 0)
            ai_human_refined = st.session_state["percentages"].get(
                "AI-generated & AI-refined", 0)
            ai_content = st.session_state["percentages"].get("AI-generated", 0)

            with col1:
                st.metric(
                    "Human Content", f"{human_content:.1f}%", delta="Original", delta_color="normal")
            with col2:
                st.metric(
                    "Human + AI", f"{human_ai_refined:.1f}%", delta="Enhanced", delta_color="off")
            with col3:
                st.metric(
                    "AI + Human", f"{ai_human_refined:.1f}%", delta="Edited", delta_color="off")
            with col4:
                st.metric("AI Content", f"{ai_content:.1f}%",
                          delta="Generated", delta_color="inverse")

            st.markdown("#### 📈 Detailed Distribution")
            df = pd.DataFrame({
                "Category": list(st.session_state["percentages"].keys()),
                "Percentage": list(st.session_state["percentages"].values())
            })
            color_scale = alt.Scale(
                domain=["AI-generated", "AI-generated & AI-refined", "Human-written", "Human-written & AI-refined"],
                range=["#ff6666", "#ff9900", "#66CC99", "#6699FF"]
            )
            chart = (
                alt.Chart(df)
                .mark_bar()
                .encode(
                    y=alt.Y("Category:N", sort="-x", title="Content Type"),
                    x=alt.X("Percentage:Q", title="Percentage (%)", scale=alt.Scale(domain=[0, 100])),
                    color=alt.Color(
                        "Category:N", scale=color_scale, legend=None),
                    tooltip=["Category:N", "Percentage:Q"]
                )
                .properties(height=300, width=600)
            )
            st.altair_chart(chart, use_container_width=True)

            st.markdown("#### 📋 Detailed Breakdown")
            st.table(df.set_index("Category").style.format(
                {"Percentage": "{:.1f}%"}))
        
        if st.session_state["annotated_pdf"]:
            st.subheader("📥 Download Your Annotated PDF")
            st.success(
                "✅ Your analyzed PDF is ready! Download the color-coded version below.")
            st.download_button(
                "📄 Download Annotated PDF",
                data=st.session_state["annotated_pdf"],
                file_name="ai_analyzed_document.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )

            st.markdown("""
            **🎨 Color Legend in Downloaded PDF:**
            - 🟢 **Green**: Human-written content
            - 🔵 **Blue**: Human-written & AI-refined  
            - 🟠 **Orange**: AI-generated & AI-refined
            - 🔴 **Red**: AI-generated content
            """)
        
        with st.expander("🔍 View Extracted Text Analysis"):
            st.text_area("Full extracted text content",
                         st.session_state["original_pdf_text"], height=200)
            st.caption(
                "This is the raw text extracted from your PDF for analysis purposes.")
    else:
        st.info(
            "👆 **Ready to start? Upload a PDF document above to begin AI content analysis.**")
        # Reset processing state when no file is uploaded
        st.session_state["pdf_processed"] = False
        st.session_state["current_pdf_name"] = None
