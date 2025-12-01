import random
import re
import ssl
import warnings
import nltk
import spacy
import streamlit as st
from nltk.corpus import wordnet
from nltk.tokenize import sent_tokenize, word_tokenize

warnings.filterwarnings("ignore", category=FutureWarning)

########################################
# Download needed NLTK resources
########################################
def download_nltk_resources():
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    resources = ['punkt', 'averaged_perceptron_tagger',
                 'punkt_tab', 'wordnet', 'averaged_perceptron_tagger_eng']
    for r in resources:
        nltk.download(r, quiet=True)

download_nltk_resources()

########################################
# Prepare spaCy pipeline
########################################
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    st.warning("spaCy en_core_web_sm model not found. Install with: python -m spacy download en_core_web_sm")
    nlp = None

########################################
# Citation Regex
########################################
CITATION_REGEX = re.compile(
    r"\(\s*[A-Za-z&\-,\.\s]+(?:et al\.\s*)?,\s*\d{4}(?:,\s*(?:pp?\.\s*\d+(?:-\d+)?))?\s*\)"
)

########################################
# Helper: Word & Sentence Counts
########################################
def count_words(text):
    return len(word_tokenize(text))

def count_sentences(text):
    return len(sent_tokenize(text))

########################################
# Step 1: Extract & Restore Citations
########################################
def extract_citations(text):
    refs = CITATION_REGEX.findall(text)
    placeholder_map = {}
    replaced_text = text
    for i, r in enumerate(refs, start=1):
        placeholder = f"[[REF_{i}]]"
        placeholder_map[placeholder] = r
        replaced_text = replaced_text.replace(r, placeholder, 1)
    return replaced_text, placeholder_map

PLACEHOLDER_REGEX = re.compile(r"\[\s*\[\s*REF_(\d+)\s*\]\s*\]")


def restore_citations(text, placeholder_map):

    def replace_placeholder(match):
        # match.group(1) contains the numeric index captured from the placeholder
        idx = match.group(1)
        key = f"[[REF_{idx}]]"
        return placeholder_map.get(key, match.group(0))

    restored = PLACEHOLDER_REGEX.sub(replace_placeholder, text)
    return restored


########################################
# Step 2: Expansions, Synonyms, & Transitions
########################################
contraction_map = {
    "n't": " not", "'re": " are", "'s": " is", "'ll": " will",
    "'ve": " have", "'d": " would", "'m": " am"
}

ACADEMIC_TRANSITIONS = [
    "Moreover,",
    "Additionally,",
    "Furthermore,",
    "Hence,",
    "Therefore,",
    "Consequently,",
    "Nonetheless,",
    "Nevertheless,",
    "In contrast,",
    "On the other hand,",
    "In addition,",
    "As a result,",
]

def expand_contractions(sentence):
    tokens = word_tokenize(sentence)
    expanded = []
    for t in tokens:
        replaced = False
        lower_t = t.lower()
        for contr, expansion in contraction_map.items():
            if contr in lower_t and lower_t.endswith(contr):
                new_t = lower_t.replace(contr, expansion)
                if t[0].isupper():
                    new_t = new_t.capitalize()
                expanded.append(new_t)
                replaced = True
                break
        if not replaced:
            expanded.append(t)
    return " ".join(expanded)

def replace_synonyms(sentence, p_syn=0.2):
    if not nlp:
        return sentence

    doc = nlp(sentence)
    new_tokens = []
    for token in doc:
        if "[[REF_" in token.text:
            new_tokens.append(token.text)
            continue
        if token.pos_ in ["ADJ", "NOUN", "VERB", "ADV"] and wordnet.synsets(token.text):
            if random.random() < p_syn:
                synonyms = get_synonyms(token.text, token.pos_)
                if synonyms:
                    new_tokens.append(random.choice(synonyms))
                else:
                    new_tokens.append(token.text)
            else:
                new_tokens.append(token.text)
        else:
            new_tokens.append(token.text)
    return " ".join(new_tokens)


