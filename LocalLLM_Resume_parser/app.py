import os
from flask import Flask, render_template, request, jsonify
import re
from langchain.llms import LlamaCpp
from langchain import PromptTemplate, LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from pypdf import PdfReader

app = Flask(__name__)

# Replace with your model path
model_path = "C:/Users/Ranjith/Downloads/nous-hermes-llama2-13b.Q4_0.gguf"

# Prompt template
template = """Text: {text}

Extracted Information:
Name: {name}
Phone Number: {phone}
Email: {email}
"""

prompt = PromptTemplate(template=template, input_variables=["text", "name", "phone", "email"])

# Callbacks support token-wise streaming
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

# Configure LlamaCpp
n_gpu_layers = 40  # Change this value based on your model and your GPU VRAM pool.
n_batch = 512  # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.

llm = LlamaCpp(
    model_path=model_path,
    n_gpu_layers=n_gpu_layers,
    n_batch=n_batch,
    callback_manager=callback_manager,
    verbose=True,
)

llm_chain = LLMChain(prompt=prompt, llm=llm)

def extract_information(text):
    # Split the text into two chunks
    chunk_size = len(text) // 2
    chunks = [text[:chunk_size], text[chunk_size:]]

    # Initialize variables to store extracted information
    name, phone, email = "", "", ""

    # Process each chunk
    for chunk in chunks:
        # Pass the input as a dictionary
        input_data = {"text": chunk, "name": " ", "phone": " ", "email": " "}
        response = llm_chain.run(input_data)

        # Extract information using regular expressions
        name_match = re.search(r"Name: (.+)", response)
        phone_match = re.search(r"Phone Number: (.+)", response)
        email_match = re.search(r"Email: (.+)", response)

        # Update extracted information
        if name_match:
            name = name_match.group(1)
        if phone_match:
            phone = phone_match.group(1)
        if email_match:
            email = email_match.group(1)

    return name, phone, email

@app.route('/')
def index():
    return render_template('index.html')

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

            # Extract information from the text
            name, phone, email = extract_information(text)

            return render_template('results.html', name=name, email=email, phone=phone)

        else:
            return jsonify({"error": "No file provided"}), 400

if __name__ == '__main__':
    app.run(debug=True)
