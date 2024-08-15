import hashlib
import itertools


def case_permutations(word):
    substitutions = {"a": "@", "i": "1!", "l": "1Ii", "o": "0", "s": "$5"}

    def variations(char):
        lower = char.lower()
        return lower + char.upper() + substitutions.get(lower, "")

    perms = map(variations, word)
    return ("".join(p) for p in itertools.product(*perms))


def check_word(word, target_hash):
    for perm in case_permutations(word):
        if hashlib.sha1(perm.encode()).hexdigest() == target_hash:
            return perm
    return None


def main():
    target_hash = "d54cc1fe76f5186380a0939d2fc1723c44e8a5f7"

    with open("10k-most-common.txt", "r") as file:
        for line in file:
            word = line.strip()
            result = check_word(word, target_hash)
            if result:
                print(f"Password found: {result}")
                return

    print("Password not found in the dictionary.")


if __name__ == "__main__":
    main()
