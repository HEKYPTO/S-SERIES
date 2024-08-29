import nltk
from nltk.corpus import words, brown
from nltk.probability import FreqDist
from nltk import ngrams
import re
from functools import lru_cache
from tqdm import tqdm
from IPython.display import clear_output

nltk.download("words", quiet=True)
nltk.download("brown", quiet=True)

nltk_words = set(word.lower() for word in words.words())
brown_words = set(word.lower() for word in brown.words())
word_freq = FreqDist(word.lower() for word in brown.words())

bigram_freq = FreqDist(ngrams(brown.words(), 2))
frequency_order = "etaoinshrdlcumwfgypbvkjxzq"[::-1]


@lru_cache(maxsize=1000)
def create_pattern(substitution_pattern):
    return "".join("*" if char.isupper() else char for char in substitution_pattern)


@lru_cache(maxsize=1000)
def find_matching_words(substitution_pattern):
    pattern = create_pattern(substitution_pattern)
    regex_pattern = re.compile(f'^{pattern.replace("*", ".")}$')
    return sorted(
        (word for word in nltk_words if regex_pattern.fullmatch(word)),
        key=lambda x: word_freq[x],
        reverse=True,
    )


@lru_cache(maxsize=1000)
def validate_mapping(cipher, decipher):
    return len(set(cipher)) == len(set(decipher))


def evaluate_decryption(decrypted_message):
    words = decrypted_message.split()
    message_bigrams = list(ngrams(words, 2))
    bigram_score = sum(bigram_freq.get(bigram, 0) for bigram in message_bigrams)
    english_word_count = sum(
        1 for word in words if word.lower().replace(".", "") in brown_words
    )
    english_word_ratio = english_word_count / len(words) if words else 0
    char_score = sum(
        frequency_order.index(char.lower())
        for char in decrypted_message
        if char.isalpha()
    )
    return bigram_score, english_word_ratio, char_score


def solve_vigenere(text):
    chunks = sorted(set(text.replace(".", "").split(" ")), key=len, reverse=True)

    def iterate_subs(chunk, index, mapping):
        if all(word.islower() for word in chunk):
            if not validate_mapping("".join(chunks), "".join(chunk)):
                return []
            copy_text = text
            for i, word in enumerate(chunk):
                copy_text = copy_text.replace(chunks[i], word)
            return [copy_text]

        if index >= len(chunk):
            return []

        if chunk[index].islower():
            return iterate_subs(chunk, index + 1, mapping)

        matches = find_matching_words(chunk[index])
        if not matches:
            return []

        possible_answers = []
        for match in tqdm(matches, desc=f"Processing chunk: ", leave=False):
            new_mapping = mapping.copy()
            valid = True
            for c, m in zip(chunk[index], match):
                if c.isupper():
                    if c in new_mapping and new_mapping[c] != m:
                        valid = False
                        break
                    new_mapping[c] = m
            if not valid:
                continue

            subbed_chunk = [
                word.translate(str.maketrans(new_mapping)) for word in chunk
            ]
            possible_answers.extend(iterate_subs(subbed_chunk, index + 1, new_mapping))

        clear_output(wait=True)

        return possible_answers

    print("Solving cipher...")
    possible_texts = iterate_subs(chunks, 0, {})
    best_decryption = None
    best_score = float("-inf")

    for decrypted_message in tqdm(
        possible_texts, desc="Evaluating decryptions", unit="text", leave=False
    ):
        bigram_score, english_word_ratio, char_score = evaluate_decryption(
            decrypted_message
        )
        if english_word_ratio == 1:
            score = bigram_score + char_score
            if score > best_score:
                best_score = score
                best_decryption = decrypted_message

    return best_decryption.upper()


cipher = "PRCSOFQX FP QDR AFOPQ CZSPR LA JFPALOQSKR. QDFP FP ZK LIU BROJZK MOLTROE."
result = solve_vigenere(cipher)
print("Decrypted message:", result)
