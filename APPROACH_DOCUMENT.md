# Approach Document: Intelligent Document Classification & Automation

## Document Metadata
- **Author:** Ramya
- **Reviewers:** Technical Lead
- **Date:** 29/12/2025
- **Version:** v1.0
- **Project:** Multi-Platform Document Classification & File Organization System

---

## 1. Project Goal

### High-Level Summary
Build an intelligent, cross-platform document classification and automation system that automatically categorizes documents across two environments (Desktop GUI and Google Drive web) into designated folders with 100% accuracy over five consecutive execution cycles.

### Target Persona & Domain
- **Persona:** Knowledge Workers, Students, Researchers managing mixed document types
- **Domain:** Document Management & File Organization
- **Intended Outcome:** Hands-free, intelligent document classification that eliminates manual file organization while maintaining semantic accuracy regardless of file ordering or patterns

---

## 2. Current Baseline (State of the Union)

### Technology Stack
- **Core Language:** Python 3.10+
- **File Processing:** `python-docx`, `PyPDF2`, `openpyxl`, `python-pptx`
- **Text Analysis:** spaCy (NLP), custom keyword extraction
- **Desktop Automation:** `shutil`, `os`, `pathlib`
- **Web Automation:** Google Drive API (`google-auth-oauthlib`, `google-api-python-client`)
- **Orchestration:** Python execution pipeline with logging framework
- **Version Control:** Git/GitHub

### Existing Infrastructure
- **Current State:** Blank slate - greenfield project
- **Starting Point:** Definition of three document categories with distinct semantic boundaries
- **Support Capabilities:** Python runtime with pip package management, Google Drive API access, Desktop file system access

### Reliability Features (Planned)
- Idempotent operations (state-aware file movements)
- Comprehensive logging with timestamps
- Deterministic classification (same input always produces same output)
- Multi-run validation system

---

## 3. Technical Approach

### Why This Approach?
We chose a **semantic keyword-based classification with multi-agent orchestration** instead of:
- ❌ **Pattern/Naming Conventions**: Vulnerable to filename obfuscation; doesn't test true intelligence
- ❌ **Rule-Based Regex**: Brittle and requires constant rule updates
- ❌ **Simple Keyword Matching**: Too simplistic, cannot handle context
- ❌ **Machine Learning Models**: Overkill for deterministic rules; difficult to maintain consistency across runs

### Our Solution: Multi-Agent Semantic Classification
Combines **lightweight NLP + content-aware parsing + deterministic scoring** to achieve intelligent classification without ML training overhead.

---

### Agent Architecture

#### **Agent 1: File Parser & Content Extractor**
**Responsibility:** Extract readable text from all file formats
- Parse PDF content (`PyPDF2`)
- Extract text from DOCX (`python-docx`)
- Read plain text files (TXT, MD)
- Extract Excel content (`openpyxl`)
- Extract presentation text (`python-pptx`)

**Input:** File path (any supported format)
**Output:** Extracted text + file metadata (name, extension, size)
**Why:** Enables content-based classification, not just filename analysis

---

#### **Agent 2: Semantic Classifier**
**Responsibility:** Score documents against predefined categories using keyword matching + semantic relevance

**Classification Knowledge Base:**
```
UNIVERSITY_DOCS:
  Keywords: [transcript, enrollment, registration, student, course, 
             internship, academic, approval, semester, application, 
             admission, degree, credential, certification]
  Context: Academic/educational documents from institutions

TECHNICAL_WORK:
  Keywords: [API, DevOps, Docker, configuration, automation, code, 
             technical, documentation, development, infrastructure, 
             deployment, integration, system, testing, debugging]
  Context: Professional technical documentation and work

CAPSTONE_WORK:
  Keywords: [capstone, project, proposal, presentation, research, 
             data collection, analysis, findings, conclusion, 
             methodology, hypothesis, report, thesis]
  Context: Academic research & capstone projects
```

**Scoring Algorithm:**
- Count keyword matches in filename + content (case-insensitive)
- Apply semantic weights (filename: 1.5x, content: 1.0x)
- Normalize scores across categories
- Return category with highest score (threshold: >0.3)
- Fallback logic: Manual review flag if ambiguous (score variance < 0.1)

**Input:** Extracted text from Agent 1
**Output:** `{category: str, score: float, confidence: float, keywords_matched: list}`

---

#### **Agent 3: File Movement Orchestrator**
**Responsibility:** Execute file movements with safety checks and state management

**Operations:**
1. Check if file already in target folder (idempotency)
2. Verify target folder exists, create if needed
3. Move file using atomic file operations
4. Log movement with timestamp
5. Update execution state file
6. Handle platform differences (Desktop vs Drive)

**Input:** Classification result + file path
**Output:** Movement status + execution log entry
**Why:** Ensures consistency across 5 runs without duplicate movements

---

### Platform-Specific Implementations

#### **Desktop Implementation (GUI Automation)**
- Monitor Desktop directory
- Use `os.listdir()` to enumerate files
- Apply classification pipeline
- Use `shutil.move()` for atomic operations
- Maintain local SQLite log for state tracking

