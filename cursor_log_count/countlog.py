import json
import re
import tiktoken
import datetime
import urllib.request
import ssl
from typing import Dict, Union, List, Tuple

# קבלת שער הדולר העדכני מול השקל
def get_exchange_rate():
    # שימוש ב-API חינמי ללא צורך ברישום
    # יצירת הקשר שלא מאמת תעודות SSL
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    # קריאה ל-API לקבלת שער הדולר העדכני מול השקל
    url = "https://open.er-api.com/v6/latest/USD"
    with urllib.request.urlopen(url, context=ctx) as response:
        data = json.loads(response.read().decode('utf-8'))
        if data.get('result') == 'success' and 'rates' in data and 'ILS' in data['rates']:
            rate = data['rates']['ILS']
            return rate, datetime.datetime.now()
        else:
            raise ValueError("לא ניתן לקבל את שער הדולר מה-API")
    # return 3.67, datetime.datetime.now() # שער ברירת מחדל

def count_tokens(text: str) -> int:
    """חישוב מספר הטוקנים באמצעות ספריית tiktoken"""
    # השתמש בקידוד cl100k_base (משמש את GPT-4 ואחרים)
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    return len(tokens)

def count_log(text: str, test_example_mode=False) -> Union[str, Dict]:
    """
    Analyze a log file and count various metrics including:
    - Number of queries
    - Input characters and tokens
    - Output characters and tokens
    - Output code characters and tokens
    - Output conversation characters and tokens
    - Total output characters and tokens
    - Total characters and tokens
    
    If test_example_mode is True, considers special case for Hebrew text test
    
    Returns a JSON object with the analysis results.
    """
    # Get the current exchange rate and timestamp
    exchange_rate, rate_timestamp = get_exchange_rate()
    
    # Initialize counters
    metrics = {
        "exchange_rate": {
            "usd_to_ils": exchange_rate,
            "timestamp": rate_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        },
        "queries_count": 0,
        "input": {
            "chars": 0,
            "tokens": 0
        },
        "output_code": {
            "chars": 0,
            "tokens": 0
        },
        "output_conversation": {
            "chars": 0,
            "tokens": 0
        },
        "output_total": {
            "chars": 0,
            "tokens": 0
        },
        "total": {
            "chars": 0,
            "tokens": 0
        }
    }
    
    # Add pricing information
    metrics.update({
        "pricing": {
            "cursor": {
                "usd": 0,
                "ils": 0
            },
            "o3_api": {
                "usd": 0,
                "ils": 0
            },
            "claude3_7": {
                "usd": 0,
                "ils": 0
            },
            "gemini_2_5": {
                "usd": 0,
                "ils": 0
            }
        }
    })
    
    # Pattern to identify user queries (starting with "User:" or similar patterns)
    query_patterns = [
        r"^User\s*:",
        r"^Human\s*:",
        r"^Customer\s*:",
        r"^Question\s*:",
        r"^Prompt\s*:",
        r"^\*\*User\*\*",         # For Cursor format: **User**
        r"^\*\*Human\*\*",        # For Cursor format: **Human**
        r"^\*\*User\*\*\s*:",
        r"^\*\*Human\*\*\s*:",
        r"^\s*\d+\s*\.\s*User\s*:"
    ]
    
    # Hebrew pattern for the example file validation - just check for parts of the phrase
    # to be more resilient to potential encoding or whitespace issues
    hebrew_patterns = [
        r"מה",              # "מה" 
        r"עכשיו",       # "עכשיו"
        r"הבעיה"        # "הבעיה"
    ]
    
    # Pattern to identify code blocks
    code_block_pattern = r"```[\s\S]*?```"
    
    # Split text into lines
    lines = text.split('\n')
    
    # Pattern to identify assistant responses (starting with "Cursor:" or similar patterns)
    cursor_patterns = [
        r"^Cursor\s*:",
        r"^Assistant\s*:",
        r"^AI\s*:",
        r"^Response\s*:",
        r"^Answer\s*:",
        r"^\*\*Cursor\*\*",          # For Cursor format: **Cursor**
        r"^\*\*Assistant\*\*",       # For Cursor format: **Assistant**
        r"^\*\*Cursor\*\*\s*:",
        r"^\*\*Assistant\*\*\s*:",
        r"^\s*\d+\s*\.\s*Cursor\s*:"
    ]
    
    # Process each line to identify queries and count metrics
    is_in_query = False
    current_query = ""
    user_queries = []
    
    for line in lines:
        is_query_start = any(re.match(pattern, line, re.IGNORECASE) for pattern in query_patterns)
        is_cursor_start = any(re.match(pattern, line, re.IGNORECASE) for pattern in cursor_patterns)
        
        if is_query_start:
            # New query found
            if is_in_query and current_query:
                user_queries.append(current_query)
            
            metrics["queries_count"] += 1
            is_in_query = True
            current_query = line
        elif is_cursor_start:
            # Cursor/assistant response found - end the current query if we're in one
            if is_in_query and current_query:
                user_queries.append(current_query)
                is_in_query = False
                current_query = ""
        elif is_in_query:
            # Continue adding to the current query as long as we don't hit a cursor response
            current_query += "\n" + line
        
    # Add the last query if there is one
    if is_in_query and current_query:
        user_queries.append(current_query)
    
    # Extract all input text (queries) - remove formatting markers
    # First, join all user queries
    all_input = "\n".join(user_queries)
    
    # Remove query markers and **User** tags
    clean_input = ""
    for line in all_input.split('\n'):
        # Skip lines with query markers or empty lines
        if any(re.match(pattern, line, re.IGNORECASE) for pattern in query_patterns) or line.strip() == "" or line.strip() == "---":
            continue
        clean_input += line + "\n"
    
    # Set the clean input
    metrics["input"]["chars"] = len(clean_input.strip())
    metrics["input"]["tokens"] = count_tokens(clean_input.strip())
    
    # Find code blocks
    code_blocks = re.findall(code_block_pattern, text)
    all_code = "\n".join(code_blocks)
    metrics["output_code"]["chars"] = len(all_code)
    metrics["output_code"]["tokens"] = count_tokens(all_code)
    
    # Calculate conversation output (non-code output)
    non_code_text = text
    for code_block in code_blocks:
        non_code_text = non_code_text.replace(code_block, "")
    
    # Remove user queries from non-code text to get AI response text
    for query in user_queries:
        non_code_text = non_code_text.replace(query, "")
    
    # Clean the output text to contain only actual response content
    clean_output = ""
    is_in_output = False
    for line in non_code_text.split('\n'):
        # Check if this line is a cursor/assistant response marker
        is_cursor_start = any(re.match(pattern, line, re.IGNORECASE) for pattern in cursor_patterns)
        
        if is_cursor_start:
            is_in_output = True
            continue  # Skip the cursor marker line
        
        if line.strip() == "---" or line.strip() == "":
            continue  # Skip separators and empty lines
        
        if is_in_output:
            clean_output += line + "\n"
    
    # Use the clean output for metrics
    metrics["output_conversation"]["chars"] = len(clean_output.strip())
    metrics["output_conversation"]["tokens"] = count_tokens(clean_output.strip())
    
    # Calculate total output
    metrics["output_total"]["chars"] = metrics["output_code"]["chars"] + metrics["output_conversation"]["chars"]
    metrics["output_total"]["tokens"] = metrics["output_code"]["tokens"] + metrics["output_conversation"]["tokens"]
    
    # Calculate total chars and tokens
    metrics["total"]["chars"] = metrics["input"]["chars"] + metrics["output_total"]["chars"]
    metrics["total"]["tokens"] = metrics["input"]["tokens"] + metrics["output_total"]["tokens"]
    
    # Calculate pricing based on new requirements
    
    # Cursor pricing - $0.04 per query
    cursor_usd = metrics["queries_count"] * 0.04
    metrics["pricing"]["cursor"]["usd"] = cursor_usd
    metrics["pricing"]["cursor"]["ils"] = cursor_usd * exchange_rate
    
    # O3 API pricing - infinity queries, $10 per 1M input tokens, $40 per 1M output tokens
    o3_input_price = (metrics["input"]["tokens"] / 1000000) * 10  # $10 per 1M input tokens
    o3_output_price = (metrics["output_total"]["tokens"] / 1000000) * 40  # $40 per 1M output tokens
    o3_usd = o3_input_price + o3_output_price
    metrics["pricing"]["o3_api"]["usd"] = o3_usd
    metrics["pricing"]["o3_api"]["ils"] = o3_usd * exchange_rate
    
    # Claude 3.7 pricing - 2 queries, $3 per 1M input tokens, $15 per 1M output tokens
    claude_query_multiplier = 2  # Each query counts as 2
    claude_query_count = metrics["queries_count"] * claude_query_multiplier
    claude_input_price = (metrics["input"]["tokens"] / 1000000) * 3  # $3 per 1M input tokens
    claude_output_price = (metrics["output_total"]["tokens"] / 1000000) * 15  # $15 per 1M output tokens
    claude_usd = claude_input_price + claude_output_price
    metrics["pricing"]["claude3_7"]["usd"] = claude_usd
    metrics["pricing"]["claude3_7"]["ils"] = claude_usd * exchange_rate
    
    # Gemini 2.5 pricing - 1 query, $2.5 per 1M input tokens, $15 per 1M output tokens
    gemini_query_multiplier = 1  # Each query counts as 1
    gemini_query_count = metrics["queries_count"] * gemini_query_multiplier
    gemini_input_price = (metrics["input"]["tokens"] / 1000000) * 2.5  # $2.5 per 1M input tokens
    gemini_output_price = (metrics["output_total"]["tokens"] / 1000000) * 15  # $15 per 1M output tokens
    gemini_usd = gemini_input_price + gemini_output_price
    metrics["pricing"]["gemini_2_5"]["usd"] = gemini_usd
    metrics["pricing"]["gemini_2_5"]["ils"] = gemini_usd * exchange_rate
    
    # Return the metrics as a JSON object
    return metrics

if __name__ == "__main__":
    # Simple test
    test_log = """
    User: How can I create a simple web app?
    
    I recommend using Flask, which is a lightweight web framework for Python. Here's a simple example:
    
    ```python
    from flask import Flask
    
    app = Flask(__name__)
    
    @app.route('/')
    def hello():
        return "Hello, World!"
        
    if __name__ == '__main__':
        app.run(debug=True)
    ```
    
    Save this code to a file named app.py and run it with `python app.py`.
    """
    
    result = count_log(test_log)
    print(json.dumps(result, indent=2))
