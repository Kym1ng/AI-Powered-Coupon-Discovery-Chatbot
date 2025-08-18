import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

class CouponAssistant:
    def __init__(self, openai_api_key: str = None, model_name: str = "gpt-3.5-turbo-0125"):
        """
        Initialize the Coupon Assistant with LangChain components
        
        Args:
            openai_api_key: OpenAI API key (will try to get from env if not provided)
            model_name: OpenAI model to use
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it to constructor.")
        
        self.model_name = model_name
        self.llm = ChatOpenAI(
            openai_api_key=self.openai_api_key,
            model_name=model_name,
            temperature=0.7
        )
        
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        self.vectorstore = None
        self.qa_chain = None
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
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
        """Set up the vector store with coupon documents"""
        print("🔄 Setting up vector store...")
        
        # Prepare documents
        documents = self._prepare_documents()
        print(f"📄 Created {len(documents)} documents from coupon data")
        
        # Split documents if they're too long
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        split_docs = text_splitter.split_documents(documents)
        print(f"✂️  Split into {len(split_docs)} chunks")
        
        # Create vector store
        self.vectorstore = Chroma.from_documents(
            documents=split_docs,
            embedding=self.embeddings
        )
        print("✅ Vector store created successfully!")
    
    def setup_qa_chain(self):
        """Set up the question-answering chain"""
        if not self.vectorstore:
            self.setup_vectorstore()
        
        # Custom prompt template
        template = """You are a helpful coupon assistant. You help users find the best coupons and deals from SimplyCodes.com.

Use the following context to answer the user's question. If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context: {context}

Question: {question}

Answer the question based on the context above. If the user is asking about coupons, provide specific details including:
- Brand name
- Coupon code
- Description/discount
- Category and subcategory
- URL if available

If there are multiple relevant coupons, list them all. Be helpful and friendly in your response.

Answer:"""

        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # Create QA chain
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 5}),
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": prompt},
            return_source_documents=True,
            verbose=False
        )
        
        print("✅ QA chain set up successfully!")
    
    def ask(self, question: str) -> Dict[str, Any]:
        """
        Ask a question about coupons
        
        Args:
            question: The user's question
            
        Returns:
            Dictionary with answer and source documents
        """
        if not self.qa_chain:
            self.setup_qa_chain()
        
        try:
            result = self.qa_chain({"question": question})
            
            return {
                "answer": result["answer"],
                "source_documents": [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata
                    }
                    for doc in result.get("source_documents", [])
                ]
            }
        except Exception as e:
            return {
                "answer": f"Sorry, I encountered an error: {str(e)}",
                "source_documents": []
            }
    
    def search_coupons(self, query: str, category: str = None, brand: str = None) -> List[Dict[str, Any]]:
        """
        Search for specific coupons
        
        Args:
            query: Search query
            category: Filter by category (optional)
            brand: Filter by brand (optional)
            
        Returns:
            List of matching coupons
        """
        results = []
        
        for category_key, category_data in self.coupon_data.items():
            category_name = category_data['category_name']
            
            # Filter by category if specified
            if category and category.lower() not in category_name.lower():
                continue
                
            for subcategory_key, subcategory_data in category_data['subcategories'].items():
                subcategory_name = subcategory_data['subcategories_name']
                
                for coupon in subcategory_data['coupons']:
                    # Filter by brand if specified
                    if brand and brand.lower() not in coupon['brand'].lower():
                        continue
                    
                    # Check if query matches any coupon field
                    query_lower = query.lower()
                    if (query_lower in coupon['brand'].lower() or
                        query_lower in coupon['code'].lower() or
                        query_lower in coupon['description'].lower() or
                        query_lower in category_name.lower() or
                        query_lower in subcategory_name.lower()):
                        
                        results.append({
                            "brand": coupon['brand'],
                            "code": coupon['code'],
                            "description": coupon['description'],
                            "category": category_name,
                            "subcategory": subcategory_name,
                            "url": subcategory_data['url'],
                            "button_index": coupon.get('button_index', 0)
                        })
        
        return results
    
    def get_categories(self) -> List[str]:
        """Get list of all available categories"""
        return [data['category_name'] for data in self.coupon_data.values()]
    
    def get_brands(self) -> List[str]:
        """Get list of all available brands"""
        brands = set()
        for category_data in self.coupon_data.values():
            for subcategory_data in category_data['subcategories'].values():
                for coupon in subcategory_data['coupons']:
                    brands.add(coupon['brand'])
        return sorted(list(brands))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the coupon data"""
        total_coupons = 0
        total_categories = len(self.coupon_data)
        total_subcategories = 0
        
        for category_data in self.coupon_data.values():
            total_subcategories += len(category_data['subcategories'])
            for subcategory_data in category_data['subcategories'].values():
                total_coupons += len(subcategory_data['coupons'])
        
        return {
            "total_coupons": total_coupons,
            "total_categories": total_categories,
            "total_subcategories": total_subcategories,
            "categories": self.get_categories()
        } 