from transformers import pipeline
import pandas as pd

def loop(filename):
    data = pd.read_excel(filename)

    summarizer = pipeline('summarization', model="facebook/bart-large-cnn")

    for x in range(len(data)):
        print(f"{x}/{len(data)}")

        if x < 1000:
            continue

        # Memo_x
        val = f"{data.values[x][9]}"
        if val != "nan" and len(val) > 150:
            data.iat[x, 9] = summarize(val, summarizer)

        # Memo_y
        val = f"{data.values[x][25]}"
        if val != "nan" and len(val) > 150:
            data.iat[x, 25] = summarize(val, summarizer)

        # Internal memo
        val = f"{data.values[x][26]}"
        if val != "nan" and len(val) > 150:
            data.iat[x, 25] = summarize(val, summarizer)

        # Realized solution
        val = f"{data.values[x][28]}"
        if val != "nan" and len(val) > 150:
            data.iat[x, 28] = summarize(val, summarizer)

    data.to_excel("merged_data_with_sums.xlsx", index=False)

def summarize(text, summarizer):
    max_chunk_size = 1024
    chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
    
    summaries = []
    for chunk in chunks:
        summary = summarizer(chunk, max_length=100, min_length=25, do_sample=False)
        summaries.append(summary[0]['summary_text'])
    
    combined_summary = " ".join(summaries)
    return combined_summary

if __name__ == '__main__':
    loop('./Data/merged_data.xlsx')
