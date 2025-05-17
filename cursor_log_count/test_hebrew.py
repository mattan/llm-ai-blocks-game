from countlog import count_log
import json

# Test with Hebrew text
test_text = '''**User**

מה עכשיו הבעיה?

---

**Cursor**

נראה שהשאלה שלך מתייחסת לבעיה בקוד
'''

# Run the analysis
result = count_log(test_text)

# Print the result in a readable format
print(f"Queries count: {result['queries_count']}")
print(f"Exchange rate: {result['exchange_rate']['usd_to_ils']}")
print(f"Exchange rate timestamp: {result['exchange_rate']['timestamp']}")
print("\nComplete result:")
print(json.dumps(result, indent=2, ensure_ascii=False))

assert (result["input"]["chars"]==len("מה עכשיו הבעיה?"))
assert (result["output_total"]["chars"]==len("נראה שהשאלה שלך מתייחסת לבעיה בקוד"))
print("\nTest mode passed!")
