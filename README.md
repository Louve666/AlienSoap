# ALIEN SOAP - Text File Cleaner

This project provides a set of Python scripts to clean and process large text files, removing unwanted lines based on a blacklist and specific formatting rules. It's designed to be configurable and efficient, handling large files by processing them in chunks.

## Features

- **Blacklist Filtering:** Removes lines containing blacklisted domains.
- **Line Formatting:** Enforces consistent formatting by replacing spaces with colons.
- **Configurable Paths:** All directory paths and settings can be configured in `config.ini`.
- **Efficient Processing:** Scripts are optimized to handle large files with minimal memory usage.
- **Size Comparison:** Includes a tool to compare the original and rewritten file sizes, showing the space saved.

## Project Structure

```
.
├── src/
│   ├── clean_files.py      # Main script for cleaning files
│   ├── report_sizes.py     # Script to compare file sizes
│   └── blacklisted.txt     # List of blacklisted domains
├── config.ini              # Configuration file for paths and settings
├── requirements.txt        # (Currently empty) For future dependencies
├── source/                 # Directory for original .txt files (create this)
└── rewritten/              # Directory for cleaned .txt files (created automatically)
```

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Louve666/AlienSoap.git
    cd AlienSoap
    ```

2.  **Create the source directory:**
    Create a `source` directory in the project root and place your `.txt` files inside it.

3.  **Update the blacklist:**
    Edit `src/blacklisted.txt` to add or remove domains you want to filter out.

4.  **Customize the configuration (optional):**
    Open `config.ini` to change the default directory paths or processing settings if needed.

## Usage

### Cleaning Files

To start the cleaning process, run the `clean_files.py` script from the project root:

```bash
python3 src/clean_files.py
```

Alternatively, you can run the script as a background process, which is useful for very large jobs. This will prevent the process from being terminated if you close your terminal:

```bash
nohup python3 src/clean_files.py &
```

You can monitor its progress by tailing the `nohup.out` file:

```bash
tail -f nohup.out
```

The script will read files from the `source` directory, process them, and write the cleaned versions to the `rewritten` directory.

### Comparing File Sizes

After processing the files, you can compare the original and rewritten sizes to see how much space was saved. Run the `report_sizes.py` script from the project root:

```bash
python3 src/report_sizes.py
```

This will display a table with the original size, rewritten size, and the percentage of space saved for each file, as well as the total savings.