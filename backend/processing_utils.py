import cv2
import numpy as np
import face_recognition

output_blur_path = "output_blurred.jpg"

def blur_image(image, box_coord, padding=100, blur_strength=99, fade_size=80, output_blur_path="output_blurred.jpg"):
    """
    Applies Gaussian blur to a specific face region with a radial fade near the edges.

    :param image_name: Path to the input image
    :param box_coord: Tuple (top, right, bottom, left) defining the bounding box
    :param padding: Extra padding around the face to blur more area
    :param blur_strength: Kernel size for Gaussian blur (must be odd)
    :param fade_size: How close to the edge the fade starts (smaller = sharper transition)
    :param output_blur_path: File path for saving the blurred image
    :return: Path to the saved blurred image
    """

    print("Blurring:", image_name)
    print("Box Coordinates:", box_coord)

    # Load the image
    image = cv2.imread(image_name)
    h_img, w_img = image.shape[:2]  
    blurred_image = image.copy()

    # Unpack box coordinates
    top, right, bottom, left = box_coord

    # Expand the bounding box with padding
    top = max(0, top - padding)
    bottom = min(h_img, bottom + padding)
    left = max(0, left - padding)
    right = min(w_img, right + padding)

    # Extract the face region
    face_region = image[top:bottom, left:right]

    # Ensure blur kernel size is odd
    if blur_strength % 2 == 0:
        blur_strength += 1

    # Apply Gaussian blur
    blurred_face = cv2.GaussianBlur(face_region, (blur_strength, blur_strength), 50)

    # Generate radial fade mask
    h, w = face_region.shape[:2]
    mask = np.zeros((h, w), dtype=np.float32)

    fully_blurred_radius = min(h, w) // 2 - fade_size  # Defines fully blurred center

    for i in range(h):
        for j in range(w):
            distance = np.sqrt((i - h//2)**2 + (j - w//2)**2)
            if distance < fully_blurred_radius:
                mask[i, j] = 1  # Fully blurred center
            else:
                fade_factor = max(0, 1 - (distance - fully_blurred_radius) / fade_size)
                mask[i, j] = fade_factor  

    # Smooth the mask edges
    mask = cv2.GaussianBlur(mask, (51, 51), 30)
    mask = cv2.merge([mask, mask, mask])  # Convert to 3-channel mask

    # Blend the blurred and original image using the mask
    blended_face = (face_region * (1 - mask) + blurred_face * mask).astype(np.uint8)

    # Replace the face region with the blended version
    blurred_image[top:bottom, left:right] = blended_face

    # Save the output
    return blurred_image


def apply_pixelation(image, face_box, padding=50, fade_size=40):
    #pixel size determined by size of image
    
    h_img, w_img = image.shape[:2]

    top, right, bottom, left = face_box

    # Expand bounding box with padding
    top = max(0, top - padding)
    bottom = min(h_img, bottom + padding)
    left = max(0, left - padding)
    right = min(w_img, right + padding)

    max_pixel_size = max(abs(right-left), abs(bottom-top))

    pixel_size = max(1, max_pixel_size // 10)
    # Extract face region
    face_region = image[top:bottom, left:right]

    # Resize smaller to pixelate, then scale back
    h, w = face_region.shape[:2]
    face_small = cv2.resize(face_region, (w // pixel_size, h // pixel_size), interpolation=cv2.INTER_LINEAR)
    pixelated_face = cv2.resize(face_small, (w, h), interpolation=cv2.INTER_NEAREST)

    # Generate radial fade mask
    mask = np.zeros((h, w), dtype=np.float32)
    fully_pixelated_radius = min(h, w) // 2 - fade_size  # Fully pixelated center

    for i in range(h):
        for j in range(w):
            distance = np.sqrt((i - h//2)**2 + (j - w//2)**2)
            if distance < fully_pixelated_radius:
                mask[i, j] = 1  # Fully pixelated center
            else:
                fade_factor = max(0, 1 - (distance - fully_pixelated_radius) / fade_size)
                mask[i, j] = fade_factor  # Gradual fade

    # Smooth the mask edges
    mask = cv2.GaussianBlur(mask, (51, 51), 30)
    mask = cv2.merge([mask, mask, mask])  # Convert to 3-channel mask

    # Blend the pixelated face with original face region using the mask
    blended_face = (face_region * (1 - mask) + pixelated_face * mask).astype(np.uint8)

    # Replace the face region with the blended version
    image[top:bottom, left:right] = blended_face

    return image


def create_best_blur(image_name, face_box):
    image = cv2.imread(image_name)

    pixellated = apply_pixelation(image, face_box)
    blurred_image = blur_image(pixellated, face_box)

    cv2.imwrite(output_blur_path, blurred_image)
    print("Saved:", output_blur_path)


def place_sticker(image_path, box_coords, corner_radius=20, output_path="output_sticker.jpg"):
    """
    Places a rectangular sticker onto an image with rounded ends.

    :param image_path: Path to the original image
    :param sticker_path: Path to the sticker image
    :param box_coords: Tuple (top, right, bottom, left) defining the bounding box
    :param corner_radius: Radius for the rounded ends
    :param output_path: Path to save the output image
    """

    sticker_path = "./test/sticker.jpeg"
    # Load images
    image = cv2.imread(image_path)
    sticker = cv2.imread(sticker_path, cv2.IMREAD_UNCHANGED)  # Load with transparency if available

    # Extract box coordinates
    top, right, bottom, left = box_coords
    width, height = right - left, bottom - top

    # Resize the sticker to exactly fit the bounding box
    sticker_resized = cv2.resize(sticker, (width, height), interpolation=cv2.INTER_LINEAR)

    # Create a mask with rounded corners
    sticker_mask = np.full((height, width), 255, dtype=np.uint8)  # White mask
    cv2.rectangle(sticker_mask, (corner_radius, 0), (width - corner_radius, height), 255, -1)
    cv2.circle(sticker_mask, (corner_radius, height // 2), corner_radius, 255, -1)
    cv2.circle(sticker_mask, (width - corner_radius, height // 2), corner_radius, 255, -1)

    # Convert mask to 3 channels
    sticker_mask = cv2.merge([sticker_mask, sticker_mask, sticker_mask])

    # Apply the mask to the sticker
    sticker_resized = cv2.bitwise_and(sticker_resized, sticker_mask)

    # Overlay the sticker on the original image (direct paste, no blending)
    image[top:bottom, left:right] = sticker_resized

    # Save output
    cv2.imwrite(output_path, image)
    print("Saved:", output_path)
    return output_path


# create_best_blur("uploads/multiple.JPG", (1093, 2221, 1360, 1954))
place_sticker("uploads/multiple.JPG", (1093, 2221, 1360, 1954))