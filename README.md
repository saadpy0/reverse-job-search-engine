# AI-Driven Reverse Job Search Engine

An intelligent job search platform that analyzes resumes and suggests hidden job opportunities based on skills and company fit using advanced NLP and machine learning techniques.

## 🚀 Features

- **AI-Powered Resume Parsing**: BERT-based NLP models to extract skills, experience, and qualifications
- **Smart Job Matching**: Semantic similarity matching between resumes and job descriptions
- **Hidden Opportunity Discovery**: Clustering algorithms to find emerging and underrepresented job opportunities
- **Intelligent Ranking**: ML-based ranking system prioritizing the best job matches
- **Company Fit Analysis**: Assessment of cultural and technical fit with potential employers

## 🏗️ Architecture

```
reverse-job-search/
├── app/                    # Main application code
│   ├── api/               # FastAPI REST endpoints
│   ├── core/              # Core business logic
│   ├── models/            # ML models and AI components
│   ├── services/          # External service integrations
│   └── utils/             # Utility functions
├── data/                  # Data storage and processing
│   ├── raw/               # Raw job data and resumes
│   ├── processed/         # Processed and cleaned data
│   └── models/            # Trained model artifacts
├── notebooks/             # Jupyter notebooks for experimentation
├── tests/                 # Test suite
├── config/                # Configuration files
└── docs/                  # Documentation
```

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy
- **AI/ML**: TensorFlow, Transformers (BERT), scikit-learn, pandas
- **Database**: PostgreSQL, Redis (caching)
- **Frontend**: React, TypeScript (future phase)
- **Deployment**: Docker, AWS/GCP (future phase)

## 📋 Prerequisites

- Python 3.9+
- pip
- virtualenv or conda

## 🚀 Quick Start

1. **Clone and Setup**:
   ```bash
   git clone <repository-url>
   cd reverse-job-search
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment Setup**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Database Setup**:
   ```bash
   python scripts/setup_database.py
   ```

4. **Run the Application**:
   ```bash
   uvicorn app.api.main:app --reload
   ```

## 📊 Project Phases

- ✅ **Phase 1**: Project Setup & Data Pipeline
- 🔄 **Phase 2**: Resume Parser (BERT-based NLP)
- ⏳ **Phase 3**: Job Data Collection
- ⏳ **Phase 4**: AI Matching Engine
- ⏳ **Phase 5**: Clustering & Hidden Opportunities
- ⏳ **Phase 6**: Ranking System
- ⏳ **Phase 7**: API & Backend
- ⏳ **Phase 8**: User Interface
- ⏳ **Phase 9**: Performance & Analytics
- ⏳ **Phase 10**: Deployment & Testing

## 🤝 Contributing

This project is currently in active development. Please refer to the development guidelines in `docs/`.

## 📄 License

MIT License - see LICENSE file for details.
