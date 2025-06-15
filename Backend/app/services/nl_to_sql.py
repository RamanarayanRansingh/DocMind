# app/services/nl_to_sql.py
import sqlite3
from typing import Tuple, List, Dict, Any
import requests
import re
import logging
from app.config import settings

class NLToSQLService:
    def __init__(self):
        self.db_path = "Chinook.db"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.api_key = settings.GROQ_API_KEY
        self.model = "llama-3.3-70b-versatile"
        
    def get_table_schema(self) -> str:
        """Get the database schema information."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get tables and their columns
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        schema_info = []
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            columns_info = [f"{col[1]} ({col[2]})" for col in columns]
            schema_info.append(f"Table {table_name}:\n" + "\n".join(columns_info))
        
        # Add some example queries to help guide the model
        schema_info.append("""
Example Queries:
1. Count albums by artist: SELECT COUNT(a.AlbumId) as album_count FROM Album a JOIN Artist ar ON a.ArtistId = ar.ArtistId WHERE ar.Name = 'Artist Name';
2. Find tracks by artist: SELECT t.Name FROM Track t JOIN Album a ON t.AlbumId = a.AlbumId JOIN Artist ar ON a.ArtistId = ar.ArtistId WHERE ar.Name = 'Artist Name';
""")
        
        conn.close()
        return "\n\n".join(schema_info)
    
    def fix_quotes(self, query: str) -> str:
        """Ensure all string literals are properly quoted."""
        def replace_quotes(match):
            content = match.group(1)
            return f"'{content}'"
            
        # Fix incomplete quotes at the end of the query
        if query.count("'") % 2 != 0:
            query += "'"
            
        return query
    
    def clean_sql_query(self, query: str) -> str:
        """Clean the SQL query by removing markdown formatting and other artifacts."""
        # Remove markdown and code blocks
        query = re.sub(r'```sql\s*', '', query)
        query = re.sub(r'```\s*', '', query)
        query = re.sub(r'`.*`\s*', '', query)
        
        # Basic cleaning
        query = query.strip()
        query = query.strip('"\'')
        
        # Replace smart quotes with regular quotes
        query = query.replace('"', '"').replace('"', '"')
        query = query.replace("'", "'").replace("'", "'")
        
        # Extract just the SQL query
        if 'SELECT' in query.upper():
            query = query[query.upper().find('SELECT'):]
            
        # Ensure the query ends with a semicolon
        query = query.rstrip(';') + ';'
        
        # Fix quotes
        query = self.fix_quotes(query)
        
        logging.debug(f"Cleaned query: {query}")
        return query

    def generate_natural_response(self, natural_query: str, results: List[Dict[str, Any]]) -> str:
        """Generate a natural language response from the query results."""
        prompt = f"""Convert these database query results into a natural language response.

Original question: "{natural_query}"

Query results: {results}

Rules:
1. Respond in a conversational, helpful tone
2. Include specific numbers and details from the results
3. Format any lists or enumerations naturally
4. Keep the response concise but informative
5. Return only the natural language response, no additional explanations

Generate the response:"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that converts database query results into natural language responses."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7  # Slightly higher temperature for more natural responses
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            
            natural_response = response.json()["choices"][0]["message"]["content"].strip()
            logging.info(f"Generated natural response: {natural_response}")
            
            return natural_response
            
        except Exception as e:
            logging.error(f"Error in generate_natural_response: {str(e)}")
            raise
    
    def generate_sql_query(self, natural_query: str) -> Tuple[str, List[Dict[str, Any]], str]:
        """Convert natural language to SQL query using Groq API and return natural language response."""
        schema = self.get_table_schema()
        
        example_query = """Example: For the query "number of albums by AC/DC", the correct SQL is:
SELECT COUNT(a.AlbumId) as album_count FROM Album a JOIN Artist ar ON a.ArtistId = ar.ArtistId WHERE ar.Name = 'AC/DC';"""
        
        prompt = f"""You are an SQL expert. Convert this natural language query to a valid SQLite query using this schema:

{schema}

{example_query}

Query to convert: "{natural_query}"

Rules:
1. Use single quotes for string literals
2. Always close string literals with a quote
3. Include proper table aliases in joins
4. End the query with a semicolon
5. Return only the SQL query, no explanations

Return the SQL query:"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an SQL expert. Return only valid SQLite queries with proper string quoting and table joins."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            
            sql_query = response.json()["choices"][0]["message"]["content"].strip()
            sql_query = self.clean_sql_query(sql_query)
            
            logging.info(f"Generated SQL query: {sql_query}")
            
            # Execute the query
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(sql_query)
            results = [dict(row) for row in cursor.fetchall()]
            
            conn.close()

            # Generate natural language response
            natural_response = self.generate_natural_response(natural_query, results)
            
            return sql_query, results, natural_response
            # return sql_query,natural_response
            
        except Exception as e:
            logging.error(f"Error in generate_sql_query: {str(e)}")
            raise