#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <ctype.h> 
#include <openssl/sha.h>

#define MAX_WORD_LENGTH 100
#define MAX_PERMUTATIONS 100000000
#define MAX_WORDS 100000000

typedef struct {
    char *key;
    char *value;
} KeyValuePair;

typedef struct {
    KeyValuePair *data;
    size_t size;
    size_t capacity;
} HashMap;

void init_hash_map(HashMap *map, size_t initial_capacity) {
    map->data = malloc(initial_capacity * sizeof(KeyValuePair));
    map->size = 0;
    map->capacity = initial_capacity;
}

void insert_hash_map(HashMap *map, const char *key, const char *value) {
    if (map->size >= map->capacity) {
        map->capacity *= 2;
        map->data = realloc(map->data, map->capacity * sizeof(KeyValuePair));
    }
    map->data[map->size].key = strdup(key);
    map->data[map->size].value = strdup(value);
    map->size++;
}

void free_hash_map(HashMap *map) {
    for (size_t i = 0; i < map->size; i++) {
        free(map->data[i].key);
        free(map->data[i].value);
    }
    free(map->data);
}

void case_permutations(const char *word, char **permutations, size_t *perm_count) {
    static const char *substitutions[] = {"@", "1!", "1Ii", "0", "$5"};
    static const char substitution_chars[] = {'a', 'i', 'l', 'o', 's'};
    
    size_t word_len = strlen(word);
    char variations[MAX_WORD_LENGTH][5];
    size_t variation_counts[MAX_WORD_LENGTH];

    for (size_t i = 0; i < word_len; i++) {
        char c = word[i];
        char lower = tolower(c);
        int found = 0;
        for (int j = 0; j < 5; j++) {
            if (lower == substitution_chars[j]) {
                snprintf(variations[i], 5, "%c%c%s", tolower(c), toupper(c), substitutions[j]);
                variation_counts[i] = strlen(variations[i]);
                found = 1;
                break;
            }
        }
        if (!found) {
            snprintf(variations[i], 3, "%c%c", tolower(c), toupper(c));
            variation_counts[i] = 2;
        }
    }

    *perm_count = 1;
    for (size_t i = 0; i < word_len; i++) {
        *perm_count *= variation_counts[i];
    }

    for (size_t i = 0; i < *perm_count; i++) {
        size_t temp = i;
        for (size_t j = 0; j < word_len; j++) {
            permutations[i][j] = variations[j][temp % variation_counts[j]];
            temp /= variation_counts[j];
        }
        permutations[i][word_len] = '\0';
    }
}

void create_table(char **words, size_t word_count, HashMap *table) {
    char **permutations = malloc(MAX_PERMUTATIONS * sizeof(char *));
    for (size_t i = 0; i < MAX_PERMUTATIONS; i++) {
        permutations[i] = malloc(MAX_WORD_LENGTH * sizeof(char));
    }

    for (size_t i = 0; i < word_count; i++) {
        size_t perm_count;
        case_permutations(words[i], permutations, &perm_count);

        for (size_t j = 0; j < perm_count; j++) {
            unsigned char hash[SHA_DIGEST_LENGTH];
            char hash_hex[SHA_DIGEST_LENGTH * 2 + 1];
            SHA1((unsigned char *)permutations[j], strlen(permutations[j]), hash);
            
            for (int k = 0; k < SHA_DIGEST_LENGTH; k++) {
                sprintf(&hash_hex[k * 2], "%02x", hash[k]);
            }
            
            insert_hash_map(table, permutations[j], hash_hex);
        }
    }

    for (size_t i = 0; i < MAX_PERMUTATIONS; i++) {
        free(permutations[i]);
    }
    free(permutations);
}

int main() {
    FILE *file = fopen("10k-most-common.txt", "r");
    if (!file) {
        perror("Error opening file");
        return 1;
    }

    char **words = malloc(MAX_WORDS * sizeof(char *));
    for (int i = 0; i < MAX_WORDS; i++) {
        words[i] = malloc(MAX_WORD_LENGTH * sizeof(char));
    }

    size_t word_count = 0;
    while (fgets(words[word_count], MAX_WORD_LENGTH, file) && word_count < MAX_WORDS) {
        words[word_count][strcspn(words[word_count], "\n")] = 0;
        word_count++;
    }
    fclose(file);

    int num_trials = 10;
    double total_time = 0;
    size_t total_size = 0;
    size_t total_memory = 0;

    for (int i = 0; i < num_trials; i++) {
        printf("Running trial %d/%d\n", i + 1, num_trials);

        HashMap table;
        init_hash_map(&table, 100000000);

        clock_t start = clock();
        create_table(words, word_count, &table);
        clock_t end = clock();

        double creation_time = ((double) (end - start)) / CLOCKS_PER_SEC;
        size_t table_size = table.size;
        size_t table_memory = 0;
        for (size_t j = 0; j < table.size; j++) {
            table_memory += strlen(table.data[j].key) + strlen(table.data[j].value) + 2;
        }

        total_time += creation_time;
        total_size += table_size;
        total_memory += table_memory;

        free_hash_map(&table);
    }

    double avg_creation_time = total_time / num_trials;
    double avg_table_size = (double)total_size / num_trials;
    double avg_table_memory = (double)total_memory / num_trials;

    printf("\nAverage Results over %d trials:\n", num_trials);
    printf("Average rainbow table creation time: %.4f seconds\n", avg_creation_time);
    printf("Average table size: %.0f entries\n", avg_table_size);
    printf("Average table memory size: %.2f MB\n", avg_table_memory / (1024.0 * 1024.0));
    printf("Average Performance: %f seconds per entry\n", avg_creation_time / avg_table_size);

    for (int i = 0; i < MAX_WORDS; i++) {
        free(words[i]);
    }
    free(words);

    return 0;
}