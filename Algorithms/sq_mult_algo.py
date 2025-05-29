m = 2
e = 42 # reduces steps from e to log e
n = 15

# This is just for large numbers so we start by at least squaring the number.

def get_bin(num):
    if (num == 0): 
        return ""
    else:
        # Compute the binary in reverse for easier manipulation later
        return str(num%2)+""+get_bin(num//2)
    
print(get_bin(e))
count = 1

# This is correct, this algorithm only reduces the no. of steps, not the size of the values being dealt with
def compute(bin, m, n, res):
    p = pow(m, 2)
    if(bin == ""):
        return res
    elif (bin[0] == '1'):
        # If the bit = 1, then we consider m*p%n in the result, else we skip it and just square and leave
        return compute(bin[1:], p, n, res*p%n)
    else:
        return compute(bin[1:], p, n, res)


print(compute(get_bin(e)[1:], m, n, 1))
# print(compute_2(get_bin(e)[1:], m, n, 1))