import json
import unittest
import re
from countlog import count_log

class TestCountLog(unittest.TestCase):
    def test_count_log_from_file(self):
        # Read the test_example.md file
        with open('test_example.md', 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Debug - print first few lines of content
        print("First 200 characters of file:")
        print(content[:200])
            
        # Debug - Find query patterns in the content
        query_patterns = [
            r"^User\s*:",
            r"^Human\s*:",
            r"^Customer\s*:",
            r"^Question\s*:",
            r"^Prompt\s*:",
            r"^\*\*User\*\*\s*:",
            r"^\*\*Human\*\*\s*:",
            r"^\s*\d+\s*\.\s*User\s*:"
        ]
        
        # Count matches manually for debugging
        lines = content.split('\n')
        query_count = 0
        query_lines = []
        
        for i, line in enumerate(lines):
            is_query_start = any(re.match(pattern, line, re.IGNORECASE) for pattern in query_patterns)
            if is_query_start:
                query_count += 1
                query_lines.append(f"Line {i+1}: {line[:50]}...")
        
        print(f"\nFound {query_count} queries manually:")
        for line in query_lines:
            print(line)
        
        # Run the count_log function
        result = count_log(content)
        
        # Validate that it's valid JSON
        try:
            json_result = json.loads(result) if isinstance(result, str) else result
        except json.JSONDecodeError:
            self.fail("Result is not valid JSON")
        
        # Print the result for verification
        print("\nResults from count_log function:")
        print(json.dumps(json_result, indent=2))
        
        # Assert that queries count is 7
        self.assertEqual(json_result.get('queries_count'), 7, 
                         "Expected 7 queries in the example file, but found {}".format(json_result.get('queries_count')))
        
        return json_result

if __name__ == '__main__':
    unittest.main()
