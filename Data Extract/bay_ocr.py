from datetime import datetime

from numpy import datetime64
import pdfplumber
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import glob
import os
import re

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
def clean_date_string(raw_text):
    """
    ดึงเฉพาะข้อความที่ตรงกับรูปแบบ วัน/เดือน/ปี (เช่น 01/07/2026)
    """
    # ค้นหาตัวเลข 2 หลัก / ตัวเลข 2 หลัก / ตัวเลข 4 หลัก
    match = re.search(r'\d{2}/\d{2}/\d{4}', str(raw_text))
    if match:
        return match.group(0)
    return raw_text # คืนค่าเดิมกลับไปถ้าไม่พบ

def clean_company_name(raw_text):
    """
    ลบตัวเลขและเครื่องหมาย / ที่แทรกตัวอยู่ออก เพื่อให้เหลือแค่ตัวอักษรชื่อบริษัท
    """
    # ลบตัวเลข 0-9 และเครื่องหมาย / ออกจากข้อความ
    cleaned = re.sub(r'[0-9/]', '', str(raw_text))
    return cleaned.strip()
def extract_date_by_keyword(page):
    matches_1 = page.search("(Print Date)")


    if matches_1:
        found_1 = matches_1[0] 
        x1_1 = found_1['x1']
        top_1 = found_1['top']
        bottom_1 = found_1['bottom']
        
        bbox_1 = (x1_1 + 6.55, top_1 - 2, x1_1 + 50, bottom_1 + 2)
              
        val_1 = page.crop(bbox_1).extract_text()

        return {"วันที่": clean_date_string(val_1)}
    
    return {"วันที่": ""}

def extract_entity_by_keyword(page):
    matches_2 = page.search("(Entity Name)")


    if matches_2:
        found_2 = matches_2[0] 
        x1_2 = found_2['x1']
        top_2 = found_2['top']
        bottom_2 = found_2['bottom']
        
        bbox_2 = (x1_2 + 6.55, top_2 - 2, x1_2 + 300, bottom_2 + 2)       
        val_2 = page.crop(bbox_2).extract_text()
        return {"ชื่อบริษัท": clean_company_name(val_2)}
    return {"ชื่อบริษัท": ""}

def extract_three_totals_by_keyword(page):
    matches = page.search("(Summary By Entity)")
    
    if matches:
        found = matches[0] 
        x1 = found['x1']
        top = found['top']
        bottom = found['bottom']
        
        # กำหนดกรอบพิกัดสำหรับ 3 ค่า (เรียงต่อกันไปทางขวา)
        bbox1 = (x1 + 207.57, top - 2, x1 + 237.13, bottom + 2) 
        bbox2 = (x1 + 248.27, top - 2, x1 + 271.26, bottom + 2) 
        bbox3 = (x1 + 283.13, top - 2, x1 + 301.19, bottom + 2) 
        bbox4 = (x1 + 516.19, top - 2, x1 + 542.46, bottom + 2) 
        bbox5 = (x1 + 628.63, top - 2, x1 + 658.19, bottom + 2) 
        # ตัด (Crop) และดึงข้อความจากทั้ง 3 กรอบ
        val1 = page.crop(bbox1).extract_text()
        val2 = page.crop(bbox2).extract_text()
        val3 = page.crop(bbox3).extract_text()
        val4 = page.crop(bbox4).extract_text()
        val5 = page.crop(bbox5).extract_text()
        # คืนค่ากลับเป็น Dictionary เพื่อความสะดวกในการเอาไปรวมกับข้อมูลอื่น
        return {
            "ยอดเงิน": val1.strip() if val1 else "",
            "ค่าธรรมเนียม": val2.strip() if val2 else "",
            "ภาษี": val3.strip() if val3 else "",
            "ค่าบริการ": val4.strip() if val4 else "",
            "ยอดสุทธิ": val5.strip() if val5 else ""
        }
    
    # กรณีไม่พบคำว่า "Total Amount" ให้คืนค่าว่างทั้ง 3 ช่อง
    return {"ยอดเงิน": "", "ค่าธรรมเนียม": "", "ภาษี": "", "ค่าบริการ": "", "ยอดสุทธิ": ""}
def extract_data_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        for page_no, page in enumerate(pdf.pages, start=1):
            row = {
                "ไฟล์": os.path.basename(pdf_file),
                "Page": page_no
            }
            # ดึงข้อมูลยอดเงิน, ภาษี, ค่าธรรมเนียม, ยอดสุทธิ ด้วย Keyword
            date = extract_date_by_keyword(page)
            row.update(date)
            entity = extract_entity_by_keyword(page)
            row.update(entity)
            totals = extract_three_totals_by_keyword(page)
            row.update(totals)

            all_data.append(row)
all_data = []

pdf_files = glob.glob(os.path.join(input_folder, "*.pdf"))

for pdf_file in pdf_files:

    print(f"กำลังประมวลผล: {os.path.basename(pdf_file)}")

    extract_data_from_pdf(pdf_file)

df = pd.DataFrame(all_data)

df["วันที่"] = pd.to_datetime(df["วันที่"], format="%d/%m/%Y", errors="coerce").dt.date

for col in ["ยอดเงิน", "ค่าธรรมเนียม", "ภาษี", "ค่าบริการ", "ยอดสุทธิ"]:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(",", "", regex=False)
    )

    df[col] = pd.to_numeric(df[col], errors="coerce")

df.to_excel(output_excel, index=False)

print(f"เสร็จสิ้น {len(pdf_files)} ไฟล์")
print(f"รวมทั้งหมด {len(df)} รายการ")