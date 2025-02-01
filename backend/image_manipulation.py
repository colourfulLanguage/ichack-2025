import cv2
import numpy as np
from typing import Tuple
from PIL import Image
from diffusers import StableDiffusionInpaintPipeline
import torch

def blur_face(image: np.ndarray, face_coords: Tuple[int, int, int, int]) -> np.ndarray:
    """
    Applies a Gaussian blur to a rectangular region in the image corresponding to a face.

    Args:
        image (np.ndarray): The input image in BGR format.
        face_coords (Tuple[int, int, int, int]): Coordinates for the face region as (x1, y1, x2, y2).

    Returns:
        np.ndarray: A copy of the image with the specified face region blurred.
    """
    x1, y1, x2, y2 = face_coords

    # Extract the face region
    face_region: np.ndarray = image[y1:y2, x1:x2]

    # Apply a Gaussian blur. The kernel size (51, 51) can be tuned based on image resolution.
    blurred_face: np.ndarray = cv2.GaussianBlur(face_region, (51, 51), 0)

    # Replace the original face region with the blurred one
    output_image: np.ndarray = image.copy()
    output_image[y1:y2, x1:x2] = blurred_face

    return output_image


def generate_face(
    image: np.ndarray,
    face_coords: Tuple[int, int, int, int],
    prompt: str = "A photorealistic face"
) -> np.ndarray:
    """
    Uses an inpainting diffusion model to generate a new face in the specified area.
    The model uses the entire image as context but only modifies the region defined by the mask.

    Args:
        image (np.ndarray): The input image (with the face region already blurred) in BGR format.
        face_coords (Tuple[int, int, int, int]): Coordinates for the face region as (x1, y1, x2, y2).
        prompt (str): A text prompt to guide the generation of the face.

    Returns:
        np.ndarray: The image with the inpainted (generated) face region.
    """
    x1, y1, x2, y2 = face_coords

    # Create a mask: 255 (white) in the face region where we want inpainting, 0 elsewhere.
    mask: np.ndarray = np.zeros(image.shape[:2], dtype=np.uint8)
    mask[y1:y2, x1:x2] = 255

    # Convert the OpenCV image (BGR) to a PIL image (RGB)
    pil_image: Image.Image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    pil_mask: Image.Image = Image.fromarray(mask)

    # Load the inpainting pipeline (this downloads the model if not cached)
    pipe: StableDiffusionInpaintPipeline = StableDiffusionInpaintPipeline.from_pretrained(
        "runwayml/stable-diffusion-inpainting",
        revision="fp16",
        torch_dtype=torch.float16
    )

    # Move the model to GPU if available
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    pipe = pipe.to(device)

    # Perform inpainting. You may adjust num_inference_steps and other parameters for quality.
    result = pipe(
        prompt=prompt,
        image=pil_image,
        mask_image=pil_mask,
        num_inference_steps=50
    )

    # Retrieve the generated image (the pipeline returns a list of PIL images)
    result_pil: Image.Image = result.images[0]

    # Convert the generated image back to OpenCV format (BGR)
    result_cv2: np.ndarray = cv2.cvtColor(np.array(result_pil), cv2.COLOR_RGB2BGR)
    return result_cv2


# Example usage:
if __name__ == "__main__":
    # Load an example image (replace with your image path)
    input_image: np.ndarray = cv2.imread("input_photo.jpg")

    # Define face coordinates (x1, y1, x2, y2) -- these could come from a face detection module.
    face_rectangle: Tuple[int, int, int, int] = (100, 50, 300, 250)

    # Step 1: Blur the face
    blurred_image: np.ndarray = blur_face(input_image, face_rectangle)
    cv2.imwrite("blurred_face.jpg", blurred_image)

    # Step 2: Generate a new face using the inpainting model
    # You can modify the prompt to influence the appearance of the generated face.
    output_image: np.ndarray = generate_face(blurred_image, face_rectangle, prompt="A photorealistic face with neutral expression")
    cv2.imwrite("generated_face.jpg", output_image)
