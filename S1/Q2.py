import hashlib
import time
import itertools
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

def create_table(words):
    table = {}
    def process_word(item):
        stripped_item = item.strip()
        local_permutations = case_permutations(stripped_item)
        local_table = {}
        for perm in local_permutations:
            hashed_item = hashlib.sha1(perm.encode()).hexdigest()
            local_table[perm] = hashed_item
        return local_table

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_word, item) for item in words]
        for future in as_completed(futures):
            local_table = future.result()
            table.update(local_table)
    return table

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

def run_trial(words):
    start_time = time.time()
    rainbow_table = create_table(words)
    end_time = time.time()
    creation_time = end_time - start_time
    table_size = len(rainbow_table)
    table_memory_size = sum(
        len(key.encode()) + len(value.encode()) for key, value in rainbow_table.items()
    )
    return creation_time, table_size, table_memory_size

def main():
    filename = "10k-most-common.txt"
    words = []
    try:
        with open(filename, "r") as file:
            words = file.readlines()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        exit(1)

    num_trials = 10
    creation_times = []
    table_sizes = []
    table_memory_sizes = []

    for i in range(num_trials):
        print(f"Running trial {i+1}/{num_trials}")
        creation_time, table_size, table_memory_size = run_trial(words)
        creation_times.append(creation_time)
        table_sizes.append(table_size)
        table_memory_sizes.append(table_memory_size)

    avg_creation_time = statistics.mean(creation_times)
    avg_table_size = statistics.mean(table_sizes)
    avg_table_memory_size = statistics.mean(table_memory_sizes)

    print(f"\nAverage Results over {num_trials} trials:")
    print(f"Average rainbow table creation time: {avg_creation_time:.4f} seconds")
    print(f"Average table size: {avg_table_size:.0f} entries")
    print(f"Average table memory size: {avg_table_memory_size / (1024 * 1024):.2f} MB")

if __name__ == "__main__":
    main()