import os
from flask import Flask, session, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import base64
import shutil

app = Flask(__name__)
# Replace this with a secure, random value for production
app.secret_key = "super-secret-key"

state = {"count": 0, "person_pic_filename": "", "main_pic_filename": ""}

CORS(app)


@app.route("/")
def index():
    return "Welcome to the bare bones Flask app!"


@app.route("/counter")
def counter():
    count = state.get("count", 0)
    count += 2
    state["count"] = count
    return f"You have visited this route {count} time(s)."


@app.route("/get_state")
def get_state():

    new_state = {s: state[s] for s in state}

    if new_state["person_pic_filename"]:
        new_state["person_pic_bytes"] = base64.b64encode(
            open(
                os.path.join("./uploads", new_state["person_pic_filename"]), "rb"
            ).read()
        ).decode("utf-8")

    if new_state["main_pic_filename"]:
        new_state["main_pic_bytes"] = base64.b64encode(
            open(os.path.join("./uploads", new_state["main_pic_filename"]), "rb").read()
        ).decode("utf-8")

    return new_state


@app.route("/result")
def get_result_image():
    return send_file(
        os.path.join("./uploads", "result_image.jpg"), mimetype="image/jpeg"
    )


@app.route("/modify", methods=["POST"])
def modify_image():
    action = request.json.get("action")
    if action == "blur":
        state["count"] += 1
    elif action == "replace":
        state["count"] -= 1
    else:
        return "Invalid action", 400

    # TODO blur/modify the image
    # for testing, save the main_image to the result_image
    shutil.copy(
        os.path.join("./uploads", state["main_pic_filename"]),
        os.path.join("./uploads", "result_image.jpg"),
    )

    return "State modified", 200


@app.route("/upload", methods=["POST"])
def upload():

    if not "main_pic" in request.files and not "person_pic" in request.files:
        print("No file part")
        return "No file part", 400

    if "main_pic" in request.files:
        file = request.files["main_pic"]
    else:
        file = request.files["person_pic"]

    is_person_pic = "person_pic" in request.files

    if file.filename == "":
        print("No selected file")
        return "No selected file", 400

    # Sanitize the file name and construct the full path
    filename = secure_filename(file.filename)
    filepath = os.path.join("./uploads", filename)

    if is_person_pic:
        state["person_pic_filename"] = filename
    else:
        state["main_pic_filename"] = filename

    # Save the file locally
    file.save(filepath)

    print("Uploaded file:", filename)

    return {"filename": filename}


if __name__ == "__main__":
    # Run in debug mode for convenience while developing
    app.run(debug=True)
