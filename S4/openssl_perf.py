import os
import time
import subprocess
import tempfile
import csv

OPENSSL = "/home/linuxbrew/.linuxbrew/opt/openssl@1.1/bin/openssl"
BLOCK_SIZES = [16, 64, 256, 1024, 4096, 16384]  
TRIALS = 10

def generate_random_file(block_size, file_size_gb=1):
    file_size = file_size_gb * 1024 * 1024 * 1024  
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file_name = temp_file.name
        print(f"Generating {file_size_gb} GB file: {file_name}")
        
        while file_size > 0:
            temp_file.write(os.urandom(min(block_size, file_size)))
            file_size -= block_size
    return file_name

def measure_openssl(command):
    start = time.time()
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    elapsed = time.time() - start
    if result.returncode == 0:
        return elapsed
    else:
        raise RuntimeError("Command failed")

def measure_sha1(file_name):
    elapsed = measure_openssl(f"{OPENSSL} sha1 {file_name}")
    return elapsed

def measure_rc4(file_name):
    key = os.urandom(16).hex()
    elapsed = measure_openssl(f"{OPENSSL} enc -rc4 -in {file_name} -out /dev/null -k {key} -pbkdf2")
    return elapsed

def measure_blowfish(file_name):
    key = os.urandom(16).hex()
    elapsed = measure_openssl(f"{OPENSSL} enc -bf -in {file_name} -out /dev/null -k {key} -pbkdf2")
    return elapsed

def measure_dsa(file_name):
    subprocess.run(f"{OPENSSL} dsaparam -out /tmp/dsa_params.pem 1024", shell=True, check=True, stderr=subprocess.DEVNULL)
    subprocess.run(f"{OPENSSL} gendsa -out /tmp/dsa_key.pem /tmp/dsa_params.pem", shell=True, check=True, stderr=subprocess.DEVNULL)
    
    sign_command = f"{OPENSSL} dgst -sha1 -sign /tmp/dsa_key.pem -out /dev/null {file_name}"    
    sign_elapsed = measure_openssl(sign_command)

    os.remove("/tmp/dsa_params.pem")
    os.remove("/tmp/dsa_key.pem")

    return sign_elapsed

def perform_trial(block_size):
    print(f"Performing trial with block size {block_size} bytes...")

    sha1_times = []
    rc4_times = []
    blowfish_times = []
    dsa_sign_times = []

    for _ in range(TRIALS):
        file_name = generate_random_file(block_size=block_size)
        
        sha1_times.append(measure_sha1(file_name))
        rc4_times.append(measure_rc4(file_name))
        blowfish_times.append(measure_blowfish(file_name))
        dsa_sign_times.append(measure_dsa(file_name))

        os.remove(file_name)

    return {
        'sha1_avg': sum(sha1_times) / TRIALS,
        'rc4_avg': sum(rc4_times) / TRIALS,
        'blowfish_avg': sum(blowfish_times) / TRIALS,
        'dsa_sign_avg': sum(dsa_sign_times) / TRIALS,
    }

def write_results_to_csv(results, filename='algorithm_performance.csv'):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Block Size', 'SHA1 Avg Time', 'RC4 Avg Time', 'Blowfish Avg Time', 'DSA Sign Avg Time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for block_size, times in results.items():
            writer.writerow({
                'Block Size': block_size,
                'SHA1 Avg Time': times['sha1_avg'],
                'RC4 Avg Time': times['rc4_avg'],
                'Blowfish Avg Time': times['blowfish_avg'],
                'DSA Sign Avg Time': times['dsa_sign_avg']
            })

def main():
    results = {}
    for block_size in BLOCK_SIZES:
        avg_times = perform_trial(block_size)
        results[block_size] = avg_times

    write_results_to_csv(results)

if __name__ == "__main__":
    main()
