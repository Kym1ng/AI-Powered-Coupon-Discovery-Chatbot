import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

class CouponAssistantGemini:
    def __init__(self, gemini_api_key: str = None, model_name: str = "gemini-1.5-flash"):
        """
        Initialize the Coupon Assistant with Gemini LangChain components
        
        Args:
            gemini_api_key: Google Gemini API key (will try to get from env if not provided)
            model_name: Gemini model to use (gemini-1.5-flash, gemini-1.5-pro, gemini-pro)
        """
        self.gemini_api_key = gemini_api_key or os.getenv("GOOGLE_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("Google Gemini API key is required. Set GOOGLE_API_KEY environment variable or pass it to constructor.")
        
        self.model_name = model_name
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=self.gemini_api_key,
            model=model_name,
            temperature=0.7
        )
        
        self.embeddings = GoogleGenerativeAIEmbeddings(
            google_api_key=self.gemini_api_key,
            model="models/embedding-001"
        )
        self.vectorstore = None
        self.qa_chain = None
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        # Load coupon data
        self.coupon_data = self._load_coupon_data()
        
    def _load_coupon_data(self) -> Dict[str, Any]:
        """Load coupon data from the tree structure JSON file"""
        data_path = Path(__file__).parent.parent / "data" / "category_tree.json"
        
        if not data_path.exists():
            raise FileNotFoundError(f"Coupon data not found at {data_path}. Please run the scraper first.")
        
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _prepare_documents(self) -> List[Document]:
        """Convert coupon data into LangChain documents for vectorization"""
        documents = []
        
        for category_key, category_data in self.coupon_data.items():
            category_name = category_data['category_name']
            category_path = category_data['category_path']
            
            for subcategory_key, subcategory_data in category_data['subcategories'].items():
                subcategory_name = subcategory_data['subcategories_name']
                subcategory_path = subcategory_data['subcategories_path']
                url = subcategory_data['url']
                coupons = subcategory_data['coupons']
                
                # Create document content for this subcategory
                content_parts = [
                    f"Category: {category_name}",
                    f"Subcategory: {subcategory_name}",
                    f"URL: {url}"
                ]
                
                # Add coupon information
                if coupons:
                    content_parts.append("Available coupons:")
                    for coupon in coupons:
                        content_parts.append(
                            f"- Brand: {coupon['brand']}, "
                            f"Code: {coupon['code']}, "
                            f"Description: {coupon['description']}"
                        )
                else:
                    content_parts.append("No coupons available in this subcategory.")
                
                # Create document
                content = "\n".join(content_parts)
                metadata = {
                    "category": category_name,
                    "subcategory": subcategory_name,
                    "category_path": category_path,
                    "subcategory_path": subcategory_path,
                    "url": url,
                    "coupon_count": len(coupons)
                }
                
                documents.append(Document(page_content=content, metadata=metadata))
        
        return documents
    
    def setup_vectorstore(self):
        """Initialize the vector store with coupon documents"""
        documents = self._prepare_documents()
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        split_docs = text_splitter.split_documents(documents)
        
        # Create vector store
        self.vectorstore = Chroma.from_documents(
            documents=split_docs,
            embedding=self.embeddings,
            collection_name="coupon_data"
        )
        
        print(f"✅ Vector store initialized with {len(split_docs)} document chunks")
    
    def setup_qa_chain(self):
        """Setup the conversational QA chain"""
        if not self.vectorstore:
            self.setup_vectorstore()
        
        # Custom prompt template
        template = """You are a helpful coupon assistant. You help users find relevant coupons and deals based on their questions.

Context: {context}

Question: {question}

Chat History: {chat_history}

Please provide helpful, accurate information about coupons and deals. If you find relevant coupons, include the brand name, coupon code, and description. If no relevant coupons are found, politely inform the user.

Answer:"""

        prompt = PromptTemplate(
            input_variables=["context", "question", "chat_history"],
            template=template
        )
        
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 5}),
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": prompt},
            return_source_documents=True,
            return_generated_question=False,
            output_key="answer"
        )
        
        print("✅ QA chain initialized with Gemini model")
    
    def ask(self, question: str) -> str:
        """Ask a question about coupons"""
        if not self.qa_chain:
            self.setup_qa_chain()
        
        try:
            result = self.qa_chain({"question": question})
            # Handle both possible response formats
            if "answer" in result:
                return result["answer"]
            elif "result" in result:
                return result["result"]
            else:
                return str(result)
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    def search_coupons(self, query: str, search_type: str = "keyword") -> List[Dict[str, Any]]:
        """Search for coupons using different methods"""
        results = []
        
        query_lower = query.lower()
        
        for category_key, category_data in self.coupon_data.items():
            category_name = category_data['category_name']
            
            for subcategory_key, subcategory_data in category_data['subcategories'].items():
                subcategory_name = subcategory_data['subcategories_name']
                url = subcategory_data['url']
                coupons = subcategory_data['coupons']
                
                # Search based on type
                if search_type == "keyword":
                    # Search in category, subcategory, and coupon details
                    if (query_lower in category_name.lower() or 
                        query_lower in subcategory_name.lower()):
                        results.extend(coupons)
                    else:
                        # Search in coupon details
                        for coupon in coupons:
                            if (query_lower in coupon['brand'].lower() or 
                                query_lower in coupon['description'].lower()):
                                results.append(coupon)
                
                elif search_type == "category":
                    if query_lower in category_name.lower():
                        results.extend(coupons)
                
                elif search_type == "brand":
                    for coupon in coupons:
                        if query_lower in coupon['brand'].lower():
                            results.append(coupon)
        
        return results[:20]  # Limit to 20 results
    
    def get_categories(self) -> List[str]:
        """Get list of all main categories"""
        return [data['category_name'] for data in self.coupon_data.values()]
    
    def get_brands(self) -> List[str]:
        """Get list of all unique brands"""
        brands = set()
        for category_data in self.coupon_data.values():
            for subcategory_data in category_data['subcategories'].values():
                for coupon in subcategory_data['coupons']:
                    brands.add(coupon['brand'])
        return sorted(list(brands))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the coupon database"""
        total_coupons = 0
        total_categories = len(self.coupon_data)
        total_subcategories = 0
        brands = set()
        
        for category_data in self.coupon_data.values():
            total_subcategories += len(category_data['subcategories'])
            for subcategory_data in category_data['subcategories'].values():
                total_coupons += len(subcategory_data['coupons'])
                for coupon in subcategory_data['coupons']:
                    brands.add(coupon['brand'])
        
        return {
            "total_coupons": total_coupons,
            "total_categories": total_categories,
            "total_subcategories": total_subcategories,
            "unique_brands": len(brands),
            "model": self.model_name,
            "api_provider": "Google Gemini"
        }
