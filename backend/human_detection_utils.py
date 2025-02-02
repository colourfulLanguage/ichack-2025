import cv2
from ultralytics import YOLO
import face_recognition

face_with_box_path = "output_face_with_boxes.jpg"
body_with_box_path = "output_body_with_boxes.jpg"
draw_boxes_output_path = "draw_boxes_output.jpg"


def detect_faces(image_name):
    """returns a list of tuples (top, right, bottom, left)"""
    # Load the image
    image = cv2.imread(image_name)

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Detect faces
    face_locations = face_recognition.face_locations(rgb_image)

    # Draw rectangles around faces
    for top, right, bottom, left in face_locations:
        cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 10)
    # Show image
    # cv2.imshow("Detected Faces", image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    cv2.imwrite(face_with_box_path, image)
    return face_locations


def is_contained(box, container):
    """Check if 'box' is fully inside 'container'"""
    top, right, bottom, left = box
    B_top, B_right, B_bottom, B_left = container

    return B_top <= top and B_left <= left and B_right >= right and B_bottom >= bottom


def contains_face(bounding_box, rectangles):
    """Return all rectangles contained in bounding_box"""
    for rect in rectangles:
        if is_contained(rect, bounding_box):
            return True
    return False


def detect_bodies(image_name, faces_rect_list):
    # returns a list of tuples (top, right, bottom, left)
    model = YOLO("yolov8n.pt")

    # Load the image
    image_path = image_name
    image = cv2.imread(image_path)

    # Run YOLOv8 to detect humans
    results = model(image)

    list_boxes = []

    # Draw bounding boxes
    for result in results:
        for box, class_id in zip(result.boxes.xyxy, result.boxes.cls):
            x1, y1, x2, y2 = map(int, box)  # Convert coordinates to int

            if int(class_id) == 0:  # Class ID 0 corresponds to "person"

                if contains_face((y1, x2, y2, x1), faces_rect_list):
                    cv2.rectangle(
                        image, (x1, y1), (x2, y2), (0, 255, 0), 10
                    )  # Green box
                    list_boxes.append((y1, x2, y2, x1))  # (top, right, bottom, left)

    # Save the output image
    cv2.imwrite(body_with_box_path, image)

    return list_boxes


def extract_box(image, box_coord):
    """box coord in format (top, right, bottom, left)"""
    return image[box_coord[0] : box_coord[2], box_coord[3] : box_coord[1]]


def extract_boxes(image_name, list_boxes):
    """list_boxes in format [(top, right, bottom, left)]
    returns dict of box to the name of the cropped image of the cropped pictures
    """

    image = cv2.imread(image_name)
    cropped_images_names_dict = {}

    for i, box in enumerate(list_boxes):
        # Crop the image using numpy slicing
        cropped = extract_box(image, box)

        # Save each cropped region as a separate image
        output_filename = f"cropped_{i}.jpg"
        cv2.imwrite(output_filename, cropped)
        print(f"Saved: {output_filename}")

        cropped_images_names_dict[box] = output_filename

    return cropped_images_names_dict  # List of cropped image arrays


def face_comparison(image_name_1, image_name_2):
    image1 = cv2.imread(image_name_1)
    image2 = cv2.imread(image_name_2)

    # Convert to RGB (face_recognition requires RGB format)
    rgb_image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2RGB)
    rgb_image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2RGB)

    # Detect faces and extract encodings
    face_locations1 = face_recognition.face_locations(rgb_image1)
    face_locations2 = face_recognition.face_locations(rgb_image2)

    if face_locations1 and face_locations2:  # Ensure faces are detected
        face_encoding1 = face_recognition.face_encodings(
            rgb_image1, [face_locations1[0]]
        )[0]
        face_encoding2 = face_recognition.face_encodings(
            rgb_image2, [face_locations2[0]]
        )[0]

        # Compare faces
        results = face_recognition.compare_faces([face_encoding1], face_encoding2)
        distance = face_recognition.face_distance([face_encoding1], face_encoding2)

        if results[0]:
            print(f"Faces Match! (Similarity Score: {1 - distance[0]:.2f})")
            return (True, 1 - distance[0])

        else:
            print(f"Faces Do NOT Match! (Difference Score: {distance[0]:.2f})")
            return (False, distance[0])
    else:
        print("Could not detect faces in one or both images.")
        return (False, 0)


def find_same_faces(cropped_images_dict, opt_out_face):
    """returns similarity score dict for boxes"""
    similar_faces_dict = {}

    for key, value in cropped_images_dict.items():
        match, score = face_comparison(value, opt_out_face)
        if match:
            # TODO: do this only if score is > 0.5
            similar_faces_dict[key] = score

    return similar_faces_dict


def test():
    test_photo = "test/fullbody-multiple.JPG"
    opt_out_face = "test/opt-out.JPG"

    faces_rect_list = detect_faces(test_photo)
    list_boxes = detect_bodies(test_photo, faces_rect_list)

    cropped_images_dict = extract_boxes(test_photo, list_boxes)
    print(cropped_images_dict)
    face_comparison_dict = find_same_faces(cropped_images_dict, opt_out_face)
    print(face_comparison_dict)
    for key, value in face_comparison_dict.items():
        print("Box ", key, " similarity score: ", value)
        print("Picture at ", cropped_images_dict[key])
        print()


def draw_box(image_name, box_coord):
    image = cv2.imread(image_name)

    top, right, bottom, left = box_coord
    cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 10)

    cv2.imwrite(draw_boxes_output_path, image)
    return draw_boxes_output_path


if __name__ == "__main__":
    test()
