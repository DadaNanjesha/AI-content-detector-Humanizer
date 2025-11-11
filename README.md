# AI Content Detector & Humanizer

A comprehensive web application that combines AI content detection with text humanization capabilities. Analyze PDF documents for AI-generated content and transform AI-written text into natural, human-like writing while preserving academic integrity.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)

## 🚀 Features

### 🔍 PDF AI Content Detection
- **Advanced AI Detection**: Classify text as Human-written, AI-generated, or hybrid content
- **PDF Annotation**: Generate color-coded PDFs with visual highlights
- **Sentence-level Analysis**: Precise classification at the sentence level
- **Interactive Visualizations**: Charts and metrics for content analysis
- **Batch Processing**: Handle multiple documents efficiently

### ✍️ AI Text Humanization
- **Citation Protection**: Automatically detect and preserve academic citations
- **Smart Rewriting**: Expand contractions, replace synonyms, add transitions
- **Customizable Intensity**: Adjust transformation levels with sliders
- **Real-time Metrics**: Track word count and sentence count changes
- **Academic Focus**: Maintain formal tone while enhancing readability

## 🛠️ Technologies Used

### Core Framework
- **Streamlit** - Web application framework
- **Python 3.8+** - Backend programming language

### PDF Processing
- **PyMuPDF (fitz)** - PDF text extraction and annotation
- **ReportLab** - PDF generation and manipulation

### Natural Language Processing
- **spaCy** - Advanced NLP processing and POS tagging
- **NLTK** - Tokenization, stemming, and WordNet integration
- **Transformers** - Hugging Face AI model integration

### AI & Machine Learning
- **Hugging Face Transformers** - Pre-trained AI detection models
- **scikit-learn** - Machine learning utilities
- **torch** - Deep learning framework

### Data Processing & Visualization
- **pandas** - Data manipulation and analysis
- **altair** - Interactive visualizations and charts
- **NumPy** - Numerical computing

### Font & Typography
- **DejaVu Sans** - Open-source font for PDF annotations
- **Noto Sans** - Unicode-compatible font family

## 📁 Project Structure

```
AI-Content-Detector-Humanizer/
│
├── main.py                          # Main Streamlit application entry point
├── requirements.txt                 # Python dependencies
├── setup.sh                        # Environment setup script
├── nltk.txt                        # NLTK resource requirements
├── README.md                       # Project documentation
├── .gitignore                      # Git ignore rules
├── Proofile                        # Deployment configuration
│
├── pages/                          # Streamlit multi-page modules
│   ├── ai_detection.py            # PDF detection and annotation page
│   ├── humanize_text.py           # Text humanization page
│   └── __pycache__/               # Python bytecode cache
│
└── utils/                          # Utility modules and helpers
    ├── __init__.py                # Package initialization
    ├── ai_detection_utils.py      # AI content classification logic
    ├── citation_utils.py          # Citation detection and handling
    ├── humanizer.py               # Text humanization algorithms
    ├── model_loaders.py           # ML model loading utilities
    ├── pdf_utils.py               # PDF processing functions
    └── __pycache__/               # Python bytecode cache
│
├── DejaVuSans.ttf                 # Font file for PDF annotations
├── NotoSans-Regular.ttf           # Unicode-compatible font
└── venv/                          # Python virtual environment (local)
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step-by-Step Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/ai-content-detector-humanizer.git
   cd ai-content-detector-humanizer
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK resources**
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('wordnet')"
   ```

5. **Download spaCy model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

### Quick Setup (Alternative)
Run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

## 🎯 Usage

### Starting the Application
```bash
streamlit run main.py
```

The application will open in your default browser at `http://localhost:8501`

### PDF AI Content Detection
1. Navigate to the "PDF Detection & Annotation" page
2. Upload a PDF document (up to 200MB)
3. View AI classification results with interactive charts
4. Download color-coded annotated PDF
5. Analyze extracted text in the expandable section

### AI Text Humanization
1. Navigate to the "Humanize AI Text" page
2. Paste your AI-generated text
3. Adjust synonym replacement and transition probabilities
4. Click "Humanize Text" to process
5. View enhanced text with citation protection
6. Download the humanized result

## ⚙️ Configuration

### Environment Variables
Create a `.env` file for custom configuration:
```env
HUGGINGFACE_TOKEN=your_hf_token_here
MODEL_CACHE_DIR=./model_cache
MAX_FILE_SIZE=209715200  # 200MB in bytes
```

### Model Configuration
The application uses Hugging Face models for AI detection. Configure in `utils/model_loaders.py`:
```python
DETECTION_MODEL = "model-name"
CONFIDENCE_THRESHOLD = 0.8
BATCH_SIZE = 32
```

## 🔧 Advanced Features

### Custom Model Integration
Extend AI detection capabilities by modifying `utils/ai_detection_utils.py`:
```python
def classify_text_custom(text, model_name="your-custom-model"):
    # Implement custom classification logic
    pass
```

### Citation Style Support
Add new citation patterns in `utils/citation_utils.py`:
```python
CITATION_PATTERNS = {
    'apa': r'your-regex-pattern',
    'mla': r'your-regex-pattern',
    'chicago': r'your-regex-pattern'
}
```

## 📊 Performance Optimization

### Caching Strategies
The application implements Streamlit caching for:
- Model loading and inference
- PDF processing operations
- Text humanization results

### Memory Management
- Lazy loading of large models
- Automatic cleanup of temporary files
- Efficient batch processing for large documents

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

### Test Coverage
- PDF text extraction accuracy
- Citation detection and preservation
- AI classification consistency
- Text humanization quality

## 🐛 Troubleshooting

### Common Issues

**Issue**: "No text could be extracted from PDF"
**Solution**: Ensure PDF contains selectable text, not scanned images

**Issue**: "spaCy model not found"
**Solution**: Run `python -m spacy download en_core_web_sm`

**Issue**: "NLTK resources missing"
**Solution**: Run the NLTK download commands in installation steps

**Issue**: "Model loading timeout"
**Solution**: Check internet connection and Hugging Face token

## 📈 API Documentation

### Custom Integration
The utility modules can be imported for standalone use:

```python
from utils.ai_detection_utils import classify_text_hf
from utils.humanizer import minimal_rewriting

# AI Detection
classification_map, percentages = classify_text_hf(text)

# Text Humanization
humanized_text = minimal_rewriting(text, p_syn=0.2, p_trans=0.2)
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints where possible
- Include docstrings for all functions
- Write comprehensive tests


## 🙏 Acknowledgments

- **Hugging Face** for pre-trained models and transformers library
- **Streamlit** for the excellent web application framework
- **spaCy** and **NLTK** for NLP capabilities
- **PyMuPDF** team for robust PDF processing
- **Altair** for beautiful visualizations

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review troubleshooting section

## 🔮 Roadmap

- [ ] Multi-language support
- [ ] Additional citation styles
- [ ] Real-time collaboration features
- [ ] Advanced AI model fine-tuning
- [ ] Mobile application
- [ ] API service deployment
- [ ] Plugin system for extensibility

---

<div align="center">

**Built with ❤️ for the open-source community**

[Report Bug](https://github.com/DadaNanjesha/AI-content-detector-Humanizer/issues) · [Request Feature](https://github.com/DadaNanjesha/AI-content-detector-Humanizer/issues)

</div>