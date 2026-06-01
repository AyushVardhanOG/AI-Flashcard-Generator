from flask import Flask, render_template, request
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import google.generativeai as genai
import os

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create Gemini model
model = genai.GenerativeModel("gemini-2.5-flash")

# Create Flask app
app = Flask(__name__)

# Upload folder configuration
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():

    file = request.files["pdf"]

    if file:

        # Save uploaded PDF
        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            file.filename
        )

        file.save(filepath)

        # Read PDF
        reader = PdfReader(filepath)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        # Gemini Prompt
        prompt = f"""
Create 10 study flashcards from these notes.

Format exactly like this:

Q: Question
A: Answer

Q: Question
A: Answer

Notes:
{text[:10000]}
"""

        # Generate flashcards
        response = model.generate_content(prompt)

        cards = []

        parts = response.text.split("Q:")

        for part in parts[1:]:

            if "A:" in part:

                question, answer = part.split("A:", 1)

                cards.append({
                    "question": question.strip(),
                    "answer": answer.strip()
                })

        return render_template(
            "flashcards.html",
            cards=cards
        )

    return "No file uploaded"


if __name__ == "__main__":
    app.run(debug=True)