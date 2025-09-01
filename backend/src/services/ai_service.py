import os
import json
from flask import current_app
import openai
from src.models import db
from src.models.document import Document
from src.models.clause import Clause, ClauseCategory
from src.models.document_summary import DocumentSummary
from src.models.obligation import Obligation
from src.utils.file_processors import FileProcessor

class AIService:
    """Service for handling AI operations."""
    
    @staticmethod
    def init_openai():
        """Initialize OpenAI API."""
        openai.api_key = current_app.config['OPENAI_API_KEY']
    
    @staticmethod
    def analyze_document(document_id):
        """
        Analyze a document using OpenAI API.
        
        Args:
            document_id (int): The document ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Get document
        document = Document.query.get(document_id)
        if not document:
            current_app.logger.error(f"Document not found: {document_id}")
            return False
        
        # Get document content
        try:
            # Get file processor based on document type
            processor = FileProcessor.get_processor(document.file_type)
            
            # Extract text from document
            text = processor.extract_text(document.file_path)
            
            if not text:
                current_app.logger.error(f"Failed to extract text from document: {document_id}")
                return False
            
            # Extract clauses
            clauses = AIService.extract_clauses(text, document_id)
            
            # Generate summary
            summary = AIService.generate_summary(text, document_id)
            
            # Extract obligations
            obligations = AIService.extract_obligations(text, document_id)
            
            # Update document status
            document.status = 'analyzed'
            db.session.commit()
            
            return True
        except Exception as e:
            current_app.logger.error(f"Error analyzing document: {str(e)}")
            return False
    
    @staticmethod
    def extract_clauses(text, document_id):
        """
        Extract clauses from document text.
        
        Args:
            text (str): The document text
            document_id (int): The document ID
            
        Returns:
            list: List of extracted clauses
        """
        AIService.init_openai()
        
        # Truncate text if too long
        max_length = 8000  # Adjust based on token limits
        if len(text) > max_length:
            text = text[:max_length]
        
        try:
            # Define common clause categories
            categories = [
                "Termination",
                "Liability",
                "Confidentiality",
                "Intellectual Property",
                "Payment",
                "Indemnification",
                "Force Majeure",
                "Governing Law",
                "Dispute Resolution",
                "Assignment",
                "Amendment",
                "Entire Agreement",
                "Severability",
                "Notices",
                "Waiver",
                "Counterparts",
                "Term",
                "Representations and Warranties",
                "Compliance with Laws",
                "Insurance",
                "Other"
            ]
            
            # Create prompt for clause extraction
            prompt = f"""
            You are a legal AI assistant specialized in contract analysis. Extract clauses from the following contract text.
            For each clause, identify:
            1. The clause category (choose from: {', '.join(categories)})
            2. The clause text
            3. Any potential risks or issues with the clause
            
            Format your response as a JSON array of objects with the following structure:
            [
                {{
                    "category": "Category name",
                    "text": "Full clause text",
                    "risk_level": "high/medium/low/none",
                    "risk_description": "Description of any risks or issues"
                }}
            ]
            
            Contract text:
            {text}
            """
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a legal AI assistant specialized in contract analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            # Parse response
            content = response.choices[0].message.content
            
            # Extract JSON from response
            json_start = content.find('[')
            json_end = content.rfind(']') + 1
            
            if json_start == -1 or json_end == 0:
                current_app.logger.error("Failed to extract JSON from OpenAI response")
                return []
            
            json_str = content[json_start:json_end]
            clauses_data = json.loads(json_str)
            
            # Save clauses to database
            saved_clauses = []
            for clause_data in clauses_data:
                # Get or create category
                category = ClauseCategory.query.filter_by(name=clause_data['category']).first()
                if not category:
                    category = ClauseCategory(name=clause_data['category'])
                    db.session.add(category)
                    db.session.flush()
                
                # Create clause
                clause = Clause(
                    document_id=document_id,
                    category_id=category.id,
                    text=clause_data['text'],
                    risk_level=clause_data['risk_level'],
                    risk_description=clause_data['risk_description']
                )
                db.session.add(clause)
                saved_clauses.append(clause)
            
            db.session.commit()
            return saved_clauses
        
        except Exception as e:
            current_app.logger.error(f"Error extracting clauses: {str(e)}")
            return []
    
    @staticmethod
    def generate_summary(text, document_id):
        """
        Generate a summary for a document.
        
        Args:
            text (str): The document text
            document_id (int): The document ID
            
        Returns:
            DocumentSummary: The generated summary
        """
        AIService.init_openai()
        
        # Truncate text if too long
        max_length = 8000  # Adjust based on token limits
        if len(text) > max_length:
            text = text[:max_length]
        
        try:
            # Create prompt for summary generation
            prompt = f"""
            You are a legal AI assistant specialized in contract analysis. Generate a comprehensive summary of the following contract.
            Include:
            1. A brief overview of the contract purpose
            2. Key parties involved
            3. Main terms and conditions
            4. Important dates and deadlines
            5. Any notable provisions or unusual terms
            
            Format your response as a JSON object with the following structure:
            {{
                "overview": "Brief overview of the contract",
                "parties": ["Party 1", "Party 2"],
                "key_terms": ["Term 1", "Term 2"],
                "important_dates": ["Date 1: Description", "Date 2: Description"],
                "notable_provisions": ["Provision 1", "Provision 2"]
            }}
            
            Contract text:
            {text}
            """
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a legal AI assistant specialized in contract analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            # Parse response
            content = response.choices[0].message.content
            
            # Extract JSON from response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                current_app.logger.error("Failed to extract JSON from OpenAI response")
                return None
            
            json_str = content[json_start:json_end]
            summary_data = json.loads(json_str)
            
            # Create summary
            summary = DocumentSummary(
                document_id=document_id,
                overview=summary_data['overview'],
                parties=summary_data['parties'],
                key_terms=summary_data['key_terms'],
                important_dates=summary_data['important_dates'],
                notable_provisions=summary_data['notable_provisions']
            )
            db.session.add(summary)
            db.session.commit()
            
            return summary
        
        except Exception as e:
            current_app.logger.error(f"Error generating summary: {str(e)}")
            return None
    
    @staticmethod
    def extract_obligations(text, document_id):
        """
        Extract obligations from document text.
        
        Args:
            text (str): The document text
            document_id (int): The document ID
            
        Returns:
            list: List of extracted obligations
        """
        AIService.init_openai()
        
        # Truncate text if too long
        max_length = 8000  # Adjust based on token limits
        if len(text) > max_length:
            text = text[:max_length]
        
        try:
            # Create prompt for obligation extraction
            prompt = f"""
            You are a legal AI assistant specialized in contract analysis. Extract key obligations and deadlines from the following contract text.
            For each obligation, identify:
            1. The party responsible
            2. The obligation description
            3. The deadline or timeframe (if any)
            4. The consequence of non-compliance (if any)
            
            Format your response as a JSON array of objects with the following structure:
            [
                {{
                    "party": "Party name",
                    "description": "Obligation description",
                    "deadline": "Deadline or timeframe (if any)",
                    "consequence": "Consequence of non-compliance (if any)"
                }}
            ]
            
            Contract text:
            {text}
            """
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a legal AI assistant specialized in contract analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            # Parse response
            content = response.choices[0].message.content
            
            # Extract JSON from response
            json_start = content.find('[')
            json_end = content.rfind(']') + 1
            
            if json_start == -1 or json_end == 0:
                current_app.logger.error("Failed to extract JSON from OpenAI response")
                return []
            
            json_str = content[json_start:json_end]
            obligations_data = json.loads(json_str)
            
            # Save obligations to database
            saved_obligations = []
            for obligation_data in obligations_data:
                obligation = Obligation(
                    document_id=document_id,
                    party=obligation_data['party'],
                    description=obligation_data['description'],
                    deadline=obligation_data['deadline'],
                    consequence=obligation_data['consequence']
                )
                db.session.add(obligation)
                saved_obligations.append(obligation)
            
            db.session.commit()
            return saved_obligations
        
        except Exception as e:
            current_app.logger.error(f"Error extracting obligations: {str(e)}")
            return []
    
    @staticmethod
    def search_document(document_id, query):
        """
        Search a document for a specific query.
        
        Args:
            document_id (int): The document ID
            query (str): The search query
            
        Returns:
            dict: Search results
        """
        AIService.init_openai()
        
        # Get document
        document = Document.query.get(document_id)
        if not document:
            current_app.logger.error(f"Document not found: {document_id}")
            return None
        
        # Get document content
        try:
            # Get file processor based on document type
            processor = FileProcessor.get_processor(document.file_type)
            
            # Extract text from document
            text = processor.extract_text(document.file_path)
            
            if not text:
                current_app.logger.error(f"Failed to extract text from document: {document_id}")
                return None
            
            # Truncate text if too long
            max_length = 8000  # Adjust based on token limits
            if len(text) > max_length:
                text = text[:max_length]
            
            # Create prompt for search
            prompt = f"""
            You are a legal AI assistant specialized in contract analysis. Search the following contract for information related to this query: "{query}"
            
            Return your response as a JSON object with the following structure:
            {{
                "answer": "Direct answer to the query",
                "context": "Relevant clause or section from the contract",
                "explanation": "Brief explanation of the answer"
            }}
            
            If the query cannot be answered based on the contract, indicate that in your answer.
            
            Contract text:
            {text}
            """
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a legal AI assistant specialized in contract analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500
            )
            
            # Parse response
            content = response.choices[0].message.content
            
            # Extract JSON from response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                current_app.logger.error("Failed to extract JSON from OpenAI response")
                return None
            
            json_str = content[json_start:json_end]
            search_result = json.loads(json_str)
            
            # Save search query to database
            from src.models.search_query import SearchQuery
            search_query = SearchQuery(
                document_id=document_id,
                query=query,
                result=search_result
            )
            db.session.add(search_query)
            db.session.commit()
            
            return search_result
        
        except Exception as e:
            current_app.logger.error(f"Error searching document: {str(e)}")
            return None

