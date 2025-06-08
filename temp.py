def are_digit_rearrangements(num1, num2):
    """
    בודק אם שני מספרים הם אותו מספר עם סדר ספרות שונה
    """
    return sorted(str(num1)) == sorted(str(num2))

def find_numbers_with_digit_rearrangement(K, max_num=100000):
    """
    מוצא מספרים שכאשר מכפילים אותם במספר בין 1 ל-K,
    מקבלים את אותו מספר עם סדר ספרות אחר עבור כל כפל
    
    Args:
        K: הגבול העליון לכפל
        max_num: המספר המקסימלי לבדיקה
    
    Returns:
        רשימה של מספרים שמקיימים את התנאי לכל מספר בין 1 ל-K
    """
    results = []
    
    for num in range(1, max_num + 1):
        all_match = True
        matches = []
        
        # בודק כפל עם כל מספר מ-1 עד K
        for multiplier in range(1, K + 1):
            product = num * multiplier
            
            # בודק אם התוצאה היא סידור מחדש של הספרות
            if are_digit_rearrangements(num, product):
                matches.append((multiplier, product))
            else:
                all_match = False
                break  # אם אחד לא מקיים, אין צורך להמשיך
        
        # רק אם כל הכפולות מקיימות את התנאי
        if all_match:
            results.append({
                'number': num,
                'matches': matches
            })
    
    return results

def print_results(results):
    """
    מדפיס את התוצאות בצורה ברורה
    """
    if len(results) == 0:
        print("לא נמצאו מספרים שמקיימים את התנאי.")
        return
        
    print(f"נמצאו {len(results)} מספרים שמקיימים את התנאי לכל הכפולות:\n")
    
    for result in results:
        num = result['number']
        matches = result['matches']
        
        print(f"המספר {num}:")
        for multiplier, product in matches:
            print(f"  {num} × {multiplier} = {product}")
        print()

def check_specific_number(num, K):
    """
    בודק מספר ספציפי - האם מקיים את התנאי לכל מספר בין 1 ל-K
    """
    print(f"בדיקת המספר {num} עם K={K}:")
    all_valid = True
    
    for multiplier in range(1, K + 1):
        product = num * multiplier
        if are_digit_rearrangements(num, product):
            print(f"  {num} × {multiplier} = {product} ✓")
        else:
            print(f"  {num} × {multiplier} = {product} ✗")
            all_valid = False
    
    print(f"\nהמספר {num} {'מקיים' if all_valid else 'לא מקיים'} את התנאי עבור K={K}")
    return all_valid

# דוגמאות שימוש
if __name__ == "__main__":
    # בדיקה עם K=3
    print("חיפוש עם K=6:")
    results = find_numbers_with_digit_rearrangement(K=6, max_num=1000000)
    print_results(results)
    
    print("\n" + "="*50 + "\n")
    
        # בדיקה עם K=3
    print("חיפוש עם K=7:")
    results = find_numbers_with_digit_rearrangement(K=7, max_num=10000000000)
    print_results(results)
    
    print("\n" + "="*50 + "\n")
    
    

# פונקציה לבדיקת מספר ספציפי
def check_specific_number(num, K):
    """
    בודק מספר ספציפי - האם מקיים את התנאי לכל מספר בין 1 ל-K
    """
    print(f"בדיקת המספר {num} עם K={K}:")
    all_valid = True
    
    for multiplier in range(1, K + 1):
        product = num * multiplier
        if are_digit_rearrangements(num, product):
            print(f"  {num} × {multiplier} = {product} ✓")
        else:
            print(f"  {num} × {multiplier} = {product} ✗")
            all_valid = False
    
    print(f"\nהמספר {num} {'מקיים' if all_valid else 'לא מקיים'} את התנאי עבור K={K}")
    return all_valid