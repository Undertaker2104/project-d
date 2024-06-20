from deep_translator import GoogleTranslator
from enum import StrEnum, IntFlag

# ANSI escape codes
class C(StrEnum):
    COLOR_RED          = "\33[1;34;31m"
    COLOR_YELLOW       = "\33[1;34;93m"
    COLOR_GREEN        = "\33[1;34;32m"
    COLOR_RESET        = "\33[1;34;0m"
    BOLD_SET           = "\33[1m"
    BOLD_RESET         = "\33[22m"

def print_info(msg):
    print(f"{C.COLOR_YELLOW}INFO{C.COLOR_RESET}: {msg}")

import os
import py3langid as langid
import pandas as pd


def translate(key_col, desc_col, memo_col, table):
    """
    Translated description and memo columns to Dutch
    """

    gt = GoogleTranslator(source='auto', target='nl')
    for row in range(len(table)):
        if desc := table[row][desc_col]:
            if langid.classify(desc)[0] != 'nl':
                table[row][desc_col] = gt.translate(desc)

        if memo := table[row][memo_col]:
            translated_segments = []
            for chunk in split_text(memo):
                #print("chunk ", chunk)
                segments = split_string_by_language(chunk)
                #print("segment: ", segments)
                for lang, segment in segments:
                    if lang != "nl" and lang is not None:
                        chunk = GoogleTranslator(
                            source=lang,
                            target='nl'
                        ).translate(chunk)
                    translated_segments.append(chunk)
            table[row][memo_col] = ' '.join(translated_segments)
            print_info(f"translated {table[row][key_col]}")
        

def split_string_by_language(text):
    segments = []
    current_segment = ''
    current_language = None
    
    for word in text.split():
        
        detected_language = langid.classify(word)
        
        if len(detected_language) != 0:
            current_language = detected_language[0]
            if detected_language != 'nl':
                current_segment += ' ' + word
            else:
                segments.append((current_language, current_segment.strip()))
                current_segment = word
        else:
            current_segment += ' ' + word

    segments.append((current_language, current_segment.strip()))

    return segments


def split_text(text, chunk_size=5000):

    if len(text) <= chunk_size:
        return [text]
    
    chunks = []

    while len(text) > chunk_size:
        split_index = text.rfind(' ', 0, chunk_size + 1)
        
        if split_index == -1:
            split_index = chunk_size
        
        chunks.append(text[:split_index].strip())
        
        text = text[split_index:].strip()

    if text:
        chunks.append(text.strip())

    return chunks
    