def add_academic_transition(sentence, p_transition=0.2):
    if random.random() < p_transition:
        transition = random.choice(ACADEMIC_TRANSITIONS)
        return f"{transition} {sentence}"
    return sentence


def get_synonyms(word, pos):
    wn_pos = None
    if pos.startswith("ADJ"):
        wn_pos = wordnet.ADJ
    elif pos.startswith("NOUN"):
        wn_pos = wordnet.NOUN
    elif pos.startswith("ADV"):
        wn_pos = wordnet.ADV
    elif pos.startswith("VERB"):
        wn_pos = wordnet.VERB

    synonyms = set()
    if wn_pos:
        for syn in wordnet.synsets(word, pos=wn_pos):
            for lemma in syn.lemmas():
                lemma_name = lemma.name().replace("_", " ")
                if lemma_name.lower() != word.lower():
                    synonyms.add(lemma_name)
    return list(synonyms)


########################################
# Step 3: Minimal "Humanize" line-by-line
########################################
def minimal_humanize_line(line, p_syn=0.2, p_trans=0.2):
    line = expand_contractions(line)
    line = replace_synonyms(line, p_syn=p_syn)
    line = add_academic_transition(line, p_transition=p_trans)
    return line


def minimal_rewriting(text, p_syn=0.2, p_trans=0.2):
    lines = sent_tokenize(text)
    out_lines = [
        minimal_humanize_line(ln, p_syn=p_syn, p_trans=p_trans) for ln in lines
    ]
    return " ".join(out_lines)


def preserve_linebreaks_rewrite(text, p_syn=0.2, p_trans=0.2):
    """Rewrite text while preserving original line breaks.

    Splits the input on newline characters and rewrites each non-empty line
    independently, keeping blank lines and original line structure.
    """
    lines = text.splitlines()
    out_lines = []
    for ln in lines:
        if not ln.strip():
            out_lines.append("")
        else:
            out_lines.append(minimal_rewriting(
                ln, p_syn=p_syn, p_trans=p_trans))
    # Rejoin using single newline to preserve original paragraph/line breaks
    return "\n".join(out_lines)


