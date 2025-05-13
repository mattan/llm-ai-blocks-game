# test_calculate_value.py
import sys
sys.path.append("/home/ubuntu") # Ensure the calculate_value module can be found
from calculate_value import calculate_empty_list_value
from itertools import groupby

N = 12 + 1
cards_sum = sum(range(N))
cards_example_6 = {n:n/cards_sum for n in range(1,N)}

k_example_6 = 7
value_example_6,all = calculate_empty_list_value(cards_example_6, k_example_6)
print(f"\nTest Case 5: cards = {cards_example_6}, k = {k_example_6}")
print(f"Calculated value: {value_example_6}, Expected: ???")

def calc(item):
    return item[1]-sum(item[0])

all_sorted = sorted(all.items(), key=lambda item: (-sum(item[0]),item[1]))
for sub_all in groupby(all_sorted,key=lambda item: -sum(item[0])):
    print(-sub_all[0],end=":")
    
    arr = list(sub_all[1])

    if calc(arr[-1])>0 and calc(arr[0])>0:
        print("ALL GO")
        continue

    if calc(arr[-1])==0 and calc(arr[0])==0:
        print("ALL STOP")
        continue

    #for cards_list, val in sub_all[1]:
    for example in (range(len(arr)) if -sub_all[0] in [21,22,23] else [0,-1]):
        cards_list, val = arr[example]
        print(f"{cards_list} => {val - sum(cards_list)} ({val} - {sum(cards_list)})")
    
print(f"Calculated value: {value_example_6}, Expected: ???")