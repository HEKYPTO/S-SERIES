import hashlib
import itertools
from concurrent.futures import ThreadPoolExecutor, as_completed

def case_permutations(word):
    substitutions = {
        'a': '@', 'i': '1!', 'l': '1Ii', 'o': '0', 's': '$5'
    }
    
    def char_variations(char):
        lower = char.lower()
        if lower in substitutions:
            return char.lower() + char.upper() + substitutions[lower]
        return char.lower() + char.upper()

    variations = map(char_variations, word)
    return (''.join(combo) for combo in itertools.product(*variations))

def check_word(word, target_hash):
    for variation in case_permutations(word):
        word_hash = hashlib.sha1(variation.encode()).hexdigest()
        if word_hash == target_hash:
            return variation
    return None

def main():
    target_hash = "d54cc1fe76f5186380a0939d2fc1723c44e8a5f7"

    with ThreadPoolExecutor() as executor:
        futures = []
        with open("10k-most-common.txt", "r") as file:
            for line in file:
                word = line.strip()
                future = executor.submit(check_word, word, target_hash)
                futures.append(future)

        for future in as_completed(futures):
            result = future.result()
            if result:
                print(f"Password found: {result}")
                executor.shutdown(wait=False, cancel_futures=True)
                return

    print("Password not found in the dictionary.")

if __name__ == "__main__":
    main()