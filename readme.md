# DocMind: A Unified Multi-Modal Framework for Intelligent Document Analysis

<div align="center">

![DocMind Logo](images/docmind_logo.png)

**🚀 A privacy-preserving, open-source RAG platform that seamlessly integrates document analysis, database querying, and web content extraction through natural language interaction**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.103.1-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Contributors](https://img.shields.io/badge/Contributors-5-orange.svg)](#contributors)

[🎯 Features](#-key-features) • [🏗️ Architecture](#️-system-architecture) • [⚡ Quick Start](#-quick-start) • [📱 Demo](#-demo) • [🔧 Installation](#-installation-guide) • [📖 Documentation](#-documentation)

</div>

---

## 📖 About DocMind

DocMind addresses the critical challenge of information fragmentation in modern organizations. Traditional systems force users to navigate multiple interfaces for accessing structured databases, unstructured documents, and dynamic web content. Our unified framework eliminates these silos through a single natural language interface.

### 🎯 Key Features

- **🔄 Unified Multi-Modal RAG**: Seamlessly integrates Document RAG, NL2SQL, and Web RAG in one platform
- **🔒 Privacy-First Architecture**: Local processing ensures sensitive data never leaves your environment
- **⚡ Real-Time Processing**: Dynamic web content integration with intelligent caching
- **🎯 92% Hallucination Reduction**: Grounded responses with comprehensive source attribution
- **📊 Advanced Analytics**: Built-in performance monitoring and usage analytics
- **🌐 Multi-Platform Access**: Web UI, REST API, and Android mobile app
- **💰 Cost-Effective**: Open-source alternative to expensive commercial solutions
- **🔍 Intelligent Query Orchestration**: Automatic source selection and parallel processing

### 🏆 Performance Highlights

| Metric | Improvement | Baseline |
|--------|-------------|----------|
| **Factual Accuracy** | 92% reduction in errors | vs. Direct LLM |
| **Information Gathering** | 78% faster | vs. Manual process |
| **Source Attribution** | 96% accuracy | vs. 0% in standard LLM |
| **User Satisfaction** | 4.4/5 rating | Based on user studies |
| **Query Processing** | 3.5-5.0s average | End-to-end response |

## 🏗️ System Architecture

![System Architecture](images/fig_1.png)

DocMind employs a modular, microservices-based architecture designed for scalability, maintainability, and privacy preservation. The system consists of four primary components:

### Core Components

1. **🔍 Document Processing Pipeline**
   - Multi-format support (PDF, DOCX, TXT, CSV, Excel)
   - Intelligent semantic chunking
   - Vector embedding generation using sentence-transformers

2. **🗄️ Database Integration Module**
   - Natural Language to SQL translation
   - Multi-database support via SQLAlchemy
   - Query validation and security checks

3. **🌐 Web Content Extraction**
   - Ethical web scraping with robots.txt compliance
   - Content quality assessment
   - Real-time information integration

4. **🤖 Unified Query Processing Engine**
   - Intent classification and source selection
   - Parallel multi-source processing
   - Response synthesis with confidence scoring

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | FastAPI 0.103.1 | High-performance API services |
| **LLM** | Llama 3.3 70B (via Groq) | Natural language generation |
| **Embeddings** | sentence-transformers | Semantic representation |
| **Vector DB** | ChromaDB 0.4.18 | Efficient similarity search |
| **Frontend** | Streamlit + React.js | Multi-interface support |
| **Mobile** | React Native/Expo | Cross-platform mobile app |

## 📱 Demo

### Document RAG in Action
![Document RAG Demo](images/fig_2.jpg)
*Semantic document retrieval with contextual response generation and source attribution*

### Natural Language to SQL
![NL2SQL Demo](images/fig_3.jpg)
*Converting natural language queries into executable SQL with explanations*

### Web RAG Integration
![Web RAG Demo](images/fig_4.jpg)
*Real-time web content integration providing current information*

## ⚡ Quick Start

Get DocMind running in under 5 minutes:

```bash
# Clone the repository
git clone https://github.com/your-username/docmind.git
cd docmind

# Set up Python environment
python -m venv docmind_env
source docmind_env/bin/activate  # On Windows: docmind_env\Scripts\activate

# Install backend dependencies
cd Backend
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start the backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In a new terminal, start the web UI
cd ../StreamlitWebUI
streamlit run app.py
```

🎉 **That's it!** Access your DocMind instance at `http://localhost:8501`

## 🔧 Installation Guide

### 📋 System Requirements

#### Minimum Hardware Requirements:
- **RAM**: 16GB (20GB recommended)
- **Processor**: Intel Core i5 or equivalent
- **Storage**: 10GB free space
- **Internet**: Required for API services

#### Software Requirements:
- **Python**: 3.8+
- **Node.js**: Latest LTS (for mobile app)
- **Java**: 17-21 (for Android development)
- **Android Studio**: SDK 30+ (optional)

### 🛠️ Detailed Setup

<details>
<summary><b>1. Backend Setup</b></summary>

```bash
# Navigate to backend directory
cd Backend

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example app/.env

# Edit app/.env with your configuration:
# JWT_SECRET_KEY=your_secure_jwt_secret_key
# GROQ_API_KEY=your_groq_api_key

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend will be available at:** `http://localhost:8000`
**API Documentation:** `http://localhost:8000/docs`

</details>

<details>
<summary><b>2. Web UI Setup</b></summary>

```bash
# Navigate to web UI directory
cd StreamlitWebUI

# Install dependencies
pip install -r requirements.txt

# Start the web interface
streamlit run app.py
```

**Web UI will be available at:** `http://localhost:8501`

</details>

<details>
<summary><b>3. Android App Setup (Optional)</b></summary>

```bash
# Navigate to Android app directory
cd DocMindAndroidApp

# Install dependencies
npm install

# Start development server
npm start

# Press 'a' to run on Android emulator
```

**Prerequisites:**
- Android Studio with AVD configured
- Android Virtual Device running (API 30+)
- Sufficient system resources allocated

</details>

### 🔒 Environment Configuration

Create a `.env` file in the `Backend/app/` directory:

```env
# JWT Configuration
JWT_SECRET_KEY=your_secure_jwt_secret_key_here

# API Keys
GROQ_API_KEY=your_groq_api_key_here

# Database Configuration
DATABASE_URL=your_database_url_here

# Optional: Additional configurations
VECTOR_DB_PATH=./data/chromadb
MAX_CHUNK_SIZE=1000
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## 📊 Usage Examples

### Document Upload and Query
```python
# Upload documents through the web interface or API
POST /api/documents/upload

# Query your documents
POST /api/query
{
  "query": "What are the key findings in the latest research report?",
  "sources": ["documents"]
}
```

### Database Integration
```python
# Connect your database
POST /api/database/connect
{
  "connection_string": "postgresql://user:pass@localhost/db",
  "database_type": "postgresql"
}

# Natural language database queries
POST /api/query
{
  "query": "Show me sales data for the last quarter",
  "sources": ["database"]
}
```

### Web Content Integration
```python
# Add web sources
POST /api/web/add-source
{
  "url": "https://example.com/news",
  "refresh_interval": 3600
}

# Query with web integration
POST /api/query
{
  "query": "What's the latest news about AI developments?",
  "sources": ["web", "documents"]
}
```

## 🧪 Evaluation Results

Our comprehensive evaluation demonstrates DocMind's superior performance:

### Individual Component Performance

| Component | Accuracy | Speed | Notes |
|-----------|----------|-------|-------|
| **Document RAG** | 94.2% | 3.2s/doc | +12% vs keyword search |
| **NL2SQL** | 92% | 1.2s | 98% success on simple queries |
| **Web RAG** | 91% | 1.8s/page | 97% information currency |

### System-Wide Improvements

- **📈 Factual Accuracy**: 92% reduction in hallucinations
- **⚡ Processing Speed**: 78% faster information gathering
- **🎯 User Satisfaction**: 4.4/5 overall rating
- **🔍 Source Attribution**: 96% accuracy vs 0% in direct LLM

## 🛠️ Troubleshooting

<details>
<summary><b>Common Issues & Solutions</b></summary>

### Python Environment Issues
```bash
# Verify Python version
python --version

# Update pip
pip install --upgrade pip

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### Backend Connection Issues
- Check if port 8000 is available
- Verify `.env` file configuration
- Ensure all API keys are correctly set

### Android Development Issues
- Verify Android Studio and SDK configuration
- Check AVD resource allocation (4GB RAM recommended)
- Enable hardware acceleration in BIOS settings

### Performance Optimization
- Allocate sufficient system resources
- Use SSD storage for better performance
- Close unnecessary applications
- Monitor memory usage during processing

</details>

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8 for Python code
- Use type hints where applicable
- Add comprehensive docstrings
- Include unit tests for new features

## 📚 Documentation

- **[API Documentation](http://localhost:8000/docs)** - Interactive Swagger UI
- **[User Guide](docs/user-guide.md)** - Comprehensive usage instructions
- **[Developer Guide](docs/developer-guide.md)** - Technical implementation details
- **[Deployment Guide](docs/deployment.md)** - Production deployment instructions

## 🔮 Future Roadmap

- [ ] **Multimodal Support**: Integration of image and video processing
- [ ] **Enterprise Connectors**: SharePoint, Salesforce, SAP integration
- [ ] **Advanced Analytics**: Usage patterns and optimization insights
- [ ] **Collaborative Features**: Shared workspaces and team collaboration
- [ ] **Mobile App Enhancement**: Offline capabilities and push notifications
- [ ] **Local LLM Support**: Reduced dependency on external APIs

## 🏆 Recognition

This project represents cutting-edge research in multi-modal information retrieval and has demonstrated significant improvements over existing solutions. The work addresses critical gaps in current knowledge management systems and provides a foundation for future innovations in AI-powered information access.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Siksha 'O' Anusandhan University** for research support
- **Groq** for providing LLM API access
- **Open-source community** for the amazing tools and libraries
- **Research participants** who provided valuable feedback

## 👥 Contributors

<table>
<tr>
<td align="center">
<a href="https://github.com/ramanarayan-ransingh">
<img src="https://github.com/ramanarayan-ransingh.png" width="100px;" alt="Ramanarayan Ransingh"/>
<br />
<sub><b>Ramanarayan Ransingh</b></sub>
</a>
<br />
<sub>Lead Developer & Researcher</sub>
</td>
<td align="center">
<a href="https://github.com/ansuman-patra">
<img src="https://github.com/ansuman-patra.png" width="100px;" alt="Ansuman Patra"/>
<br />
<sub><b>Ansuman Patra</b></sub>
</a>
<br />
<sub>Backend Architecture</sub>
</td>
<td align="center">
<a href="https://github.com/akash-kumar-n">
<img src="https://github.com/akash-kumar-n.png" width="100px;" alt="Akash Kumar N"/>
<br />
<sub><b>Akash Kumar N</b></sub>
</a>
<br />
<sub>Frontend Development</sub>
</td>
<td align="center">
<a href="https://github.com/subhajit-mohanty">
<img src="https://github.com/subhajit-mohanty.png" width="100px;" alt="Subhajit Mohanty"/>
<br />
<sub><b>Subhajit Mohanty</b></sub>
</a>
<br />
<sub>Mobile App Development</sub>
</td>
<td align="center">
<a href="https://github.com/sunil-samanta-singhar">
<img src="https://github.com/sunil-samanta-singhar.png" width="100px;" alt="Sunil Samanta Singhar"/>
<br />
<sub><b>Sunil Samanta Singhar</b></sub>
</a>
<br />
<sub>Research Supervisor</sub>
</td>
</tr>
</table>

---

<div align="center">

**⭐ If you find DocMind helpful, please consider giving us a star!**

[⬆ Back to Top](#docmind-a-unified-multi-modal-framework-for-intelligent-document-analysis)

Made with ❤️ by the DocMind Team

</div>