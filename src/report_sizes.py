import os
import concurrent.futures
import configparser

# --- Configuration ---
config = configparser.ConfigParser()
config.read('config.ini')

ORIGINAL_DIR = config.get('Paths', 'source_dir', fallback='./source/')
REWRITTEN_DIR = config.get('Paths', 'dest_dir', fallback='./rewritten/')
MAX_WORKERS = 32  # Use more workers for SSD, tune as needed
# --- End Configuration ---

def get_size_gb(path):
    try:
        return os.path.getsize(path) / (1024 ** 3)
    except Exception as e:
        print(f"Error getting size for {path}: {e}")
        return -1

def get_file_stats(filename):
    orig_path = os.path.join(ORIGINAL_DIR, filename)
    rew_path = os.path.join(REWRITTEN_DIR, filename)
    if not os.path.exists(rew_path):
        return None
    orig_size = get_size_gb(orig_path)
    rew_size = get_size_gb(rew_path)
    if orig_size == -1 or rew_size == -1:
        return None
    saved_pct = ((orig_size - rew_size) / orig_size * 100) if orig_size > 0 else 0
    return (filename, orig_size, rew_size, saved_pct)

def main():
    if not os.path.exists(ORIGINAL_DIR):
        print(f"Source directory '{ORIGINAL_DIR}' not found.")
        print("Please create it and add your .txt files, or update config.ini.")
        return
    if not os.path.exists(REWRITTEN_DIR):
        print(f"Rewritten directory '{REWRITTEN_DIR}' not found.")
        return

    original_files = [f for f in os.listdir(ORIGINAL_DIR) if f.endswith(".txt")]
    total_original = 0.0
    total_rewritten = 0.0

    print(f"Checking {len(original_files)} files...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        stats = list(executor.map(get_file_stats, original_files))

    print(f"{'FILENAME':40} {'ORIGINAL (GB)':>15} {'REWRITTEN (GB)':>15} {'SAVED (%)':>12}")
    print("-" * 90)
    for stat in stats:
        if stat is None:
            continue
        filename, orig_size, rew_size, saved_pct = stat
        total_original += orig_size
        total_rewritten += rew_size
        print(f"{filename:40} {orig_size:15.6f} {rew_size:15.6f} {saved_pct:12.2f}")

    total_saved_pct = ((total_original - total_rewritten) / total_original * 100) if total_original > 0 else 0
    print("-" * 90)
    print(f"{'TOTAL':40} {total_original:15.6f} {total_rewritten:15.6f} {total_saved_pct:12.2f}")

if __name__ == "__main__":
    main()