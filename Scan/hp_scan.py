import requests
import time
import sys
import os
import msvcrt
import shutil
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()  # ซ่อนหน้าต่างหลัก

output_folder = filedialog.askdirectory(title="เลือกโฟลเดอร์สำหรับเก็บไฟล์สแกน")
if not output_folder:
    print("❌ ไม่ได้เลือกโฟลเดอร์ ออกจากโปรแกรม")
    sys.exit()
#----import config.py เพื่อดึงค่า printer_ip จากไฟล์ config.py
try:
    from config import printer_ip
except ImportError:
    print("❌ ไม่พบไฟล์ config.py หรือไม่สามารถนำเข้า printer_ip ได้")
    sys.exit()

    
base_url = f"http://{printer_ip}/eSCL"

xml_payload = """<?xml version="1.0" encoding="UTF-8"?>
<scan:ScanSettings xmlns:pwg="http://www.pwg.org/schemas/2010/12/sm" xmlns:scan="http://schemas.hp.com/imaging/escl/2011/05/03">
    <pwg:Version>2.63</pwg:Version>
    <scan:Intent>Document</scan:Intent>
    <pwg:InputSource>Platen</pwg:InputSource> 
    <scan:DocumentFormat>image/jpeg</scan:DocumentFormat>
    <scan:ColorMode>Grayscale8</scan:ColorMode>
    <scan:XResolution>300</scan:XResolution>
    <scan:YResolution>300</scan:YResolution>
</scan:ScanSettings>"""

try:
    total_pages = int(input("ระบุจำนวนแผ่นที่ต้องการสแกนทั้งหมด: "))  #ใส่จำนวนสูงสุดที่ต้องการสแกน
    start_page = int(input("เริ่มสแกนจากหน้าที่เท่าไหร่? (พิมพ์ 1 ถ้าเริ่มใหม่): ")) # จำนวนหน้าที่ต้องการเริ่มสแกน(จะเริ่มจากหน้าที่ใส่ถึงจำนวนสูงสุดที่ใส่ไว้ เช่น สูงสุด 10 เริ่ม 5 จะได้ 5 แผ่น 5-6-7-8-9-10)
except ValueError:
    print("❌ กรุณาพิมพ์เป็นตัวเลขเท่านั้นครับ")
    sys.exit()

for page in range(start_page, total_pages + 1):
    print(f"\n▶️ [แผ่นที่ {page}/{total_pages}] กำลังส่งคำสั่งสแกน...")
    try:
        response = requests.post(f"{base_url}/ScanJobs", data=xml_payload, headers={"Content-Type": "text/xml"}, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"❌ ติดต่อเครื่องปริ้นไม่ได้: {e}")
        break

    if response.status_code == 201:  #คอยเช็คว่าเครื่องปริ้นแสกนเสร็จรึยัง
        job_url = response.headers.get('Location')
        if not job_url.startswith("http"):
            job_url = f"http://{printer_ip}{job_url}"
            
        print("⏳ เครื่องกำลังสแกน... (รอให้หัวสแกนกวาดแสงเสร็จ)")
        time.sleep(5) 
        
        download_success = False
        max_attempts = 20 
        
        for attempt in range(1, max_attempts + 1):
            sys.stdout.write(f"\rกำลังพยายามดึงไฟล์ (ครั้งที่ {attempt}/{max_attempts})... ")
            sys.stdout.flush()
            
            try:
                doc_response = requests.get(f"{job_url}/NextDocument", stream=True, timeout=10)
                
                if doc_response.status_code == 200: 
                    content_type = doc_response.headers.get('Content-Type', '').lower()
                    
                    # ตรวจสอบว่าเป็นไฟล์ประเภทไหน เพื่อตั้งนามสกุลให้ถูกต้อง
                    if 'pdf' in content_type:
                        ext = ".pdf"
                    elif 'jpeg' in content_type or 'jpg' in content_type:
                        ext = ".jpg"
                    else:
                        ext = ".jpg" # เผื่อฉุกเฉิน (fallback)
                        
                    filename = os.path.join(output_folder, f"receipt_{page:03d}{ext}")
                    
                    # เซฟไฟล์
                    with open(filename, "wb") as f:
                        doc_response.raw.decode_content = True
                        shutil.copyfileobj(doc_response.raw, f)
                        
                    file_size = os.path.getsize(filename)
                    print(f"\n🎉 บันทึกไฟล์สมบูรณ์ ({file_size // 1024} KB) -> {filename}")
                    download_success = True
                    break 
                    
                elif doc_response.status_code in [503, 404, 409]:
                    time.sleep(2)
                else:
                    print(f"\n❌ ไม่สามารถดึงไฟล์ได้ (Error Code: {doc_response.status_code})")
                    break
                    
            except requests.exceptions.RequestException:
                time.sleep(2)

        if not download_success:
            print("\n⚠️ ดึงไฟล์ไม่สำเร็จ ข้ามไปแผ่นถัดไป")
            
    else:
        print(f"❌ เกิดข้อผิดพลาดตอนสั่งเครื่องปริ้น: {response.status_code}\n{response.text}")
        break 

    # --- ส่วนนับถอยหลังและการกด 'c' ---
    if page < total_pages:
        print("\n⏳ เปลี่ยนกระดาษได้เลยครับ... (กด 'c' เพื่อสแกนทันที หรือรอ 30 วินาที)")
        
        while msvcrt.kbhit():
            msvcrt.getch()
            
        skip_timer = False
        for remaining in range(30, 0, -1):
            sys.stdout.write(f"\rระบบจะสแกนแผ่นที่ {page+1} อัตโนมัติในอีก {remaining:02d} วินาที... ")
            sys.stdout.flush()
            
            for _ in range(10):
                if msvcrt.kbhit(): 
                    key = msvcrt.getch() 
                    if key.lower() == b'c': 
                        skip_timer = True
                        break 
                time.sleep(0.1)
                
            if skip_timer:
                print("\n⏭️ เริ่มสแกนแผ่นต่อไปทันที...")
                break 
                
        if not skip_timer:
            print("\n") 

print("\n✅ เสร็จสิ้นภารกิจการสแกนทั้งหมดแล้วครับ")