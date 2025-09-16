
def process_text(text):
    
    lines = text.split('\n')
    cleaned_lines = [line for line in lines if not line.strip().lower() in ['share', 'save']]
    clean_text = "\n".join(cleaned_lines)

    return clean_text
