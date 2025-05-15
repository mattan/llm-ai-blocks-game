import json
import re
from typing import Dict, Union, List, Tuple

def count_tokens(text: str) -> int:
    """Estimate token count using a simple approximation method."""
    # Simple approximation: about 4 characters per token in English/mixed text
    return len(text) // 4

def count_log(text: str) -> Union[str, Dict]:
    """
    Analyze a log file and count various metrics including:
    - Number of queries
    - Input characters and tokens
    - Output code characters and tokens
    - Output conversation characters and tokens
    - Total output characters and tokens
    - Total characters and tokens
    
    Returns a JSON object with the analysis results.
    """
    # Initialize counters
    metrics = {
        "queries_count": 0,
        "input_chars": 0,
        "input_tokens": 0,
        "output_code_chars": 0,
        "output_code_tokens": 0,
        "output_conversation_chars": 0,
        "output_conversation_tokens": 0,
        "output_total_chars": 0,
        "output_total_tokens": 0,
        "total_chars": 0,
        "total_tokens": 0
    }
    
    # Add pricing information
    metrics.update({
        "price_coursera": 0,
        "price_o3_api": 0,
        "price_claude3_7": 0,
        "price_gemini_2_5": 0
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
    
    # Pattern to identify code blocks
    code_block_pattern = r"```[\s\S]*?```"
    
    # Split text into lines
    lines = text.split('\n')
    
    # Process each line to identify queries and count metrics
    is_in_query = False
    current_query = ""
    user_queries = []
    
    for line in lines:
        is_query_start = any(re.match(pattern, line, re.IGNORECASE) for pattern in query_patterns)
        
        if is_query_start:
            # New query found
            if is_in_query and current_query:
                user_queries.append(current_query)
            
            metrics["queries_count"] += 1
            is_in_query = True
            current_query = line
        elif is_in_query:
            current_query += "\n" + line
        
    # Add the last query if there is one
    if is_in_query and current_query:
        user_queries.append(current_query)
    
    # Extract all input text (queries)
    all_input = "\n".join(user_queries)
    metrics["input_chars"] = len(all_input)
    metrics["input_tokens"] = count_tokens(all_input)
    
    # Find code blocks
    code_blocks = re.findall(code_block_pattern, text)
    all_code = "\n".join(code_blocks)
    metrics["output_code_chars"] = len(all_code)
    metrics["output_code_tokens"] = count_tokens(all_code)
    
    # Calculate conversation output (non-code output)
    non_code_text = text
    for code_block in code_blocks:
        non_code_text = non_code_text.replace(code_block, "")
    
    # Remove user queries from non-code text to get AI response text
    for query in user_queries:
        non_code_text = non_code_text.replace(query, "")
    
    metrics["output_conversation_chars"] = len(non_code_text)
    metrics["output_conversation_tokens"] = count_tokens(non_code_text)
    
    # Calculate total output
    metrics["output_total_chars"] = metrics["output_code_chars"] + metrics["output_conversation_chars"]
    metrics["output_total_tokens"] = metrics["output_code_tokens"] + metrics["output_conversation_tokens"]
    
    # Calculate total chars and tokens
    metrics["total_chars"] = metrics["input_chars"] + metrics["output_total_chars"]
    metrics["total_tokens"] = metrics["input_tokens"] + metrics["output_total_tokens"]
    
    # Calculate pricing
    # Coursera pricing (per query)
    metrics["price_coursera"] = metrics["queries_count"] * 0.002  # Assumed $0.002 per query
    
    # O3 API pricing (per 1000 tokens)
    metrics["price_o3_api"] = (metrics["total_tokens"] / 1000) * 0.015  # Assumed $0.015 per 1000 tokens
    
    # Claude 3.7 pricing 
    claude_input_price = (metrics["input_tokens"] / 1000) * 0.015  # $0.015 per 1K input tokens
    claude_output_price = (metrics["output_total_tokens"] / 1000) * 0.075  # $0.075 per 1K output tokens
    metrics["price_claude3_7"] = claude_input_price + claude_output_price
    
    # Gemini 2.5 pricing
    gemini_input_price = (metrics["input_tokens"] / 1000) * 0.0035  # $0.0035 per 1K input tokens
    gemini_output_price = (metrics["output_total_tokens"] / 1000) * 0.0035  # $0.0035 per 1K output tokens
    metrics["price_gemini_2_5"] = gemini_input_price + gemini_output_price
    
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
