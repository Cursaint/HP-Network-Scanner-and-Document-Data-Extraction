import pdfplumber
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import glob
import os

root = tk.Tk()
root.withdraw()
# กำหนดโฟลเดอร์เริ่มต้นสำหรับการเลือกไฟล์ PDF
# import default_dir from config.py
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
    "วันที่": (404.64,134.66,434.12,143.66),
    "เลขที่เอกสาร": (404.64,149.66,465.56,158.66),
}
def extract_three_totals_by_keyword(page):
    matches = page.search("(TOTAL)")
    
    if matches:
        found = matches[0] 
        x1 = found['x1']
        top = found['top']
        bottom = found['bottom']
        
        # กำหนดกรอบพิกัดสำหรับ 3 ค่า (เรียงต่อกันไปทางขวา)
        bbox1 = (x1+5, top - 2, x1 + 94.9, bottom + 2)       # ค่าแรก: ห่างขวา 100
        bbox2 = (x1 + 96, top - 2, x1 + 176.45, bottom + 2) # ค่าที่ 2: ขยับต่ออีก 50
        bbox3 = (x1 + 178, top - 2, x1 + 266.45, bottom + 2) # ค่าที่ 3: ขยับต่ออีก 50
        bbox4 = (x1 + 268, top - 2, x1 + 349.9, bottom + 2) # ค่าที่ 4: ขยับต่ออีก 50
        # ตัด (Crop) และดึงข้อความจากทั้ง 3 กรอบ
        val1 = page.crop(bbox1).extract_text()
        val2 = page.crop(bbox2).extract_text()
        val3 = page.crop(bbox3).extract_text()
        val4 = page.crop(bbox4).extract_text()
        
        # คืนค่ากลับเป็น Dictionary เพื่อความสะดวกในการเอาไปรวมกับข้อมูลอื่น
        return {
            "ยอดเงิน": val1.strip() if val1 else "",
            "ภาษี": val2.strip() if val2 else "",
            "ค่าธรรมเนียม": val3.strip() if val3 else "",
            "ยอดสุทธิ": val4.strip() if val4 else ""
        }
    
    # กรณีไม่พบคำว่า "Total Amount" ให้คืนค่าว่างทั้ง 3 ช่อง
    return {"ยอดเงิน": "", "ภาษี": "", "ค่าธรรมเนียม": "", "ยอดสุทธิ": ""}
def extract_data_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        for page_no, page in enumerate(pdf.pages, start=1):
            row = {
                "ไฟล์": os.path.basename(pdf_file),
                "Page": page_no
            }

            # ดึงข้อมูลจากพิกัดที่กำหนดใน FIELDS_CONFIG
            for field_name, bbox in FIELDS_CONFIG.items():
                text = page.crop(bbox).extract_text()
                row[field_name] = text.strip() if text else ""

            # ดึงข้อมูลยอดเงิน, ภาษี, ค่าธรรมเนียม, ยอดสุทธิ ด้วย Keyword
            totals = extract_three_totals_by_keyword(page)
            row.update(totals)

            all_data.append(row)
all_data = []

pdf_files = glob.glob(os.path.join(input_folder, "*.pdf"))

for pdf_file in pdf_files:

    print(f"กำลังประมวลผล: {os.path.basename(pdf_file)}")

    extract_data_from_pdf(pdf_file)

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