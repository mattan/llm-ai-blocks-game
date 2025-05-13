# calculate_value.py
def calculate_empty_list_value(cards, k):
    """
    מחשב את הערך של הרשימה הריקה על פי ההגדרה הרקורסיבית שסופקה,
    עם השינוי שבכל שלב מוחזר המקסימום בין סכום הבחירה הנוכחית לערך הרקורסיבי.

    Args:
        cards (dict): מילון המכיל מספרים כמפתחות והסתברויות כערכים.
                      דוגמה: {10: 0.5, 20: 0.3, 5: 0.2}
        k (int): עומק החיפוש (מספר היעדים של איברים שונים במערך).

    Returns:
        float: הערך המחושב של הרשימה הריקה.
    """
    memo = {}  # מילון לשמירת תוצאות שכבר חושבו (memoization)

    def get_value_recursive(current_selection_tuple):
        # מפתח הממואיזציה יהיה טאפל ממוין של המספרים הנוכחיים,
        # כדי להבטיח שאותו סט של מספרים, גם אם נבחר בסדר שונה, ימופה לאותה תוצאה.
        key = tuple(sorted(list(current_selection_tuple)))

        if key in memo:
            return memo[key]

        current_sum = sum(current_selection_tuple)

        if len(current_selection_tuple) == k:
            # מקרה בסיס: מערך עם k מספרים שונים.
            # הערך הוא סכום המספרים במערך.
            memo[key] = current_sum
            return current_sum

        # שלב רקורסיבי: מערך עם פחות מ-k מספרים.
        # חשב את הערך הצפוי מהמשך הבחירות.
        expected_value_from_recursion = 0.0
        
        for card_num, card_prob in cards.items():
            if card_num not in current_selection_tuple:
                # יוצרים את המערך החדש על ידי הוספת הקלף הנוכחי
                new_selection_list = list(current_selection_tuple)
                new_selection_list.append(card_num)
                
                # קוראים רקורסיבית כדי לקבל את הערך של המערך המורחב
                value_of_extended_selection = get_value_recursive(tuple(new_selection_list))
                
                # מוסיפים לערך הכולל את התרומה של קלף זה
                expected_value_from_recursion += card_prob * value_of_extended_selection
        
        # הערך של המצב הנוכחי הוא המקסימום בין סכום המספרים בבחירה הנוכחית
        # לבין הערך הצפוי שחושב מהמשך הרקורסיה.
        # זה כולל את המקרה של הרשימה הריקה, שם current_sum יהיה 0.
        final_value_for_this_state = max(expected_value_from_recursion, current_sum)
        
        memo[key] = final_value_for_this_state
        return final_value_for_this_state

    # מתחילים את החישוב עבור הרשימה הריקה (טאפל ריק)
    return get_value_recursive(tuple()),memo

