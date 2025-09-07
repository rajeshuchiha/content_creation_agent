import re
import os

def process_text(text):
    x = re.sub(r"\[\d+\]", "", text)
    x = re.sub(r"([^\w\s]*)", "", x, flags=re.ASCII)
    processed = re.sub(r"()", "", x)
    return processed

FILE_PATH = r"C:\Users\rvisw\OneDrive\Desktop\shashank_Project\content_creation_agent\data"
RAW_PATH = os.path.join(FILE_PATH, "raw")

files = os.listdir(RAW_PATH)


for i, file in enumerate(files, start=1):
    
    with open(os.path.join(RAW_PATH, file), "r", encoding="utf-8") as f:
        page_content = f.read()
    
    file_path_processed = os.path.join(
        FILE_PATH,
        "processed",
        f"wiki_page_{i}.txt"
    )
        
    with open(file_path_processed, "w", encoding="utf-8") as f:
        f.write(process_text(page_content))