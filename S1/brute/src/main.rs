use std::collections::HashMap;
use std::fs::File;
use std::io::{BufRead, BufReader};
use sha1::{Sha1, Digest};

fn case_permutations(word: &str) -> Vec<String> {
    let substitutions: HashMap<char, &str> = [
        ('a', "@"), ('i', "1!"), ('l', "1Ii"), ('o', "0"), ('s', "$5")
    ].iter().cloned().collect();

    let mut variations = vec![String::new()];

    for c in word.chars() {
        let lower = c.to_lowercase().next().unwrap();
        let chars = if let Some(sub) = substitutions.get(&lower) {
            format!("{}{}{}", c.to_lowercase(), c.to_uppercase(), sub)
        } else {
            format!("{}{}", c.to_lowercase(), c.to_uppercase())
        };

        let mut new_variations = Vec::new();
        for var in &variations {
            for ch in chars.chars() {
                let mut new_var = var.clone();
                new_var.push(ch);
                new_variations.push(new_var);
            }
        }
        variations = new_variations;
    }

    variations
}

fn check_word(word: &str, target_hash: &str) -> Option<String> {
    for variation in case_permutations(word) {
        let mut hasher = Sha1::new();
        hasher.update(variation.as_bytes());
        let word_hash = format!("{:x}", hasher.finalize());
        if word_hash == target_hash {
            return Some(variation);
        }
    }
    None
}

fn main() {
    let target_hash = "d54cc1fe76f5186380a0939d2fc1723c44e8a5f7";
    let filename = "../10k-most-common.txt";

    let file = File::open(filename).expect("Could not open file");
    let reader = BufReader::new(file);
    let words: Vec<String> = reader.lines().filter_map(Result::ok).collect();

    for word in words.iter() {
        if let Some(password) = check_word(word, target_hash) {
            println!("Password found: {}", password);
            return;
        }
    }

    println!("Password not found in the dictionary.");
}
