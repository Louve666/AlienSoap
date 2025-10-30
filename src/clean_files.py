import os
import re
import configparser

# --- Configuration ---
config = configparser.ConfigParser()
config.read('config.ini')

SOURCE_DIR = config.get('Paths', 'source_dir', fallback='./source/')
DEST_DIR = config.get('Paths', 'dest_dir', fallback='./rewritten/')
CHUNK_SIZE = config.getint('Settings', 'chunk_size', fallback=100000)
# --- End Configuration ---

def load_blacklist(path="src/blacklisted.txt"):
    bl = set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    bl.add(line)
    except Exception as e:
        print(f"Could not load blacklist: {e}")
    return bl

def process_line(line, blacklist):
    # Returns (cleaned_line, skip_reason) where skip_reason is None if not skipped
    if line.startswith("android://"):
        return None, "starts with android://"
    if "[NOT_SAVED]" in line or ":UNKNOWN:" in line:
        return None, "contains [NOT_SAVED] or :UNKNOWN:"
    # Convert all spaces to colons before further processing
    line = line.replace(" ", ":")
    # Remove http(s):// for blacklist check
    line_for_bl = re.sub(r"^https?://", "", line)
    # Extract domain for blacklist check (up to first "/" or ":")
    domain_end = len(line_for_bl)
    for sep in ["/", ":"]:
        idx = line_for_bl.find(sep)
        if idx != -1 and idx < domain_end:
            domain_end = idx
    domain = line_for_bl[:domain_end]
    # Check blacklist (substring match only in domain, including subdomains and TLDs)
    domain_lower = domain.lower()
    for bl in blacklist:
        bl = bl.lower()
        # Check if the blacklist entry is anywhere in the domain (including subdomains, TLDs, or as a substring)
        if bl in domain_lower:
            return None, f"contains blacklisted domain: {bl}"
    if line.count(":") < 3:
        return None, "fewer than 3 colons"
    # Remove http(s)://
    line_ = re.sub(r"^https?://", "", line)
    slash_idx = line_.find("/")
    colon_idx = line_.find(":")
    if slash_idx != -1 and (colon_idx == -1 or slash_idx < colon_idx):
        after_slash = line_[slash_idx:]
        colon_after_slash = after_slash.find(":")
        if colon_after_slash != -1:
            domain = line_[:slash_idx]
            rest = after_slash[colon_after_slash:]
            return (domain + rest).replace(" ", ":"), None
        else:
            return None, "no colon after slash"
    else:
        return line_.replace(" ", ":"), None

def get_size_gb(path):
    try:
        size_bytes = os.path.getsize(path)
        return size_bytes / (1024 ** 3)
    except Exception:
        return 0.0

def process_file(src_path, dest_path, blacklist):
    orig_size = get_size_gb(src_path)
    skipped_count = 0
    with open(src_path, "r", encoding="utf-8", errors="ignore") as fin, \
         open(dest_path, "w", encoding="utf-8") as fout:
        for i, line in enumerate(fin, 1):
            line = line.rstrip("\n\r")
            cleaned, reason = process_line(line, blacklist)
            if cleaned is not None:
                fout.write(cleaned + "\n")
            else:
                ascii_line = line.encode("ascii", errors="ignore").decode("ascii")
                # print(f"SKIPPED: {ascii_line} > {reason}")
                skipped_count += 1
            if i % CHUNK_SIZE == 0:
                fout.flush()
        fout.flush()
    new_size = get_size_gb(dest_path)
    percent_saved = 0.0
    if orig_size > 0:
        percent_saved = 100.0 * (orig_size - new_size) / orig_size
    return {
        "filename": os.path.basename(src_path),
        "orig_size": orig_size,
        "new_size": new_size,
        "skipped": skipped_count,
        "percent_saved": percent_saved
    }

def main():
    import platform
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)

    blacklist = load_blacklist()

    if not os.path.exists(SOURCE_DIR):
        print(f"Source directory '{SOURCE_DIR}' not found.")
        print("Please create it and add your .txt files, or update config.ini.")
        os.makedirs(SOURCE_DIR)
        print(f"Created '{SOURCE_DIR}' for you as a placeholder.")
        return

    files = [fname for fname in os.listdir(SOURCE_DIR) if fname.endswith(".txt")]
    total_files = len(files)
    results = []
    for idx, fname in enumerate(files, 1):
        src_path = os.path.join(SOURCE_DIR, fname)
        dest_path = os.path.join(DEST_DIR, fname)
        result = process_file(src_path, dest_path, blacklist)
        results.append(result)
        files_left = total_files - idx
        print(f"FILES LEFT TO PROCESS: {files_left}")
        # Clear terminal after each file
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")
        # Print summary table
        print(f"{'FILENAME':40} {'ORIGINAL(GB)':>14} {'REWRITTEN(GB)':>14} {'SKIPPED':>10} {'%SAVED':>10}")
        for r in results:
            print(f"{r['filename']:40} {r['orig_size']:14.3f} {r['new_size']:14.3f} {r['skipped']:10} {r['percent_saved']:9.2f}%")

if __name__ == "__main__":
    main()
