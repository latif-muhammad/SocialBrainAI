

from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# filename: rag_keyword_extractor.py

# 🆕 Correct imports
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate

class RAGKeywordExtractor:
    def __init__(self, 
                 search_k=20, 
                 chunk_size=1000, 
                 chunk_overlap=50,
                 embedding_model_name="text-embedding-ada-002",
                 llm_model_name="gpt-4",
                 similarity_k=3):
        
        self.search_tool = TavilySearchResults(k=search_k)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.embedding_model = OpenAIEmbeddings(model=embedding_model_name)
        self.llm = ChatOpenAI(model=llm_model_name, temperature=0)
        self.similarity_k = similarity_k

        self.prompt = ChatPromptTemplate.from_template("""
You are a social media trend analyst. Given a user prompt, your job is to extract
    the most trending keywords, hashtags, and related tags that people are searching or using online.

    Rules:
    - Focus on keywords that are popular in 2025.
    - Include hashtags that are trending on Facebook, X, TikTok, Instagram, Linkedin and YouTube.
    - Return exactly 25 items as a list.
    - Don't include explanations, only output the tags or keywords.

    User Prompt: "{user_prompt}"

    give relevant keywords from the following text:
        {text}
        Return only the keywords as a comma-separated list.
        """)
        
        # In new version, you don't use LLMChain
        self.chain = self.prompt | self.llm

    # def retrieve_and_split(self, user_prompt):
    #     print("[Step 1] Retrieving search results...")
    #     results = self.search_tool.invoke({"query": user_prompt})
    #     contents = [res['content'] for res in results]
    #     documents = self.text_splitter.create_documents(contents)
    #     return documents


    def retrieve_and_split(self, user_prompt):
        print("[Step 1] Retrieving search results...")
        results = self.search_tool.invoke({"query": user_prompt})
        

        
        # Ensure results is a list of dictionaries
        if isinstance(results, list) and all(isinstance(res, dict) for res in results):
            contents = [res['content'] for res in results]
        else:
            raise ValueError("Unexpected format of search results. Expected a list of dictionaries.")
        
        documents = self.text_splitter.create_documents(contents)
        return documents

    def retrieve(self, user_prompt):
        print("[Step 1] Retrieving search results...")
        results = self.search_tool.invoke({"query": user_prompt})

        # Ensure results is a list of dictionaries
        if isinstance(results, list) and all(isinstance(res, dict) for res in results):
            return results
        else:
            raise ValueError("Unexpected format of search results. Expected a list of dictionaries.")

    def build_vectorstore(self, documents):
        print("[Step 2] Building vectorstore...")
        vectorstore = FAISS.from_documents(documents, self.embedding_model)
        return vectorstore

    def similarity_search(self, vectorstore, user_prompt):
        print("[Step 3] Performing similarity search...")
        relevant_docs = vectorstore.similarity_search(user_prompt, k=self.similarity_k)
        return relevant_docs

    def extract_keywords(self, user_prompt, relevant_docs):
        print("[Step 4] Extracting keywords with LLM...")
        combined_text = " ".join(doc.page_content for doc in relevant_docs)
        keywords = self.chain.invoke({"user_prompt": user_prompt, "text": combined_text})
        return keywords.content.strip()

    def find_keywords(self, user_prompt):
        documents = self.retrieve_and_split(user_prompt)
        vectorstore = self.build_vectorstore(documents)
        relevant_docs = self.similarity_search(vectorstore, user_prompt)
        keywords = self.extract_keywords(user_prompt, relevant_docs)
        return keywords

if __name__ == "__main__":
    extractor = RAGKeywordExtractor()

    user_prompt = input("Enter your prompt: ")

    docs = extractor.retrieve(user_prompt)
    print("length  " ,len(docs) , "   type " ,type(docs))
    for i in docs:
        print(i['content'])
        print("--------------------------------------------------")     

   # Save the retrieved documents to a text file
    with open("retrieved_documents.txt", "w", encoding="utf-8") as file:
        for i, doc in enumerate(docs):
            file.write(f"Document {i + 1}:\n")
            file.write(doc.page_content + "\n\n")
   

    print("Documents have been saved to 'retrieved_documents.txt'.")

    # keywords = extractor.find_keywords(user_prompt)
# print("\n🔑 Extracted Keywords:\n", keywords)