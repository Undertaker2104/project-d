from transformers import pipeline

qa_pipeline = pipeline(
    "question-answering",
    model="henryk/bert-base-multilingual-cased-finetuned-dutch-squad2",
    tokenizer="henryk/bert-base-multilingual-cased-finetuned-dutch-squad2"
)
input = input("Geef een vraag op: ")
context = """Hallo,
Rashid van Friesland Campina belde dat shuttle 4 niet meer verder ging. 
Ze hadden bij de vorige opdracht de actie handmatig afgerond, echter ging de shuttle niet meer verder. 
Ik heb deze waarden in de database aangepast en daarna ging shuttle 4 weer verder. 
Hierna hadden ze nog een probleem met een pallet dat uit VT2 kwam, 
ik heb ze gevraagd om die pallet even handmatig uit te voeren, hierna was alles opgelost.
Graag 1 servicebon, PO nummer: 100059204

Met vriendelijke groet,

Ronald Meijboom 
"""
print(qa_pipeline({
    'context': context,
    'question': input}))