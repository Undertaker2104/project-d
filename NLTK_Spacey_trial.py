import pandas as pd
import json
from datetime import datetime
import spacy
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

def group_data(data, key1, key2):
    grouped_data = {}
    placeholder_key1 = "niet gespecificeerd"  # Define a placeholder name for rows with key1 as None
    for row in data:
        group_key1 = row[key1] if key1 is not None and not pd.isna(row[key1]) else placeholder_key1
        group_key2 = row[key2] if key2 in row and not pd.isna(row[key2]) else "None"
        if pd.isna(group_key1):
            group_key1 = None  # Replace NaN with None
        if group_key1 not in grouped_data:
            grouped_data[group_key1] = {}
        if group_key2 not in grouped_data[group_key1]:
            grouped_data[group_key1][group_key2] = []
        grouped_data[group_key1][group_key2].append(row)
    return grouped_data

def write_to_json(grouped_data, output_file, columns_to_include):
    # Replace NaN values with None
    def replace_nan(value):
        if isinstance(value, list):
            return [replace_nan(v) for v in value]
        elif pd.isna(value):
            return None
        return value

    # Write the grouped data to a JSON file including only specified columns
    with open(output_file, 'w', encoding='utf-8') as json_file:  # Open file with utf-8 encoding
        json.dump({
            group_key1: {
                group_key2: [{
                    col: replace_nan(row[col]) for col in columns_to_include
                } for row in rows] 
                for group_key2, rows in subgroups.items()
            } 
            for group_key1, subgroups in grouped_data.items()
        }, json_file, indent=2, cls=DateTimeEncoder, ensure_ascii=False)  # Set ensure_ascii to False


if __name__ == "__main__":
    file_path = "translated_service_joborders.xlsx"  # Adjust the file path as necessary
    data = pd.read_excel(file_path, sheet_name="Sheet1")

    # Load the Dutch language model from spaCy
    nlp = spacy.load("nl_core_news_sm")

    # Load the custom NER model
    ner_model = spacy.load("custom_ner_model")

    # Specify the columns you want to combine
    columns_to_combine = ["Service object.Description", "Description", "Memo"]

    # Combine specific columns into one column
    data['Combined_Text'] = data[columns_to_combine].apply(lambda row: ' '.join([str(row[col]) for col in columns_to_combine]), axis=1)

    # Process each text using spaCy and extract token information and named entities
    doc_tokens_pos_entities = []
    for text in data['Combined_Text']:
        doc = nlp(text)
        tokens_pos_entities = [(token.text, token.pos_) for token in doc]
        entities = [(ent.text, ent.label_) for ent in doc.ents]

        # Extract named entities using the custom NER model
        doc = ner_model(text)
        custom_entities = [(ent.text, ent.label_) for ent in doc.ents]

        doc_tokens_pos_entities.append({'tokens_pos': tokens_pos_entities, 'entities': entities, 'custom_entities': custom_entities})

    # Add token-POS and named entity information to DataFrame
    data['SpaCy_Tokens_POS_Entities'] = doc_tokens_pos_entities

    # Remove unnecessary columns
    # data.drop(columns=['Combined_Text'], inplace=True)

    # Convert DataFrame to a list of dictionaries
    data_dict = data.to_dict(orient='records')

    # Group the data
    grouped_data = group_data(data_dict, "Service object.Object location.Relation delivery address ID", "Servicetype")

    # Specify the output file path
    json_file_path = "data.json"

    columns_to_include = ['Code', 'Servicetype', 'Service object.Object location.Relation delivery address ID', 'Combined_Text', 'SpaCy_Tokens_POS_Entities']

    # Write to JSON using the custom function
    write_to_json(grouped_data, json_file_path, columns_to_include)

    print("Data saved to JSON file:", json_file_path)
