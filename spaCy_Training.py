import spacy
import random
from spacy.training.example import Example

# Load the base model (e.g., Dutch language model)
nlp = spacy.blank("nl")

# Define the training data
TRAIN_DATA = [
    ("Pos.818 Elektro, Prikkersetlijn C Band onder trommel loopt niet 4660-860 Zaaimachine tek. 40540017  Wij hebben een storing aan een rollerband onder de prikkerrol van lijn 8. Dit is een 48V motor, voeding komt vanuit een print (zie foto)  Bij de andere twee printen brand er boven een groene LED, bij de middelste zie je hem knipperen (motor draait ook niet) Onder voorbehoud vermoed ik dat het probleem de print is. (koolborstels zijn vervangen)  Bij deze opdracht om de storing spoedig te verhelpen, graag hoor ik wanneer jullie langs kunnen komen.  Florensis ordernummer: 4660-860",
     {"entities": [(0, 15, "MACHINE_NAME"), (65, 84, "MACHINE_NAME"), (131, 141, "MACHINE_PART"), (185, 194, "MACHINE_NAME")]}),
    ("Ombouw zaailijn Buffersysteem communicatie zaaimachine Flier nan",
     {"entities": [(7, 29, "MACHINE_NAME")]}),
    ("Pos.080 Opvang bak onderhoud lijn nakijken nan",
     {"entities": [(0, 18, "MACHINE_PART")]}),
    ("Storing Stapelaar Kisten wilden niet uit stapelaar lopen. X34B wekt niet meer",
     {"entities": [(8, 24, "MACHINE_NAME"), (58, 62, "MACHINE_NAME")]}),
    ("Storing ergon tros 40608001 Obe Jan de Jong 004915234150821 o.dejong@westhof-bio.de ergon tros pakt een complete stapel, en wil die ook in 1x wegdraaien. waarschijnlijk problemen met de encoder",
     {"entities": [(8, 27, "MACHINE_NAME"), (84, 89, "MACHINE_NAME")]}),
    ("specs bindmateriaal Naam: ERIK HELDERMAN Tel.nr. waarop te bereiken: 06-22655953 Bedrijfsnaam: HARVEST HOUSE Voor welke BV: Visser/Viscon Soort melding: ONDERDELEN  e.helderman@harvesthouse.nl  Wie wil men spreken: Mag het ook een andere collega zijn: Waar gaat het over: BANDEN BIJ COMBIVLIET? Welke info kan er worden doorgegeven: Binnen welke termijn moet contact op worden genomen: GEEN HAAST  vraagt om de specificaties van het bind materiaal. 12-5-2017 opgevraagd bij OMS",
     {"entities": [(283, 293, "MACHINE_NAME")]}),
]

# Add the named entity labels to the pipeline
ner = nlp.add_pipe("ner", last=True)
ner.add_label("MACHINE_NAME")
ner.add_label("MACHINE_PART")

# Disable other pipelines for efficiency
pipe_exceptions = ["ner"]
unaffected_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]

# Training the model
with nlp.disable_pipes(*unaffected_pipes):
    optimizer = nlp.begin_training()
    for itn in range(10):  # Adjust number of iterations as needed
        random.shuffle(TRAIN_DATA)
        for text, annotations in TRAIN_DATA:
            # Convert to spaCy Example
            example = Example.from_dict(nlp.make_doc(text), annotations)
            # Update the model with the Example
            nlp.update([example], sgd=optimizer)

# Save the trained model
nlp.to_disk("custom_ner_model")

# Load the trained model
nlp_loaded = spacy.load("custom_ner_model")

# Test the trained model
texts = [
    "De machine met serienummer ABC-123 is gerepareerd.",
    "Ombouw zaailijn Buffersysteem communicatie zaaimachine Flier nan",
    "Pos.080 Opvang bak onderhoud lijn nakijken nan",
    "Storing Stapelaar Kisten wilden niet uit stapelaar lopen. X34B wekt niet meer",
    "Storing ergon tros 40608001 Obe Jan de Jong 004915234150821 o.dejong@westhof-bio.de ergon tros pakt een complete stapel, en wil die ook in 1x wegdraaien. waarschijnlijk problemen met de encoder",
    "Nieuwe encoder en belt",
    "specs bindmateriaal Naam: ERIK HELDERMAN Tel.nr. waarop te bereiken: 06-22655953 Bedrijfsnaam: HARVEST HOUSE Voor welke BV: Visser/Viscon Soort melding: ONDERDELEN  e.helderman@harvesthouse.nl  Wie wil men spreken: Mag het ook een andere collega zijn: Waar gaat het over: BANDEN BIJ COMBIVLIET? Welke info kan er worden doorgegeven: Binnen welke termijn moet contact op worden genomen: GEEN HAAST  vraagt om de specificaties van het bind materiaal. 12-5-2017 opgevraagd bij OMS"
]

for text in texts:
    doc = nlp_loaded(text)
    for ent in doc.ents:
        print(ent.text, ent.label_)
    print()
