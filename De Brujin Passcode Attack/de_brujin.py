import numpy as np
import galois

passcode = list(map(int, input("Enter passcode: ")))
k = int(input("Enter alphabet size: "))
n = len(passcode) # Passcode size, also the required degree of the irreducable polynomial

kSpace = [i for i in range (0, k+1)]  # Alphabet space 

# x : int, poly: [int], poly[0] = coeff of x^k
def eval(x, poly):
    result = 0
    deg = k
    print(poly)
    for c in poly:
        result = result + c * pow(x, deg)
        deg = deg-1
    return result

def choose_poly(base, deg):
    return galois.GF(base**deg, repr="poly")

# deg : int 
def get_all_polys(base, deg):
    if deg == 0:
        return [[elem] for elem in kSpace]
    else:
        new_space = []
        for char in kSpace:
            for p in get_all_polys(deg-1):
                temp = [char]
                temp.extend(p)
                print("Temp:", temp)
                new_space.append(temp)
        return new_space

# pol1y: [int], poly2: [int], poly[0] = coeff of x^k, poly[1] = coeff of x^k-1 ... 
def divides(poly1, poly2):
    print(poly1, poly2)
    q, r = np.polydiv(poly1, poly2)
    # Check if remainder is zero (or very close to zero, for floats)
    return np.allclose(r, 0)

def find_coeffs():
    c = []
    # Now we want that our chosen polynomial does not evaluate to 0 for any x in gp_p
    poly = choose_poly(k, n).irreducible_poly.coeffs # Get a polynomial of degree k
    l = len(poly)
    for i in range (0, l):
        c.append(int(poly[i]))
    return c

def get_next_char(a, c):
    if a == [0]*n:
        return c[0]
    elif a == [1].extend([0]*(n-1)):
        return 0
    else:
        result = 0
        l = len(a)
        for i in range(0, l):
            result = result + a[i]*c[i]
        return result%k

def get_string():
    lim = pow(k, n)
    s = str(kSpace[0]) * n
    a = [kSpace[0]] * n
    ind = 0
    found = -1
    c = find_coeffs()
    # print("C: ", c)
    for i in range (0, lim):
        if a[ind : ind+n] == passcode and found == -1:
            found = ind+n
        next_char = get_next_char(a[ind : ind+n], c)
        s = s + str(next_char)
        a.append(next_char)
        ind += 1
    return s, found

de_bruj_seq, ind = get_string()
print("De Brujin sequence: ",de_bruj_seq)
print("String entered till the attack is successful: ",de_bruj_seq[0:ind])
print("No. of keystrokes before success: ", ind)