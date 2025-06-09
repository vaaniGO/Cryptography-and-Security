import sys
import math
from bisect import bisect_left

# Set a constant for the maximum denominator to consider.
# d is roughly sqrt(k * pi^2 / 3).
# For k ~ 1.2e10,
MAX_D = 220001

phi = list(range(MAX_D))
total_counts = [0] * MAX_D

def precompute():
    global phi, total_counts

    phi[1] = 1
    for i in range(2, MAX_D):
        if phi[i] == i:  # means i is a prime number
            for j in range(i, MAX_D, i):
                # This update is based on the formula: phi(n) = n * product(1 - 1/p)
                # for all distinct prime factors p of n.
                phi[j] -= phi[j] // i

    total_counts[0] = 0  
    total_counts[1] = 2  
    for i in range(2, MAX_D):
        total_counts[i] = total_counts[i-1] + phi[i]

def solve():
    search_list = total_counts[1:MAX_D]

    for line in sys.stdin:
        try:
            k = int(line.strip())
        except (IOError, ValueError):
            break
            
        if k == 0:
            break

        # `bisect_left` finds the index where `k` would be inserted.
        d_idx = bisect_left(search_list, k)
        d = d_idx + 1

        prev_count = total_counts[d - 1]
        k_prime = k - prev_count

        if d == 1:
            n = k_prime - 1
        else:
            count = 0
            n = 0
            for n_candidate in range(1, d + 1):
                if math.gcd(n_candidate, d) == 1:
                    count += 1
                    if count == k_prime:
                        n = n_candidate
                        break
        
        print(f"{n}/{d}")

if __name__ == "__main__":
    precompute()
    solve()
