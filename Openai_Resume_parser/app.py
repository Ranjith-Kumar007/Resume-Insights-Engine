import os
from flask import Flask, render_template, request, jsonify
import openai
import json
import pandas as pd
from PyPDF2 import PdfReader

app = Flask(__name__)

# Configure OpenAI API Key
openai_key = 'sType your key here'
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
    return '''Please retrieve Name, Phone Number, and email id (@gmail.com)
        from the following resume. If you can't find the information from this article 
        then return "". Do not make things up, give responses as a valid JSON string. The format of that string should be this, 
        {
            "Name": "xyxyxyx xyxy xyxy",
            "Phone Number": "9611648528",
            "email id": "ranjithkumar.422001@gmail.com",
        }
        Resume text:
        ============
    '''

@app.route('/')
def index():
    return render_template('index.html', name="", email="", phone="")

@app.route('/get-insights', methods=['POST'])
def get_insights():
    if request.method == 'POST':
        file = request.files['resume']
        if file:
            os.makedirs('uploads', exist_ok=True)
            file_path = os.path.join('uploads', file.filename)
            file.save(file_path)

            # Extract text from PDF
            pdf_reader = PdfReader(file_path)
            text = ""
            for page_number in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_number].extract_text()

            df = extract_data(text)
            return render_template('index.html', name=df.at[0, 'Value'], email=df.at[1, 'Value'], phone=df.at[2, 'Value'])

        else:
            return jsonify({"error": "No file provided"}), 400

if __name__ == '__main__':
    app.run(debug=True)
