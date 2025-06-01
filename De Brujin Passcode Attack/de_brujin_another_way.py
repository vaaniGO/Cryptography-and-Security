# These packages are used in the correctness test
from collections import Counter
from itertools import product
k = 7
n = 3
# This is basically like wanting all 3 tuples where elements are in {a, b}. There are 2^3 = 8 such tuples
# Let's use the graphical construct, not the Mantel's algorithm construct this time

required_len = pow(k, n)

# We want to 'split' equally among all members of the key space
repeat_times = required_len // k
arr1 = [i for i in range(0, k) for _ in range(repeat_times)]
print(arr1)

sample_unit = [i for i in range(0, k)]
arr2 = sample_unit * (required_len // k)
print(arr2)

matched_arr1 = [0]*(required_len+1)
shift = 1
shift_factor = 1 # 2 
start_shift = 0
for i in range (1, required_len+1):
        # if (matched_arr1[i] != 0): # Already done through pairwise, so no need to compute anything
        #      continue
        matched_pos = (shift_factor)
        print("Matched position for ", i, "is: ", matched_pos)
        matched_arr1[i] = matched_pos 
        shift_factor = shift_factor + k 
        if (i % (repeat_times) == 0):
             start_shift = start_shift + 1
             shift_factor = start_shift + 1

# We now have matched all original char positions with their positions in the new str
# if we have k = p, then starting at 1, we
# fill every pth number, once we can't do anymore without exceeding required len, 
# we start at 2 and fill every pth number,... so on and so forth till we reach p and 
# fill every pth number. 
str_arr = [0]
print("Matched array: ", matched_arr1)
matched = [False]*(required_len+1)

for i in range(1, required_len+1):
    matched_pos = matched_arr1[i] # Returns the corresponding matching of the ith char 
    if (matched[i] == True): # We have to do nothing if the node has already ben visited
         continue 
    else :
        matched[i] = True # We visit the node
        str_arr.append(i) # Add it to the string
    
    if (matched[matched_pos] == False):
        while matched[matched_pos] == False: # Iteratively traverse the graph
            matched[matched_pos] = True
            str_arr.append(matched_pos)
            matched_pos = matched_arr1[matched_pos]
    else:
         continue
    # print(c, matched_pos)

print("String_arr", str_arr)

    # i = 1, matched_pos = i, while loop doesn't run
    # i = 2, mp= 3, mp != 2, while loop starts, 
de_brujin_string = ""

for elem in str_arr[1: ]:
     de_brujin_string = de_brujin_string + str(arr1[elem-1])

print(de_brujin_string)

# Correctness test below: 

s = de_brujin_string

# Consider it cyclic
s_cyclic = s + s[:n-1]

# Generate all substrings of length n
substrings = [s_cyclic[i:i+n] for i in range(len(s))]
substring_counts = Counter(substrings)

# Generate the expected set of substrings using all k^n combinations
alphabet = [str(i) for i in range(k)]
expected_subs = {''.join(p) for p in product(alphabet, repeat=n)}

# Report
print("Unique substrings found:", len(substring_counts))
print("Expected unique substrings:", len(expected_subs))

# Check for repeated substrings
repeated = {sub: count for sub, count in substring_counts.items() if count > 1}
if repeated:
    print("Repeated substrings and their counts:", repeated)
else:
    print("No repeated substrings")

# Check for missing substrings
missing = expected_subs - set(substring_counts)
if missing:
    print("Missing substrings:", missing)
else:
    print("All substrings present")

