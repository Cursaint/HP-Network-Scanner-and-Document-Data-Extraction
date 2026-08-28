# 📄 HP Network Scanner & Automated Data Extractor

## 📌 Overview
This project is an end-to-end automated document processing pipeline designed to eliminate manual data entry in an accounting environment. 

It consists of two main components:
1. **Network Scanner API Integration:** A script that bypasses standard manufacturer software to trigger scans programmatically over the local network using the HP eSCL API.
2. **Deterministic Data Extractor:** A rules-based OCR pipeline that batch-processes bank receipts (such as BAY, KBank, and KTC), extracting embedded text and structuring it into clean Excel reports.

By utilizing exact coordinate mapping and anchor-keyword searching rather than unpredictable AI, this tool ensures highly accurate extraction accuracy, making it highly reliable for strict financial data workflows.

## 🚀 Key Features
* **Automated Network Scanning:** Uses Python to send XML configuration payloads to an HP printer's IP, triggering hardware scans and downloading the files directly via HTTP requests.
* **Continuous Batch Scanning:** Built-in timers and keyboard interrupts allow users to seamlessly scan multiple physical pages without constantly returning to the PC.
* **Rules-Based Extraction:** Uses `pdfplumber` to extract data via absolute bounding box coordinates (for static layouts) and keyword-relative cropping (for dynamic layouts).
* **Data Cleaning & Transformation:** Utilizes Regular Expressions (`re`) and `pandas` to clean entity names, format dates, and convert string currencies into calculable numeric values.
* **Custom Layout Mapping Tool:** Includes a custom utility script to reverse-engineer PDF text coordinates, significantly reducing the time needed to add support for new document types.

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **Network/API:** `requests` (HTTP REST/XML interaction with HP eSCL protocol)
* **PDF Processing:** `pdfplumber` (Coordinate and keyword-based extraction)
* **Data Structuring:** `pandas`, `openpyxl` (DataFrames and Excel export)
* **UI:** `tkinter` (Native file dialogs)

## 🧠 How It Works

### Part 1: Network Scanning (`Scan\hp_scan.py`)
1. **Trigger Scan:** The script reads the printer IP from `config.py` and sends an XML payload via a POST request to the printer's `/eSCL/ScanJobs` endpoint.
2. **Retrieve Image:** It polls the printer's job URL, waits for the scan head to finish, and downloads the resulting document (PDF/JPG) to a designated local output folder.
3. **Continuous Batch Scanning:** For multiple pages, the script provides a 30-second countdown allowing the user to change the physical paper. It automatically triggers the next scan when the timer expires, or the user can press the `c` key to skip the timer and scan immediately.

### Part 2: Data Extraction (`data_extract/`)
1. **Input Selection:** The user is prompted via a native Windows GUI (`tkinter`) to select a target folder containing the scanned PDF receipts.
2. **Text Parsing:** The script iterates through the PDFs. Depending on the bank format:
   * **Static Layouts (e.g., KBank):** Crops specific `(x0, top, x1, bottom)` bounding boxes.
   * **Dynamic Layouts (e.g., BAY):** Searches for anchor keywords like `(Summary By Entity)` and calculates relative bounding boxes to capture the dynamic values.
3. **Structuring & Export:** Extracted strings are cleaned, cast to correct numeric/date data types, and compiled into a Pandas DataFrame before being exported to `.xlsx`.

## ⚙️ Setup & Installation
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Rename `config_template.py` to `config.py` and input your local HP scanner's IP address and preferred default folders.
4. Run `hp_scan.py` to scan documents, or run any script in the `Data Extract/` folder to process existing PDFs.

*Note: All code provided is sanitized. No actual financial records or sensitive company data are included in this repository.*
