import time
from statistics import mean
from rainbow_table import create_table

def read_words(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file]

def run_trial(words):
    start = time.time()
    rainbow_table = create_table(words)
    creation_time = time.time() - start
    table_size = len(rainbow_table)
    return creation_time, table_size

def main():
    filename = "../10k-most-common.txt"
    words = read_words(filename)

    num_trials = 10

    creation_times = []
    table_sizes = []

    for i in range(num_trials):
        print(f"Running trial {i + 1}/{num_trials}")
        creation_time, table_size = run_trial(words)
        creation_times.append(creation_time)
        table_sizes.append(table_size)

    avg_creation_time = mean(creation_times)
    avg_table_size = mean(table_sizes)

    print(f"\nAverage Results over {num_trials} trials:")
    print(f"Average rainbow table creation time: {avg_creation_time:.4f} seconds")
    print(f"Average table size: {avg_table_size:.0f} entries")
    print(f"Average Performance: {avg_creation_time / avg_table_size} seconds per entry")

if __name__ == "__main__":
    main()