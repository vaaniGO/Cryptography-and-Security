# De Bruijn Sequence and Passcode Security

## 📘 Overview

We consider a system where an **n-length passcode** is formed from an **alphabet of size \( k \)** (i.e., \( k \) unique characters). The machine unlocks when the correct passcode appears as a **contiguous substring** of the input stream.

**Example:**  
If the passcode is `'AABA'` and the entered string is `'CCDAABA'`, the lock opens because the passcode appears in order.

---

## 🔒 Motivation: What Increases Security?

We compare two methods to increase brute-force resistance:

1. **Requiring a terminating character**  
2. **Increasing the passcode length**

### Approximate Growth:
- Adding a **terminating character** increases brute-force difficulty by a factor of **n**
- Increasing the **passcode length** increases difficulty by a factor of **k**

So, when \( k > n \), increasing the passcode length is the better option for enhancing security.

---

## ✅ Assumption

We assume that we can **wrap around** the sequence.  
- There are \( k^n \) valid combinations.
- To cover all combinations, we need a string of length at least \( k^n \).
- We wrap the last \( n-1 \) characters to ensure that all starting substrings are included.

---

## 🔄 Generating a De Bruijn Sequence

We want to find a **primitive polynomial** of degree \( n \) over the finite field \( GF(k) \).

### Requirements for the Polynomial:
- It must be **irreducible**.
- It must be **monic** (leading coefficient of \( x^n \) is 1).
- It must have a **root a** that is a **generator** of \( GF(k^n)^* \) (i.e., it must be a primitive polynomial).

When arranged in decreasing powers of \( x \), the polynomial has:
- A leading 1 for \( x^n \)
- The remaining coefficients are negated and used to generate the sequence.

---

## 🔧 Generating the Sequence

Given:
- `a`: current state (a list of the last `n` characters)
- `c`: coefficient array from the primitive polynomial

```python
def get_next_char(a, c):
    # a is the list of last n characters
    # c is the coefficient array
    if a == [0] * n:
        return c[0]
    elif a == [1] + [0] * (n - 1):
        return 0
    else:
        result = 0
        l = len(a)
        for i in range(l):
            result += a[i] * c[i]
        return result % k