### Sample I/O: Desktop Classification

**Request:**
```json
{
  "file_path": "C:\\Users\\ramya\\Desktop\\Semester_Transcript_2024.pdf",
  "run_id": "run_001"
}
```

**Response:**
```json
{
  "status": "success",
  "file_name": "Semester_Transcript_2024.pdf",
  "classification": {
    "category": "UNIVERSITY_DOCS",
    "confidence_score": 0.92,
    "keywords_matched": ["transcript", "semester"],
    "reasoning": "High match on 'transcript' (filename) + 'semester' (content)"
  },
  "movement": {
    "source": "C:\\Users\\ramya\\Desktop\\Semester_Transcript_2024.pdf",
    "destination": "C:\\Users\\ramya\\Desktop\\University Docs\\Semester_Transcript_2024.pdf",
    "status": "completed",
    "timestamp": "2025-12-29T14:32:15Z"
  }
}
```

### Sample I/O: Multi-Run Validation

**Request:**
```json
{
  "run_count": 5,
  "execution_logs": ["run_001.log", "run_002.log", "run_003.log", "run_004.log", "run_005.log"]
}
```

**Response:**
```json
{
  "status": "validation_complete",
  "total_files_processed": 50,
  "consistency_score": 1.0,
  "accuracy_summary": {
    "run_1": {"correct": 10, "total": 10, "accuracy": 1.0},
    "run_2": {"correct": 10, "total": 10, "accuracy": 1.0},
    "run_3": {"correct": 10, "total": 10, "accuracy": 1.0},
    "run_4": {"correct": 10, "total": 10, "accuracy": 1.0},
    "run_5": {"correct": 10, "total": 10, "accuracy": 1.0}
  },
  "cross_run_consistency": 1.0,
  "conclusion": "100% accuracy maintained across all 5 runs"
}
```

---

## 5. Strategic Roadmap (Phased Approach)

### Phase 1: Core Classification Engine & Desktop Automation
**Goal:** Build deterministic semantic classifier with 100% accuracy on desktop dataset

**Intuition:** 
- Establish classification logic as single source of truth
- Validate on simpler desktop environment first
- Build comprehensive logging framework early


### Phase 2: Multi-Run Reliability & State Management
**Goal:** Ensure 100% consistency across 5 consecutive execution cycles

**Intuition:**
- Idempotent operations prevent duplicate movements
- State tracking prevents re-processing of moved files
- Deterministic classification guarantees same output for same input



### Phase 3: Google Drive Web Automation & API Integration
**Goal:** Replicate classification logic for cloud-based document management

**Intuition:**
- Google Drive API provides remote file operations without manual download
- Same semantic classifier ensures platform consistency
- OAuth 2.0 enables secure integration



### Phase 4: Documentation, Testing & Deployment
**Goal:** Deliver production-ready solution with comprehensive documentation

**Intuition:**
- Reproducible setup ensures others can replicate results
- Automated testing validates reliability
- Clear documentation enables adoption


### External Libraries & APIs
- **PyPDF2**: https://pypdf.readthedocs.io/
- **python-docx**: https://python-docx.readthedocs.io/
- **openpyxl**: https://openpyxl.readthedocs.io/
- **python-pptx**: https://python-pptx.readthedocs.io/
- **spaCy**: https://spacy.io/
- **Google Drive API**: https://developers.google.com/drive/api/v3/


### Research & Best Practices
- Document Classification: Information Retrieval fundamentals
- Semantic Analysis: Keyword extraction & TF-IDF basics
- API Design: RESTful principles (RFC 3986)
- File Operations: POSIX file semantics & idempotency patterns
- Automation Testing: Python `unittest` & `pytest` frameworks

### Tools & Frameworks
- **Version Control:** Git/GitHub
- **Testing:** pytest, unittest
- **Logging:** Python logging module
- **Package Management:** pip, requirements.txt
- **CI/CD:** GitHub Actions (future enhancement)

---

## Appendix: Classification Knowledge Base Detail

### UNIVERSITY_DOCS Category
**Primary Keywords:** transcript, enrollment, registration, student, course, internship, academic, approval, semester, application, admission, degree, credential, certification

**Contextual Indicators:** Academic institutions, educational milestones, enrollment processes, financial/academic standing, course registration, internship programs

**Example Files in This Category:**
- Semester_Transcript_2024.pdf
- Course_Registration_Form.docx
- Internship_Approval_Letter.pdf
- Student_ID_Application.docx

---

### TECHNICAL_WORK Category
**Primary Keywords:** API, DevOps, Docker, configuration, automation, code, technical, documentation, development, infrastructure, deployment, integration, system, testing, debugging

### CAPSTONE_WORK Category
**Primary Keywords:** capstone, project, proposal, presentation, research, data collection, analysis, findings, conclusion, methodology, hypothesis, report, thesis

**Contextual Indicators:** Research documents, academic projects, experimental data, presentation materials, formal reports, academic conclusions

**Example Files in This Category:**
- Capstone_Project_Proposal.pdf
- Capstone_Data_Collection_Log.xlsx
- Final_Presentation_Slides.pptx

---



