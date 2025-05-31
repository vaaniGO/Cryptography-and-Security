k = 2
n = 4
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

matched_arr1 = []
shift = 0
shift_factor = 1
for i in range (0, required_len):
        matched_arr1.append(((i+shift+shift_factor)%(required_len+1)))
        if ((i+1) >= repeat_times and repeat_times % (i+1) == 0):
            shift_factor = shift_factor + 1
            shift = shift + shift_factor
        else:
            shift = shift + 1
    

# We now have matched all original char positions with their positions in the new str
# There is also another way to do this - if we have k = p, then starting at 1, we
# fill every pth number, once we can't do anymore without exceeding required len, 
# we start at 2 and fill every pth number,... so on and so forth till we reach p and 
# fill every pth number. 
str_arr = []
matched_arr1 = [0]+matched_arr1
matched = [False]*required_len
print(matched_arr1)
str_arr.append(1)
for i in range(1, required_len):
    matched_pos = matched_arr1[i]
    if (matched[i] == True):
         continue
    else :
        matched[i] = True
    str_arr.append(matched_pos)
    # print(c, matched_pos)
    while matched_pos > i and matched[matched_pos] == False:
        print("Matched: ", matched_pos)
        matched[matched_pos] = True
        matched_pos = matched_arr1[matched_pos]
        str_arr.append(matched_pos)

print(str_arr)

    # i = 1, matched_pos = i, while loop doesn't run
    # i = 2, mp= 3, mp != 2, while loop starts, 
de_brujin_string = ""

for elem in str_arr:
     de_brujin_string = de_brujin_string + str(arr1[elem])

print(de_brujin_string)
