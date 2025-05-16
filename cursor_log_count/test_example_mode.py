import json
from countlog import count_log

# Test with Hebrew text matching the pattern
test_text = '''**User**

מה עכשיו הבעיה?

---

**Cursor**

נראה שהשאלה שלך מתייחסת לבעיה בקוד
'''

print("Testing with Hebrew text containing 'מה עכשיו הבעיה?'...")
try:
    # Run with test_example_mode=True to test pattern matching
    result = count_log(test_text, test_example_mode=True)
    print("✓ Success! Hebrew pattern detected correctly.")
    
    # Print some basic metrics
    print(f"Queries count: {result['queries_count']}")
    print(f"Exchange rate: {result['exchange_rate']['usd_to_ils']}")
    print(f"Exchange rate timestamp: {result['exchange_rate']['timestamp']}")
except Exception as e:
    print(f"✗ Test failed: {e}")

# Create a mock test that shouldn't pass pattern validation
invalid_test_text = '''**User**

שאלה אחרת לגמרי

---

**Cursor**

תשובה כלשהי
'''

print("\nTesting with text that doesn't match the Hebrew pattern...")
try:
    # This should raise an exception since it doesn't contain the required pattern
    result = count_log(invalid_test_text, test_example_mode=True)
    print("✗ Test incorrectly passed for invalid text! This is a bug.")
except Exception as e:
    print(f"✓ Expected failure (this is good): {e}")

print("\nTesting complete!")
