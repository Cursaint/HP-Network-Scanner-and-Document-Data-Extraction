import pdfplumber
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import glob
import os

root = tk.Tk()
root.withdraw()

#import default_dir from config.py
from config import ocr_default_dir

default_dir = ocr_default_dir

# เลือกโฟลเดอร์
input_folder = filedialog.askdirectory(
    title="เลือกโฟลเดอร์ PDF",
    initialdir=default_dir
)

output_excel = filedialog.asksaveasfilename(
    title="บันทึกไฟล์ Excel",
    defaultextension=".xlsx",
    filetypes=[("Excel files", "*.xlsx")]
)

FIELDS_CONFIG = {
    "วันที่": (397.46,198.26,426.54,208.26),
    "เลขที่เอกสาร": (472.46,198.26,521.53,208.26),
    "เลขบัญชี": (418,265.82,463.1,277.82),
    "ยอดเงิน": (486.05,443.82,520.95,455.82),
    "ภาษี": (410.34,443.82,431.66,455.82),
    "ค่าธรรมเนียม": (313.99,443.82,345.01,455.82),
    "ยอดสุทธิ": (225.05,443.82,259.95,455.82)
}

all_data = []

pdf_files = glob.glob(os.path.join(input_folder, "*.pdf"))

for pdf_file in pdf_files:

    print(f"กำลังประมวลผล: {os.path.basename(pdf_file)}")

    with pdfplumber.open(pdf_file) as pdf:

        for page_no, page in enumerate(pdf.pages, start=1):

            row = {
                "ไฟล์": os.path.basename(pdf_file),
                "Page": page_no
            }

            for field_name, bbox in FIELDS_CONFIG.items():
                text = page.crop(bbox).extract_text()
                row[field_name] = text.strip() if text else ""

            all_data.append(row)

df = pd.DataFrame(all_data)

for col in ["ยอดเงิน", "ภาษี", "ค่าธรรมเนียม", "ยอดสุทธิ"]:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(",", "", regex=False)
    )

    df[col] = pd.to_numeric(df[col], errors="coerce")

df.to_excel(output_excel, index=False)

print(f"เสร็จสิ้น {len(pdf_files)} ไฟล์")
print(f"รวมทั้งหมด {len(df)} รายการ")