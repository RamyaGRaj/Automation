"""
Semantic Classifier Module
Classifies documents based on keyword matching and semantic analysis
"""

from pathlib import Path
from config import CLASSIFICATION_KEYWORDS, FILENAME_WEIGHT, CONTENT_WEIGHT, SCORE_THRESHOLD
from file_parser import extract_content


def normalize_text(text):
    """Convert text to lowercase for matching"""
    return text.lower()


def calculate_keyword_score(text, keywords):
    """
    Calculate match score for a set of keywords in text
    Returns: number of matches
    """
    matches = 0
    text_lower = normalize_text(text)
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        # Count occurrences (case-insensitive)
        matches += text_lower.count(keyword_lower)
    
    return matches


def classify_document(file_path):
    """
    Classify a document into one of the predefined categories
    
    Args:
        file_path: Path to the document file
    
    Returns:
        {
            "filename": str,
            "category": str,
            "confidence_score": float (0-1),
            "keywords_matched": list,
            "reasoning": str,
            "all_scores": dict,
            "status": "success" or "error"
        }
    """
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        return {
            "filename": file_path.name,
            "category": None,
            "confidence_score": 0.0,
            "keywords_matched": [],
            "reasoning": f"File not found: {file_path}",
            "all_scores": {},
            "status": "error"
        }
    
    # Extract filename and content
    filename, content = extract_content(file_path)
    
    if filename is None:
        return {
            "filename": file_path.name,
            "category": None,
            "confidence_score": 0.0,
            "keywords_matched": [],
            "reasoning": "Could not extract content from file",
            "all_scores": {},
            "status": "error"
        }
    
    # Prepare text for scoring
    filename_text = filename.replace("_", " ").replace("-", " ")
    full_text = f"{filename_text} {content}"
    
    # Calculate scores for each category
    scores = {}
    matched_keywords_per_category = {}
    
    for category, category_info in CLASSIFICATION_KEYWORDS.items():
        keywords = category_info["keywords"]
        
        # Score filename and content separately
        filename_score = calculate_keyword_score(filename_text, keywords) * FILENAME_WEIGHT
        content_score = calculate_keyword_score(content, keywords) * CONTENT_WEIGHT
        
        total_score = filename_score + content_score
        scores[category] = total_score
        
        # Track matched keywords
        matched = []
        for keyword in keywords:
            if normalize_text(keyword) in normalize_text(full_text):
                matched.append(keyword)
        matched_keywords_per_category[category] = matched
    
    # Find the category with the highest score
    best_category = max(scores, key=scores.get)
    best_score = scores[best_category]
    
    # Calculate confidence score (normalize to 0-1 range)
    total_scores = sum(scores.values())
    if total_scores > 0:
        confidence = best_score / (total_scores + 1)  # +1 to avoid division by zero
    else:
        confidence = 0.0
    
    # Ensure confidence is between 0 and 1
    confidence = min(max(confidence, 0.0), 1.0)
    
    # Check if confidence meets threshold
    if confidence < SCORE_THRESHOLD:
        status = "low_confidence"
        reasoning = f"Low confidence score ({confidence:.2f}). Top category: {best_category}"
    else:
        status = "success"
        reasoning = f"Strong match on {best_category} with {len(matched_keywords_per_category[best_category])} keywords"
    
    return {
        "filename": filename,
        "category": best_category,
        "confidence_score": confidence,
        "keywords_matched": matched_keywords_per_category[best_category],
        "reasoning": reasoning,
        "all_scores": {k: v for k, v in scores.items()},
        "status": status
    }


def batch_classify(file_paths):
    """
    Classify multiple files
    
    Args:
        file_paths: List of file paths
    
    Returns:
        List of classification results
    """
    results = []
    for file_path in file_paths:
        result = classify_document(file_path)
        results.append(result)
    
    return results


if __name__ == "__main__":
    # Test the classifier
    test_files = [
        Path.home() / "Desktop" / "Semester_Transcript_2024.pdf",
        Path.home() / "Desktop" / "Docker_Configuration_Checklist.docx",
        Path.home() / "Desktop" / "Capstone_Project_Proposal.pdf",
    ]
    
    print("🔍 Testing Classifier\n")
    for test_file in test_files:
        if test_file.exists():
            result = classify_document(test_file)
            print(f"File: {result['filename']}")
            print(f"Category: {result['category']}")
            print(f"Confidence: {result['confidence_score']:.2%}")
            print(f"Status: {result['status']}")
            print(f"Reasoning: {result['reasoning']}")
            print("-" * 60)
        else:
            print(f"Test file not found: {test_file}\n")
