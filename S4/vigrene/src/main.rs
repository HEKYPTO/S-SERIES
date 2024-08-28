use std::collections::{HashMap, HashSet};

const ENGLISH_FREQS: [f64; 26] = [
    0.08167, 0.01492, 0.02782, 0.04253, 0.12702, 0.02228, 0.02015,  // A-G
    0.06094, 0.06966, 0.00153, 0.00772, 0.04025, 0.02406, 0.06749,  // H-N
    0.07507, 0.01929, 0.00095, 0.05987, 0.06327, 0.09056, 0.02758,  // O-U
    0.00978, 0.02360, 0.00150, 0.01974, 0.00074                     // V-Z
];

const COMMON_WORDS: [&str; 20] = [
    "THE", "BE", "TO", "OF", "AND", "IN", "THAT", "HAVE", "IT", "FOR",
    "NOT", "ON", "WITH", "HE", "AS", "YOU", "DO", "AT", "THIS", "BUT"
];

fn main() {
    let ciphertext = "PRCSOFQX FP QDR AFOPQ CZSPR LA JFPALOQSKR. QDFP FP ZK LIU BROJZKMOLTROE.";
    let decrypted = decrypt_vigenere(ciphertext);
    println!("Initial decryption: {}", decrypted);
    let improved = improve_decryption(&decrypted);
    println!("Improved decryption: {}", improved);
}

fn decrypt_vigenere(ciphertext: &str) -> String {
    let cleaned_text: String = ciphertext.chars().filter(|c| c.is_ascii_alphabetic()).collect();
    let key_length = guess_key_length(&cleaned_text);
    let key = find_key(&cleaned_text, key_length);
    decrypt(ciphertext, &key)
}

fn guess_key_length(text: &str) -> usize {
    (1..=20).max_by(|&a, &b| {
        let ioc_a = index_of_coincidence(text, a);
        let ioc_b = index_of_coincidence(text, b);
        ioc_a.partial_cmp(&ioc_b).unwrap()
    }).unwrap()
}

fn index_of_coincidence(text: &str, step: usize) -> f64 {
    let subtext: String = text.chars().step_by(step).collect();
    let n = subtext.len() as f64;
    let freqs = count_frequencies(&subtext);
    let sum: f64 = freqs.values().map(|&count| (count as f64) * ((count - 1) as f64)).sum();
    sum / (n * (n - 1.0))
}

fn count_frequencies(text: &str) -> HashMap<char, usize> {
    let mut freqs = HashMap::new();
    for c in text.chars() {
        *freqs.entry(c).or_insert(0) += 1;
    }
    freqs
}

fn find_key(text: &str, key_length: usize) -> String {
    (0..key_length)
        .map(|i| {
            let column: String = text.chars().skip(i).step_by(key_length).collect();
            find_shift(&column)
        })
        .collect()
}

fn find_shift(text: &str) -> char {
    let freqs = count_frequencies(text);
    let text_len = text.len() as f64;
    
    (0..26)
        .map(|shift| {
            let chi_squared: f64 = (0..26).map(|i| {
                let expected = ENGLISH_FREQS[i] * text_len;
                let c = ((i as u8 + shift) % 26 + b'A') as char;
                let observed = *freqs.get(&c).unwrap_or(&0) as f64;
                (observed - expected).powi(2) / expected
            }).sum();
            (shift, chi_squared)
        })
        .min_by(|&(_, a), &(_, b)| a.partial_cmp(&b).unwrap())
        .map(|(shift, _)| (shift as u8 + b'A') as char)
        .unwrap()
}

fn decrypt(ciphertext: &str, key: &str) -> String {
    ciphertext
        .chars()
        .enumerate()
        .map(|(i, c)| {
            if c.is_ascii_alphabetic() {
                let key_char = key.chars().nth(i % key.len()).unwrap();
                let shift = key_char as u8 - b'A';
                ((c as u8 - b'A' + 26 - shift) % 26 + b'A') as char
            } else {
                c
            }
        })
        .collect()
}

fn improve_decryption(decrypted: &str) -> String {
    let mut best_score = f64::MAX;
    let mut best_text = decrypted.to_string();

    let word_set: HashSet<_> = COMMON_WORDS.iter().cloned().collect();

    for _ in 0..1000 {  // Limit iterations to prevent infinite loop
        let mut improved = best_text.clone();
        for word in &COMMON_WORDS {
            let pattern: String = (0..word.len()).map(|_| '.').collect();
            if let Some(pos) = improved.find(&pattern) {
                improved.replace_range(pos..pos+word.len(), word);
            }
        }

        let score = score_text(&improved, &word_set);
        if score < best_score {
            best_score = score;
            best_text = improved;
        }
    }

    best_text
}

fn score_text(text: &str, word_set: &HashSet<&str>) -> f64 {
    let words: Vec<&str> = text.split_whitespace().collect();
    let unknown_words = words.iter().filter(|w| !word_set.contains(*w)).count() as f64;
    unknown_words / words.len() as f64
}