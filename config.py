"""
Configuration file for document classification
Defines categories, keywords, and thresholds
"""

# Desktop paths
DESKTOP_PATH = None  # Will be set dynamically

# Classification Categories and Keywords
CLASSIFICATION_KEYWORDS = {
    "UNIVERSITY_DOCS": {
        "keywords": [
            "transcript", "semester", "enrollment", "registration",
            "student", "course", "internship", "academic", "approval",
            "application", "degree", "certification", "gpa", "university",
            "campus", "enrollment", "registered", "courses", "standing"
        ],
        "weight": 1.0,
        "description": "Academic and educational documents"
    },
    "TECHNICAL_WORK": {
        "keywords": [
            "api", "docker", "devops", "configuration", "automation",
            "infrastructure", "deployment", "code", "technical",
            "development", "integration", "testing", "kubernetes",
            "container", "microservices", "cicd", "github", "jenkins","game"
        ],
        "weight": 1.0,
        "description": "Technical documentation and development work"
    },
    "CAPSTONE_WORK": {
        "keywords": [
            "capstone", "project", "proposal", "presentation", "research",
            "data collection", "analysis", "methodology", "thesis",
            "findings", "conclusion", "hypothesis", "experiment",
            "report", "paper", "study", "slides", "results"
        ],
        "weight": 1.0,
        "description": "Capstone projects and research work"
    }
}

# Scoring settings
FILENAME_WEIGHT = 1.5  # Filenames weighted more heavily
CONTENT_WEIGHT = 1.0   # Content weight
SCORE_THRESHOLD = 0.3  # Minimum confidence score

# File extensions that are supported
SUPPORTED_EXTENSIONS = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".xlsx": "excel",
    ".pptx": "pptx",
    ".md": "markdown",
    ".txt": "text"
}

# Database settings
DATABASE_PATH = None  # Will be set dynamically to Desktop/automation.db

print("[OK] Configuration loaded")
