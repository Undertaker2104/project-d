from transformers import pipeline

class Summarizer():
    def __init__(self):
        self.pipeline = pipeline('summarization', model="facebook/bart-large-cnn")

    def summarize(self, text):
        max_chunk_size = 1024
        chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
        
        summaries = []
        for chunk in chunks:
            summary = self.pipeline(chunk, max_length=100, min_length=25, do_sample=False)
            summaries.append(summary[0]['summary_text'])
        
        combined_summary = " ".join(summaries)
        return combined_summary
