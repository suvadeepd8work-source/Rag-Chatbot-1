import json
import os
import re

# Configuration
CHUNKS_FILE = os.path.join("Phase_2_Vector_Database", "course_chunks.json")

def initialize_db():
    # In lightweight mode, we just load the chunks into memory as a list
    if not os.path.exists(CHUNKS_FILE):
        print(f"Error: {CHUNKS_FILE} not found. Run prepare_data.py first.")
        return []
    
    with open(CHUNKS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def query_db(collection, query_text, n_results=3):
    """
    Advanced Lightweight Keyword Search with Course Mention Detection
    """
    query_lower = query_text.lower()
    
    # 1. Course Mention Detection (Synonym mapping)
    course_keywords = {
        "Product Management": ["product management", "pm", "product manager", "pm fellowship", "product management course", "product management fellowship"],
        "Ux Design": ["ux", "ui", "design", "ux design", "ui ux", "user experience", "ux design course", "ux design fellowship"],
        "Data Analytics": ["data analytics", "data analyst", "data", "data analytics course", "data analytics fellowship"],
        "Business Analytics": ["business analytics", "business analyst", "analytics", "business analytics course", "business analytics fellowship"],
        "Generative Ai": ["genai", "generative ai", "ai", "llm", "generative", "generative ai course", "generative ai bootcamp"]
    }
    
    detected_course = None
    for course_name, aliases in course_keywords.items():
        if any(alias in query_lower for alias in aliases):
            detected_course = course_name
            break

    # 2. Prepare keywords
    stop_words = {"what", "is", "the", "of", "and", "a", "to", "in", "it", "you", "that", "was", "for", "on", "are", "with", "as", "i", "at", "be", "this", "have", "from", "or", "one", "had", "by", "word", "but", "not", "all", "were", "we", "when", "your", "can", "said", "there", "use", "an", "each", "which", "she", "do", "how", "their", "if", "will", "up", "other", "about", "out", "many", "then", "them", "these", "so", "some", "her", "would", "make", "like", "him", "into", "time", "has", "look", "two", "more", "write", "go", "see", "number", "no", "way", "could", "my", "than", "first", "water", "been", "call", "who", "oil", "its", "now", "find", "long", "down", "day", "did", "get", "come", "made", "may", "part"}
    
    query_words = re.findall(r'\w+', query_lower)
    keywords = [w for w in query_words if w not in stop_words and len(w) > 2]
    if not keywords: keywords = query_words

    scored_chunks = []
    for chunk in collection:
        content = chunk["content"].lower()
        chunk_course = chunk["metadata"].get("course", "")
        
        score = 0
        
        # If this chunk belongs to the detected course, give it a massive boost
        if detected_course and chunk_course == detected_course:
            score += 10
            
        for kw in keywords:
            if re.search(rf'\b{re.escape(kw)}\b', content):
                score += 3
            elif kw in content:
                score += 1
        
        if score > 0:
            scored_chunks.append((score, chunk))
            
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    
    results = {'documents': [[]], 'metadatas': [[]]}
    
    if not scored_chunks:
        # Fallback: Top 10 results if nothing specific matches
        for chunk in collection[:10]:
            results['documents'][0].append(chunk['content'])
            results['metadatas'][0].append(chunk['metadata'])
    else:
        for score, chunk in scored_chunks[:n_results]:
            results['documents'][0].append(chunk['content'])
            results['metadatas'][0].append(chunk['metadata'])
        
    return results

if __name__ == "__main__":
    col = initialize_db()
    print(f"Initialized lightweight search with {len(col)} chunks.")
    
    # Test query
    print("\n--- Testing Lightweight Query: 'Product Management' ---")
    res = query_db(col, "Product Management")
    if res['documents'][0]:
        print(f"Top Result: {res['documents'][0][0][:100]}...")
    else:
        print("No results found.")
