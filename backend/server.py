import os
from flask import Flask, session, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import base64
import shutil
import human_detection_utils
import processing_utils

app = Flask(__name__)
# Replace this with a secure, random value for production
app.secret_key = "super-secret-key"

# Ensure the uploads folder exists
UPLOAD_FOLDER = "./uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

state = {
    "count": 0,
    "person_pic_filename": "",
    "main_pic_filename": "",
    "modified_main_pic_filename": "",
    "specific_cut_person": "",
    "body_with_box_path": "",
    "similarity_score": 0,
    "cropped_images_dict": {},
    "face_comparison_dict": {},
    "score_key_order": [],
    "specific_cut_key": (),
    "any_more_faces": 1,
}

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
    print("CALLING GET STATE")
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

    if new_state["body_with_box_path"]:
        new_state["body_with_box_bytes"] = base64.b64encode(
            open(new_state["body_with_box_path"], "rb").read()
        ).decode("utf-8")

    del new_state["specific_cut_person"]
    del new_state["face_comparison_dict"]
    del new_state["cropped_images_dict"]
    del new_state["score_key_order"]
    del new_state["specific_cut_key"]

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

        next_key = tuple(state["specific_cut_key"])
        state["modified_main_pic_filename"] = processing_utils.blur_image(
            os.path.join("./uploads", state["main_pic_filename"]), next_key
            )
        
        
    elif action == "sticker":
        state["count"] -= 1
    else:
        return "Invalid action", 400

    # TODO blur/modify the image
    shutil.copy(
        os.path.join(state["modified_main_pic_filename"]),
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


@app.route("/human_detection", methods=["POST"])
def human_detection():

    faces_rect_list = human_detection_utils.detect_faces(
        os.path.join("./uploads", state["main_pic_filename"])
    )

    list_boxes = human_detection_utils.detect_bodies(
        human_detection_utils.face_with_box_path, faces_rect_list
    )

    # read the human_detection_utils.body_with_box_path and add it into the state

    body_with_box_path = human_detection_utils.body_with_box_path
    state["body_with_box_path"] = body_with_box_path

    state["cropped_images_dict"] = human_detection_utils.extract_boxes(os.path.join("./uploads", state["main_pic_filename"]), faces_rect_list)
    state["face_comparison_dict"] = human_detection_utils.find_same_faces(state["cropped_images_dict"], 
                                           os.path.join("./uploads", state["person_pic_filename"])
                                           )
    state["score_key_order"] = sorted(state["face_comparison_dict"], key=state["face_comparison_dict"].get, reverse=False)
    state["any_more_faces"] = 1
    return "", 200

@app.route("/confirm_human", methods=["POST"])
def confirm_human():
    # show the next highest score and the image
    print("HERE!!")
    if len(state["score_key_order"]) == 0:
        print("No more faces")
        state["any_more_faces"] = 0
        return "", 200
    
    next_key = state["score_key_order"].pop(-1)

    output_img = human_detection_utils.draw_box(os.path.join("./uploads", state["main_pic_filename"]), next_key)

    state["body_with_box_path"] = output_img
    state["similarity_score"] = state["face_comparison_dict"][next_key]
    state["specific_cut_person"] = state["cropped_images_dict"][next_key]
    state["specific_cut_key"] = next_key

    return "", 200

@app.route("/found_person", methods=["POST"])
def found_person():
    # show the next highest score and the image
    print("FOUND PERSON!!")
    return "", 200


if __name__ == "__main__":
    # Run in debug mode for convenience while developing
    app.run(debug=True, port=5123)
