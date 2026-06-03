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
    mode = request.form["mode"]

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

        # ==========================
        # FLASHCARDS
        # ==========================

        if mode == "flashcards":

            prompt = f"""
Create 10 study flashcards.

Format:

Q: Question
A: Answer

Notes:
{text[:10000]}
"""

        # ==========================
        # MCQS
        # ==========================

        elif mode == "mcqs":

            prompt = f"""
Create exactly 10 multiple choice questions.

Format EXACTLY like this:

Q1. Question text
A) Option A
B) Option B
C) Option C
D) Option D
Correct Answer: A

Q2. Question text
A) Option A
B) Option B
C) Option C
D) Option D
Correct Answer: B

Do not add introductions.
Do not add explanations.
Only output questions.

Notes:
{text[:10000]}
"""

        # ==========================
        # QUIZ
        # ==========================

        else:

            prompt = f"""
Create 10 quiz questions.

Format:

Q1. Question

A) Option
B) Option
C) Option
D) Option

Correct Answer: X

Notes:
{text[:10000]}
"""

        # Generate AI response
        response = model.generate_content(prompt)

        # ==========================
        # FLASHCARDS PAGE
        # ==========================

        if mode == "flashcards":

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

        # ==========================
        # MCQ PAGE
        # ==========================

        elif mode == "mcqs":

            mcq_blocks = response.text.split("Q")

            mcqs = []

            for block in mcq_blocks:

                block = block.strip()

                if not block:
                    continue

                full_mcq = "Q" + block

                lines = full_mcq.split("\n")

                question_lines = []
                answer = ""

                for line in lines:

                    if "Correct Answer:" in line:

                        answer = line.replace(
                            "Correct Answer:",
                            ""
                        ).strip()

                    else:

                        question_lines.append(line)

                mcqs.append({
                    "question": "\n".join(question_lines),
                    "answer": answer
                })

            return render_template(
                "mcqs.html",
                mcqs=mcqs
            )

        # ==========================
        # QUIZ PAGE
        # ==========================

        else:

            questions = response.text.split("\n\n")

            return render_template(
                "quiz.html",
                questions=questions
            )

    return "No file uploaded"


if __name__ == "__main__":
    app.run(debug=True)