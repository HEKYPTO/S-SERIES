import hashlib
import itertools
import time

subs = {"a": "@", "i": "1!", "l": "1Ii", "o": "0", "s": "$5"}

def hash_permutations(word):
    perms = (
        "".join(p)
        for p in itertools.product(
            *(c.lower() + c.upper() + subs.get(c.lower(), "") for c in word.strip())
        )
    )
    return {p: hashlib.sha1(p.encode()).hexdigest() for p in perms}

def create_table(words):
    table = {}
    for word in words:
        table.update(hash_permutations(word))
    return table

def main():
    with open("10k-most-common.txt") as file:
        words = file.readlines()

    num_trials = 10
    times, sizes = [], []

    for i in range(num_trials):
        print(f"Running trial {i + 1}/{num_trials}")
        start_time = time.time()
        table = create_table(words)
        end_time = time.time()

        times.append(end_time - start_time)
        sizes.append(len(table))

    print("\nAverage Results over 10 trials:")
    print(f"Average creation time: {sum(times) / num_trials:.4f} seconds")
    print(f"Average table size: {sum(sizes) / num_trials:.0f} entries")
    print(f"Average hash time : {sum(times) / sum(sizes):.9f} seconds")

if __name__ == "__main__":
    main()
