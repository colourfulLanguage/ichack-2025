from diffusers import StableDiffusionImg2ImgPipeline
import torch
from PIL import Image
import numpy as np
import requests
from transformers import pipeline
from accelerate.test_utils.testing import get_backend

# automatically detects the underlying device type (CUDA, CPU, XPU, MPS, etc.)
device, _, _ = get_backend()
# pipe = pipeline(task="image-to-image", model="caidas/swin2SR-lightweight-x2-64", device=device)

    return image

def apply_gaussian_blur(
    image: np.ndarray,
    rect: tuple[int, int, int, int],
    kernel_size: tuple[int, int] = (15, 15),
    sigmaX: float = 0.0
) -> np.ndarray:
    """
    Applies a Gaussian blur to a specified rectangular region of an image.

    Args:
        image (np.ndarray): The input image as a NumPy array.
        rect (Tuple[int, int, int, int]): A tuple (x1, y1, x2, y2) representing
            the top-left (x1, y1) and bottom-right (x2, y2) coordinates of the rectangle.
        kernel_size (Tuple[int, int], optional): The size of the Gaussian kernel.
            Must be positive and odd. Defaults to (15, 15).
        sigmaX (float, optional): Gaussian kernel standard deviation in the X direction.
            A value of 0.0 means it is calculated from the kernel size. Defaults to 0.0.

    Returns:
        np.ndarray: A copy of the image with the specified rectangular region blurred.

    Raises:
        ValueError: If the rectangle coordinates are invalid or out of image bounds.
    """
    x1, y1, x2, y2 = rect
    height, width = image.shape[:2]

    # Check that the rectangle is within the image bounds and the coordinates make sense.
    if x1 < 0 or y1 < 0 or x2 > width or y2 > height or x1 >= x2 or y1 >= y2:
        raise ValueError("Invalid rectangle coordinates: they must be within the image bounds and satisfy x1 < x2 and y1 < y2.")

    result = image.copy()

    # Extract the region of interest (ROI).
    roi = result[y1:y2, x1:x2]
    blurred_roi = cv2.GaussianBlur(roi, kernel_size, sigmaX)
    result[y1:y2, x1:x2] = blurred_roi

    return result


if __name__ == '__main__':

    im_path = "test_portrait.jpg"
    output_im_path = f"blurred_{im_path}"
    image = cv2.imread(im_path)
    if image is None:
        raise FileNotFoundError(f"Could not load image from path: {im_path}")

    # Define the rectangle and kernel size.
    rect = 70, 30, 130, 110
    kernel_size = (11, 11)
    kernel_sigma = 4

    # Apply the Gaussian blur to the specified rectangle.
    try:
        output_img = apply_gaussian_blur(image, rect, kernel_size, kernel_sigma)
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)

    # Save the resulting image.
    if cv2.imwrite(output_im_path, output_img):
        print(f"Processed image saved to {output_im_path}")
    else:
        print("Failed to save the processed image.")


# build_face(image).save("blurred_face")