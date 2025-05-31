import numpy as np
# A polynomial is represented as a list of floats where poly[n] = coeff of x^n for all 0 <= n < len(poly)

def eval(p, x):
    result = 0
    l = len(p)
    for i in range (0, l):
        result = result + (x**i)*p[i]
    return result

def check_linear_factors(p, deg):
    for i in range(0, deg):
        if (eval(p, i) == 0):
            return False
    return True

def are_polys_equal(p1, p2):
    max_len = max(len(p1), len(p2))
    p1 = np.pad(p1, (0, max_len - len(p1)))
    p2 = np.pad(p2, (0, max_len - len(p2)))
    return np.array_equal(p1, p2)

def get_greater(p1, p2):
    p1 = np.trim_zeros(p1, 'f')
    p2 = np.trim_zeros(p2, 'f')

    if len(p1) > len(p2):
        return p1
    elif len(p2) > len(p1):
        return p2
    else:
        # Same degree, compare lexicographically
        for a, b in zip(p1, p2):
            if a > b:
                return p1
            elif b > a:
                return p2
        return p1  # Equal polynomials

def eval(p, x):
    result = 0
    l = len(p)
    for i in range(0, l):
        result = result + x**i * p[i]  # Fixed: use ** instead of ^
    return result  # Added return

def get_gcd(poly1, poly2):
    # Trim trailing zeros (highest degrees)
    a = np.trim_zeros(poly1, 'b')
    b = np.trim_zeros(poly2, 'b')
    
    # Base case: if b is zero, return normalized a
    if len(b) == 0:
        if len(a) == 0:
            return a, a
        # Normalize to monic polynomial
        leading_coeff = a[-1]
        a_normalized = [x / leading_coeff for x in a]
        return a_normalized, a_normalized
    
    # Reverse coefficients for np.polydiv (needs highest degree first)
    a_rev = a[::-1]
    b_rev = b[::-1]
    
    # Polynomial division
    q_rev, r_rev = np.polydiv(a_rev, b_rev)
    
    # Convert remainder to original format and trim trailing zeros
    r = r_rev[::-1]  # Back to lowest degree first
    r = np.trim_zeros(r, 'b')
    
    # Recursive call with (b, remainder)
    g, _ = get_gcd(b, r)  # g is the GCD
    return g, g

def check_factors(p, deg):
    for i in range(0, deg):
        temp_deg = pow(deg, i)
        poly1 = [0, -1]
        poly1.extend([0]*(temp_deg - 2))
        poly1.append(1)
        g = get_gcd(p, poly1)
        if g != 1:
            return False
    return True

def check_divisibility(p, deg):
    temp = [0, -1].extend([0]*(pow(deg, deg) - 2)).append(1)
    q, r = np.polydiv(temp, p)
    return r == 0

def check_irreducible(p, deg):
    return check_linear_factors(p, deg) and check_factors(p, deg) and check_divisibility(p, deg)

p = [1, -1, 0, 1]
# Represents 1 - x + x^3
print(check_irreducible(p, len(p)-1))
