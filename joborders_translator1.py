from deep_translator import GoogleTranslator
import pandas as pd
import langid
import os



def translate(inputfile, outputfile):
    #skiprows=13999
    data = pd.read_excel(inputfile, nrows=6999)


    counter = 0
    for x in range(0, len(data)):
        counter +=1 
        os.system('cls')
        #print(f"{counter/max*100} %")
        print(counter)
        
    #8, 10, 11, 12, 13, 14
    #11, 12, 13, 14
        

        val = f"{data.values[x][8]}"
        if val != "nan":
            translation = GoogleTranslator(source='auto', target='nl').translate(data.values[x][8])
            data.iat[x, 8] = translation
        
        val = f"{data.values[x][10]}"
        if val != "nan":
            translation = GoogleTranslator(source='auto', target='nl').translate(data.values[x][10])
            data.iat[x, 10] = translation

        for i in range(11, 15):
            val = f"{data.values[x][i]}"
            if val != "nan":
                translated_text = ''
                chunks = split_text(data.values[x][i])

                for chunk in chunks:
                    segments = split_string_by_language(chunk)

                translated_segments = GoogleTranslator(source='auto', target='nl').translate_batch(segments)
                for translated_segment in translated_segments:
                    if translated_segment != None:
                        translated_text += translated_segment + ' '
                    

            
            data.iat[x, 9] = translated_text.strip()

    data.to_excel(outputfile, index=False, header=False)
    #, header=False  mode='a',

def split_string_by_language(text):
    segments = []
    current_segment = ''
    current_language = None
    
    for word in text.split():
        
        detected_language = langid.classify(word)
        
        if len(detected_language) != 0:
            
            if detected_language != 'nl':
                current_segment += ' ' + word
            else:
                segments.append((current_language, current_segment.strip()))
                current_segment = word
        else:
            current_segment += ' ' + word

    segments.append(current_segment.strip())

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



if __name__ == "__main__":
    input_file = './Data/Service_joborders.xlsx'  
    output_file = './Data/translated_service_joborders_excel.xlsx'  
    translate(input_file, output_file)
    #translation(input_file, output_file)
    #test()
    
