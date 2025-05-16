import re
import json

def simplified_count_log(text):
    """Simplified version of count_log to test basic query detection"""
    # Pattern to identify user queries
    query_patterns = [
        r"^\*\*User\*\*",         # For Cursor format: **User**
        r"^User\s*:"              # For standard format: User:
    ]
    
    # Hebrew pattern for example file validation
    hebrew_query_pattern = r"מה עכשיו הבעיה\?"
    
    # Count the queries
    lines = text.split('\n')
    queries_count = 0
    queries = []
    
    is_in_query = False
    current_query = ""
    
    for line in lines:
        is_query_start = any(re.match(pattern, line) for pattern in query_patterns)
        
        if is_query_start:
            # New query found
            if is_in_query and current_query:
                queries.append(current_query)
            
            queries_count += 1
            is_in_query = True
            current_query = line
        elif is_in_query:
            current_query += "\n" + line
    
    # Add the last query if there is one
    if is_in_query and current_query:
        queries.append(current_query)
    
    # Check for Hebrew pattern
    contains_hebrew = False
    if queries:
        for query in queries:
            if re.search(hebrew_query_pattern, query):
                contains_hebrew = True
                break
    
    return {
        "queries_count": queries_count,
        "queries": queries,
        "contains_hebrew_pattern": contains_hebrew
    }

# Test with Hebrew text
test_text = '''**User**

מה עכשיו הבעיה?

---

**Cursor**

נראה שהשאלה שלך מתייחסת לבעיה בקוד
'''

# Run the analysis
result = simplified_count_log(test_text)

# Print the result
print(f"Queries count: {result['queries_count']}")
print(f"Contains Hebrew pattern: {result['contains_hebrew_pattern']}")
print("\nQueries found:")
for i, query in enumerate(result['queries']):
    print(f"Query {i+1}: {query[:50]}...")

print("\nComplete result:")
print(json.dumps(result, indent=2, ensure_ascii=False))
