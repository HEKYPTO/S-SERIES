use std::collections::HashMap;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::time::Instant;
use sha1::{Sha1, Digest};

fn create_table(words: &[String]) -> HashMap<String, String> {
    let mut table = HashMap::new();

    for word in words {
        let permutations = case_permutations(word);
        for perm in permutations {
            let mut hasher = Sha1::new();
            hasher.update(perm.as_bytes());
            let hash = format!("{:x}", hasher.finalize());
            table.insert(perm, hash);
        }
    }

    table
}

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

fn run_trial(words: &[String]) -> (f64, usize) {
    let start = Instant::now();
    let rainbow_table = create_table(words);
    let creation_time = start.elapsed().as_secs_f64();
    let table_size = rainbow_table.len();
    (creation_time, table_size)
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let filename = "../10k-most-common.txt";
    let file = File::open(filename)?;
    let reader = BufReader::new(file);
    let words: Vec<String> = reader.lines().filter_map(Result::ok).collect();

    let num_trials = 10;

    let mut creation_times = Vec::new();
    let mut table_sizes = Vec::new();

    for i in 0..num_trials {
        println!("Running trial {}/{}", i + 1, num_trials);
        let (creation_time, table_size) = run_trial(&words);
        creation_times.push(creation_time);
        table_sizes.push(table_size);
    }

    let avg_creation_time: f64 = creation_times.iter().sum::<f64>() / num_trials as f64;
    let avg_table_size: f64 = table_sizes.iter().sum::<usize>() as f64 / num_trials as f64;

    println!("\nAverage Results over {} trials:", num_trials);
    println!("Average rainbow table creation time: {:.4} seconds", avg_creation_time);
    println!("Average table size: {:.0} entries", avg_table_size);
    println!("Average Performance: {} seconds per entry", avg_creation_time / avg_table_size);

    Ok(())
}
