import os
import json
from groq import Groq
from dotenv import load_dotenv
import sys

# Add project root to path to import from Phase 2
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
from Phase_2_Vector_Database.vector_db import initialize_db, query_db

# Load .env from project root
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

class NextLeapRAG:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.collection = initialize_db()
        self.model = "llama-3.1-8b-instant" # Modern fast model on Groq

    def get_context(self, query, n_results=8):
        results = query_db(self.collection, query, n_results=n_results)
        print(f"DEBUG: Retrieved {len(results['documents'][0])} chunks for query: {query}")

        
        context_list = []
        sources = set()
        
        for i in range(len(results['documents'][0])):
            doc = results['documents'][0][i]
            url = results['metadatas'][0][i]['url']
            context_list.append(f"Content: {doc}\nSource URL: {url}")
            sources.add(url)
            
        return "\n\n---\n\n".join(context_list), list(sources)

    def generate_response_stream(self, user_query):
        context, sources = self.get_context(user_query)
        
        system_prompt = f"""
        You are a helpful and professional NextLeap Chatbot. Your task is to provide accurate information about NextLeap's fellowships, courses, and programs based on the provided context.
        
        CRITICAL KNOWLEDGE:
        - At NextLeap, the terms "Fellowship", "Course", and "Program" are used interchangeably. 
        - If a user asks for the "Fellowship" price and the context mentions the "Course" price, they are the same thing. DO NOT distinguish between them.
        
        GUIDELINES:
        1. Use the provided "CONTEXT" to answer the question.
        2. Combine details from the context to provide a comprehensive answer.
        3. ALWAYS provide the Source URL found in the context for each course mentioned.
        4. Stay professional, helpful, and direct.
        
        CONTEXT:
        {context}
        """
        
        try:
            stream = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query},
                ],
                model=self.model,
                temperature=0,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Error: {str(e)}"

    def generate_response(self, user_query):
        # Synchronous wrapper for existing tests
        response = ""
        for chunk in self.generate_response_stream(user_query):
            response += chunk
        return response

if __name__ == "__main__":
    # Test block
    if not os.getenv("GROQ_API_KEY"):
        print("Please set your GROQ_API_KEY in the .env file.")
    else:
        rag = NextLeapRAG()
        print("Bot initialized. (Type 'exit' to quit)")
        while True:
            query = input("\nYou: ")
            if query.lower() == 'exit':
                break
            response = rag.generate_response(query)
            print(f"\nBot: {response}")
