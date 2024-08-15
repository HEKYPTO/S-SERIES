# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True

import hashlib
import itertools
import time
from cpython cimport array
import array

cdef dict subs = {"a": "@", "i": "1!", "l": "1Ii", "o": "0", "s": "$5"}

cdef bytes sha1_hash(str s):
    return hashlib.sha1(s.encode()).hexdigest().encode()

cdef dict hash_permutations(str word):
    cdef:
        list chars = []
        str c, perm_str
        tuple perm
        bytes hash_value
        dict result = {}
    
    word = word.strip()  
    if not word:
        return result
    
    chars = [c.lower() + c.upper() + subs.get(c.lower(), "") for c in word]
    
    for perm in itertools.product(*chars):
        perm_str = ''.join(perm)
        hash_value = sha1_hash(perm_str)
        result[perm_str] = hash_value
    
    return result

cdef dict create_table(list words):
    cdef:
        dict table = {}
        dict word_perms
        str word
    
    for word in words:
        word_perms = hash_permutations(word)
        table.update(word_perms)
    
    return table

def main():
    cdef:
        list words
        int num_trials = 10
        double[:] times = array.array('d', [0] * num_trials)
        long long[:] sizes = array.array('q', [0] * num_trials)
        int i
        double start_time, end_time
        dict table
    
    with open("../10k-most-common.txt", "r") as file:
        words = file.readlines()
    
    for i in range(num_trials):
        print(f"Running trial {i + 1}/{num_trials}")
        start_time = time.time()
        table = create_table(words)
        end_time = time.time()
        
        times[i] = end_time - start_time
        sizes[i] = len(table)
    
    cdef:
        double avg_time = sum(times) / num_trials
        double avg_size = sum(sizes) / num_trials
        double avg_hash_time = sum(times) / sum(sizes)
    
    print("\nAverage Results:")
    print(f"Average creation time: {avg_time:.4f} seconds")
    print(f"Average table size: {avg_size:.0f} entries")
    print(f"Average hash time : {avg_hash_time:.9f} seconds")

if __name__ == "__main__":
    main()
