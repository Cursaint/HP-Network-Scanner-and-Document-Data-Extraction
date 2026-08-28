import pdfplumber
import pandas as pd
import os
import sys
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()
#import default_dir from config.py
from config import ocr_default_dir

default_dir = ocr_default_dir

input_pdf = filedialog.askopenfilename(
    title="เลือกไฟล์ PDF", 
    filetypes=[("PDF files", "*.pdf")], 
    initialdir=default_dir
    )
output_excel = filedialog.asksaveasfilename(
    title="บันทึกไฟล์ Excel", 
    defaultextension=".xlsx", 
    filetypes=[("Excel files", "*.xlsx")], 
    initialdir=ocr_default_dir
    )

def export_pdf_coords_to_excel(input_pdf, output_excel="pdf_data.xlsx"):
    all_data = []
    
    print(f"กำลังอ่านไฟล์ {input_pdf}...")
    
    with pdfplumber.open(input_pdf) as pdf:
        for i in range(1):
            page = pdf.pages[i]
            words = page.extract_words()
            for word in words:
                all_data.append({
                    "Page": i + 1,
                    "Text": word['text'],
                    "x0": round(word['x0'], 2),
                    "top": round(word['top'], 2),
                    "x1": round(word['x1'], 2),
                    "bottom": round(word['bottom'], 2)
                })
    
    # แปลงเป็น DataFrame
    df = pd.DataFrame(all_data)
    
    # บันทึกลง Excel
    df.to_excel(output_excel, index=False)
    print(f"บันทึกข้อมูลเรียบร้อยแล้วที่ไฟล์: {output_excel}")
    print(f"จำนวนข้อมูลที่พบ: {len(df)} แถว")

# เรียกใช้งาน
export_pdf_coords_to_excel(input_pdf, output_excel)