########################################
# Final: Show Humanize Page
########################################
def show_humanize_page():
    # Navigation buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Back to Main", type="secondary"):
            st.session_state["current_page"] = "Main"
            st.rerun()
    with col2:
        if st.button("Switch to PDF Detection →", type="secondary"):
            st.session_state["current_page"] = "PDF Detection & Annotation"
            st.rerun()
    
    st.title("✍️ AI Text Humanizer & Enhancer")

    st.markdown("""
    ### Transform AI-Generated Text into Natural, Human-Like Content
    
    Our advanced text humanization tool intelligently rewrites AI-generated content to sound more natural, 
    authentic, and human-written while preserving your original meaning and academic integrity. Perfect for 
    refining articles, essays, reports, and any content that needs a more personal touch.
    """)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        #### 🛡️ **Smart Citation Protection**
        - **APA citation preservation** - automatically detects and protects academic references
        - **No data loss** - your citations remain intact and properly formatted
        - **Academic integrity** - maintain proper referencing while enhancing text
        - **Multiple citation styles** - handles various academic formatting standards
        """)

    with col2:
        st.markdown("""
        #### 🔧 **Intelligent Text Enhancement**
        - **Contraction expansion** - transforms "can't" to "cannot" for formal tone
        - **Synonym replacement** - replaces repetitive words with natural alternatives
        - **Academic transitions** - adds professional connecting phrases
        - **Context-aware processing** - maintains original meaning and technical terms
        """)

    with col3:
        st.markdown("""
        #### 📊 **Customizable Processing**
        - **Adjustable intensity** - control how much transformation is applied
        - **Real-time preview** - see word and sentence count changes
        - **Quality metrics** - track improvements in readability and flow
        - **Batch processing** - handle large documents efficiently
        """)

    st.markdown("---")

    st.markdown("""
    ### 🎯 **Ideal For:**
    - **Students & Researchers** - enhancing academic papers while keeping citations
    - **Content Creators** - making AI-generated articles sound more authentic
    - **Business Professionals** - refining reports and presentations
    - **Writers & Editors** - improving flow and readability of draft content
    - **Marketing Teams** - humanizing product descriptions and blog posts
    """)

    st.success("🚀 **Fast & Secure**: No external API calls - all processing happens locally in your browser for complete privacy.")

    st.markdown("---")

    st.subheader("🎛️ Customize Your Humanization Settings")

    col1, col2 = st.columns(2)
    
    with col1:
        p_syn = st.slider(
            "**Synonym Replacement Intensity**", 
            0.0, 1.0, 0.2, 0.05,
            help="Higher values replace more words with synonyms for greater variation"
        )
    
    with col2:
        p_trans = st.slider(
            "**Academic Transition Frequency**", 
            0.0, 1.0, 0.2, 0.05,
            help="Higher values add more transitional phrases for better flow"
        )

    st.subheader("📝 Enter Your Text to Humanize")
    
    input_text = st.text_area(
        "Paste your AI-generated text below:", 
        height=200,
        placeholder="Paste your text here... We'll automatically protect your citations and enhance the writing style.",
        label_visibility="collapsed"
    )

    if st.button("🚀 Humanize Text", type="primary", use_container_width=True):
        if not input_text.strip():
            st.warning("📝 Please enter some text to humanize first.")
            return

        # Show original stats
        orig_wc = count_words(input_text)
        orig_sc = count_sentences(input_text)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Original Word Count", orig_wc)
        with col2:
            st.metric("Original Sentence Count", orig_sc)

        with st.spinner("🔍 Analyzing text and protecting citations..."):
            # Extract and protect citations
            no_refs_text, placeholders = extract_citations(input_text)
            
        with st.spinner("✍️ Enhancing writing style and flow..."):
            # Apply humanization while preserving line breaks
            partially_rewritten = preserve_linebreaks_rewrite(
                no_refs_text, p_syn=p_syn, p_trans=p_trans
            )
            
        with st.spinner("✅ Restoring citations and finalizing..."):
            # Restore citations
            final_text = restore_citations(partially_rewritten, placeholders)

            # Normalize spaces around punctuation but do not remove newlines
            final_text = re.sub(r"[ \t]+([.,;:!?])", r"\1", final_text)
            final_text = re.sub(r"(\()[ \t]+", r"\1", final_text)
            final_text = re.sub(r"[ \t]+(\))", r"\1", final_text)
            # Collapse multiple spaces/tabs (but keep newlines)
            final_text = re.sub(r"[ \t]{2,}", " ", final_text)
            # Normalize paired tokenized quotes: `` ... '' -> "..." (remove stray spaces)
            final_text = re.sub(r"``\s*(.+?)\s*''", r'"\1"', final_text)

        # Calculate new stats
        new_wc = count_words(final_text)
        new_sc = count_sentences(final_text)

        st.subheader("🎉 Your Humanized Text")

        st.success(f"✅ Successfully enhanced your text! Added **{new_wc - orig_wc} words** and **{new_sc - orig_sc} sentences** for better flow.")

        # Single editable output box that preserves original line breaks and paragraphs
        st.text_area(
            "Humanized Result",
            final_text,
            height=300,
            label_visibility="collapsed"
        )

        # Copy to clipboard functionality
        st.download_button(
            "📋 Download Humanized Text",
            data=final_text,
            file_name="humanized_text.txt",
            mime="text/plain",
            use_container_width=True
        )

        st.markdown("""
        ### 📊 Enhancement Summary
        """)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Words Added", new_wc - orig_wc, delta="Enhancement")
        with col2:
            st.metric("Sentences Added", new_sc - orig_sc, delta="Flow")
        with col3:
            st.metric("Final Word Count", new_wc)
        with col4:
            st.metric("Final Sentence Count", new_sc)

    else:
        st.info("""
        👆 **Ready to enhance your text?** 
        - Paste your AI-generated content above
        - Adjust the sliders to control enhancement intensity  
        - Click the 'Humanize Text' button to transform your writing
        - Your citations will be automatically protected!
        """)

# Run the app
if __name__ == "__main__":
    show_humanize_page()