from sentence_transformers import SentenceTransformer, util
from pathlib import Path
import pdfplumber
import re
import polars as pl
from datetime import datetime

def chunk_text(text, tokenizer, max_tokens=384, overlap=64):
    # Tokenize text into IDs (no truncation here!)
    input_ids = tokenizer.encode(text, add_special_tokens=False)

    chunks = []
    start = 0
    while start < len(input_ids):
        end = start + max_tokens
        chunk_ids = input_ids[start:end]
        chunk_text = tokenizer.decode(chunk_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
        chunks.append(chunk_text)
        # Move forward with overlap
        start += max_tokens - overlap

    return chunks
  
def remove_links(text):
    url_pattern = r'https?://\S+|www\.\S+'
    return re.sub(url_pattern, '', text)
    
def clean_text(text):
    text = remove_links(text)
    text = re.sub(r'[^a-zA-Z0-9.,()!?+\s-]', '', text)
    return re.sub(r'\s+', ' ', text).strip()
    
def read_text_file(filename) -> str:
    file_path = Path(__file__).parent / filename
    return clean_text(file_path.read_text(encoding='utf-8').strip())
    
def extract_text_from_pdf(file_path):
    full_text = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)
    return clean_text("\n".join(full_text).strip())
    
def load_model(model_name):
    return SentenceTransformer(model_name)
    
def encode_texts(model, text):
    vec = model.encode(text, convert_to_tensor=True)
    return vec

def calculate_match_score(vec1, vec2):
    cosine_similarity = util.cos_sim(vec1, vec2).max().item()
    return cosine_similarity * 100
    
def extract_from_folder(folder_name):
    folder_path = Path(__file__).parent / folder_name
    pdf_files = {}

    for pdf_file_path in folder_path.glob("*.pdf"):
        pdf_files[pdf_file_path.name] = pdf_file_path

    return pdf_files

def write_to_excel(result_rows, timestamp):
    pl.DataFrame(result_rows).sort("match_score", descending=True).write_excel(f"result_{timestamp}.xlsx", autofit=True)

def check_if_exists(filepath):
    file_path = Path(__file__).parent / filepath
    if file_path.exists():
        return True
    else:
        return False

def main():
    print("Starting script...")
    
    # model_name = 'all-MiniLM-L6-v2'
    model_name = 'all-mpnet-base-v2'
    if check_if_exists(f"cached-{model_name}"):
        model = load_model(f"cached-{model_name}")
    else:
        model = load_model(model_name)
        model.save(f"cached-{model_name}")
    
    job_desc_text = read_text_file("job_desc.txt")
    job_desc_vec = encode_texts(model, job_desc_text)
    resumes_dict = extract_from_folder("resumes")
    number_of_resumes = len(resumes_dict) 
    iteration = 0
    result_rows = []
    for name, file_path in resumes_dict.items():
        resume_text = extract_text_from_pdf(file_path)
        resume_chunks = chunk_text(resume_text, model.tokenizer, model.tokenizer.model_max_length)
        resume_vec = encode_texts(model, resume_chunks)
        match_score = calculate_match_score(job_desc_vec, resume_vec)
        iteration += 1
        print(f"[{iteration}/{number_of_resumes}] - Match score {name}: {match_score:.2f}")

        result_rows.append({
            "resume_name": name,
            "match_score": match_score
        })
                    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    write_to_excel(result_rows, timestamp)
    print(f"\nScript finished successfully. Check results in result_{timestamp}.xlsx")
    
if __name__ == "__main__":
    main()
