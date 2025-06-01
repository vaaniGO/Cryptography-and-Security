k = 7
n = 2
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
halfway = required_len//2
start_shift = 0
for i in range (1, required_len+1):
        # if (matched_arr1[i] != 0): # Already done through pairwise, so no need to compute anything
        #      continue
        matched_pos = (shift_factor)
        print("Matched position for ", i, "is: ", matched_pos)
        matched_arr1[i] = matched_pos
        matched_arr1[matched_pos] = i     
        shift_factor = shift_factor + k 
        if (i % (repeat_times) == 0):
             start_shift = start_shift + 1
             shift_factor = start_shift + 1
# i = 1 OK matched to 1, sf = 4
# i = 2 OK matched to 4, sf = 7
# i = 3 OK matched to 7, sf = 10
# i = 4, OK sf = 1, start_shift = 1, matched to 2, sf = 4
# i = 5, OK matched to 5, sf = 7
# i = 6, OK matched to 8, sf = 10
# i = 7, OK 
# i = 8, OK
# i = 9, 



# We now have matched all original char positions with their positions in the new str
# There is also another way to do this - if we have k = p, then starting at 1, we
# fill every pth number, once we can't do anymore without exceeding required len, 
# we start at 2 and fill every pth number,... so on and so forth till we reach p and 
# fill every pth number. 
str_arr = []
print("Matched array: ", matched_arr1)
matched = [False]*(required_len+1)

for i in range(1, required_len):
    matched_pos = matched_arr1[i]
    if (matched[i] == True):
         continue
    else :
        matched[i] = True
        str_arr.append(i)
    str_arr.append(matched_pos)
    # print(c, matched_pos)
    while matched[matched_pos] == False:
        matched[matched_pos] = True
        matched_pos = matched_arr1[matched_pos]
        str_arr.append(matched_pos)

print("String_arr", str_arr)

    # i = 1, matched_pos = i, while loop doesn't run
    # i = 2, mp= 3, mp != 2, while loop starts, 
de_brujin_string = ""

for elem in str_arr:
     de_brujin_string = de_brujin_string + str(arr1[elem])

print(de_brujin_string)

# Correctness test below: 

s = de_brujin_string

# Consider it cyclic
s_cyclic = s + s[:n-1]

substrings = [s_cyclic[i:i+n] for i in range(len(s)+1)]
unique_subs = set(substrings)

print(len(unique_subs))  # Should be 49
