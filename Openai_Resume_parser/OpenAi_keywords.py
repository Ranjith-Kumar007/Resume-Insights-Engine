import openai
import pandas as pd
import time
import json
from pypdf import PdfReader

reader = PdfReader("C:/Users/Ranjith/Desktop/Resumes/Ranjith_Resume.pdf")

# Print the number of pages in the PDF
print(f"There are {len(reader.pages)} Pages")

# Get the first page (index 0) 
page = reader.pages[0]
# Use extract_text() to get the text of the page
text= page.extract_text()


openai_key = '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'
openai.api_key = openai_key

def extract_data(text):
    prompt = resume() + text
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
)
    content = response.choices[0]['message']['content']

    try:
        data = json.loads(content)
        return pd.DataFrame(data.items(), columns=["Measure", "Value"])

    except (json.JSONDecodeError, IndexError):
        pass

    return pd.DataFrame({
        "Measure": ["Name", "Phone Number", "Email Id"],
        "Value": ["", "", ""]
    })

def resume():
    return '''Please retrieve Name, Phone Number and  email id (@gmail.com)
    from the following resume. If you can't find the information from this article 
    then return "". Do not make things up give responses as a valid JSON string. The format of that string should be this, 
    {
        "Name": "xyxyxyx xyxy xyxy",
        "Phone Number": "9611648528",
        "email id": "ranjithkumar.422001@gmail.com",
        
    }
    Resume text:
    ============

    '''

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    
    df = extract_data(text)

    print(df.to_string())