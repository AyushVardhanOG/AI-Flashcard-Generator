from flask import Flask, render_template, request
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():

    from PyPDF2 import PdfReader

    file = request.files["pdf"]

    if file:

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            file.filename
        )

        file.save(filepath)

        reader = PdfReader(filepath)

        text = ""

        for page in reader.pages:
            text += page.extract_text() + "\n"

        return f"""
        <h2>PDF Uploaded Successfully</h2>
        <h3>Extracted Text:</h3>
        <pre>{text[:5000]}</pre>
        """

    return "No file uploaded"


if __name__ == "__main__":
    app.run(debug=True)