import os
from html_chunking import get_html_chunks

if __name__ == '__main__':
    with open('cases/Andrej-Karpathy-YouTube.html', 'r', encoding='utf-8') as file:
        html = file.read()

    merged_chunks = get_html_chunks(html, max_tokens=1000, is_clean_html=True, attr_cutoff_len=0)
    
    if os.path.exists('chunks'):
        for file in os.listdir('chunks'):
            os.remove(os.path.join('chunks', file))

    for i, chunk in enumerate(merged_chunks):
        with open(f'chunks/chunk_{i}.html', 'w', encoding='utf-8') as output_file:
            output_file.write(chunk)
