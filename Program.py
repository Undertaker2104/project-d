import spacy
import pandas as pd


class Program:
    def __init__(self):
        self.nlp = spacy.load("nl_core_news_sm")

    def process_text(self, text):
        doc = self.nlp(text)
        return [(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
    
if __name__ == "__main__":
    program = Program()
    name = "./translated_actionscopes_excel.xlsx"
    data = pd.read_excel(name, nrows=20)
    counter = 0
    for x in range(0, len(data)):
        counter +=1 
        val = f"{data.values[x][5]}"
        print(program.process_text(val))
        val = f"{data.values[x][8]}"
        print(program.process_text(val))
        val = f"{data.values[x][9]}"
        print(program.process_text(val))

