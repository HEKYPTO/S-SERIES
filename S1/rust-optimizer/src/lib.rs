use pyo3::prelude::*;
use std::collections::HashMap;
use sha1::{Sha1, Digest};

#[pyfunction]
fn create_table(words: Vec<String>) -> PyResult<HashMap<String, String>> {
    let mut table = HashMap::new();

    for word in words {
        let permutations = case_permutations(&word);
        for perm in permutations {
            let mut hasher = Sha1::new();
            hasher.update(perm.as_bytes());
            let hash = format!("{:x}", hasher.finalize());
            table.insert(perm, hash);
        }
    }

    Ok(table)
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

#[pymodule]
fn rainbow_table(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(create_table, m)?)?;
    Ok(())
}