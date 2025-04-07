print(len(
'''
    def is_prime(n):
    """בודק אם מספר הוא ראשוני"""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def print_primes_up_to(limit):
    """מדפיס את כל המספרים הראשוניים עד הגבול המוגדר"""
    for num in range(2, limit + 1):
        if is_prime(num):
            print(num, end=" ")

# הגדר את הגבול כאן
limit = 100
print(f"המספרים הראשוניים עד {limit}:")
print_primes_up_to(limit)
'''
))