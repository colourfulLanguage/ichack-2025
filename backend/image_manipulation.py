from diffusers import StableDiffusionImg2ImgPipeline
import torch
from PIL import Image
import numpy as np
import cv2
import requests
from transformers import pipeline
from accelerate.test_utils.testing import get_backend

# automatically detects the underlying device type (CUDA, CPU, XPU, MPS, etc.)
device, _, _ = get_backend()
# pipe = pipeline(task="image-to-image", model="caidas/swin2SR-lightweight-x2-64", device=device)

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
        rect (Tuple[int, int, int, int]): A tuple (y1, x2, y2, x1) representing
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

    y1, x2, y2, x1 = rect
    height, width = image.shape[:2]

    # Check that the rectangle is within the image bounds and the coordinates make sense.
    if x1 < 0 or y1 < 0 or x2 > width or y2 > height or x1 >= x2 or y1 >= y2:
        raise ValueError(
            "Invalid rectangle coordinates: they must be within the image bounds and satisfy x1 < x2 and y1 < y2.")

    result = image.copy()

    # Extract the region of interest (ROI).
    roi = result[y1:y2, x1:x2]
    blurred_roi = cv2.GaussianBlur(roi, kernel_size, sigmaX)
    result[y1:y2, x1:x2] = blurred_roi

    return result


def generate_transparent_mask(
        image: np.ndarray,
        rect: tuple[int, int, int, int]
) -> np.ndarray:
    """
    Generates an RGBA mask for the input image where the specified rectangular region is transparent.

    The mask is created with the same dimensions as the input image. Every pixel is white with full
    opacity (RGBA: (255, 255, 255, 255)), except for the area defined by the rectangle, which is set
    to be fully transparent (alpha = 0).

    Args:
        image (np.ndarray): The input image as a NumPy array.
        rect (Tuple[int, int, int, int]): A tuple (x1, y1, x2, y2) representing the rectangle area.

    Returns:
        np.ndarray: An RGBA image (mask) as a NumPy array.
    """
    height, width = image.shape[:2]
    # Create a white image with full opacity (4 channels: R, G, B, A)
    mask = np.full((height, width, 4), (0, 0, 0, 255), dtype=np.uint8)

    y1, x2, y2, x1 = rect
    # Set the alpha channel of the rectangular area to 0 (transparent)
    mask[y1:y2, x1:x2, :] = (255, 255, 255, 255)

    return mask


def crop_square_containing_rect(image, rect, allowed_sizes=(256, 512, 1024)):
    """
    Crop a square region from the image that fully contains the given rectangle.
    The square's side length is chosen as the smallest allowed size that is
    at least as large as the rectangle's width or height.

    Parameters
    ----------
    image : numpy.ndarray
        The input image.
    rect : tuple
        The rectangle coordinates in (top, right, bottom, left) order.
    allowed_sizes : tuple of ints, optional
        Allowed square sizes (in pixels). Default is (256, 512, 1024).

    Returns
    -------
    cropped : numpy.ndarray
        The cropped square region from the image.

    Raises
    ------
    ValueError
        If the rectangle is too large for any of the allowed sizes.
    """
    # Unpack rectangle coordinates.
    top, right, bottom, left = rect

    # Determine the required size (the max of width and height)
    rect_width = right - left
    rect_height = bottom - top
    required_size = max(rect_width, rect_height)

    # Choose the smallest allowed size that is >= required_size
    allowed_sizes = sorted(allowed_sizes)
    crop_size = None
    for size in allowed_sizes:
        if size >= required_size:
            crop_size = size
            break
    if crop_size is None:
        raise ValueError("The rectangle is too large for the allowed crop sizes.")

    # Compute the center of the rectangle.
    center_x = (left + right) / 2
    center_y = (top + bottom) / 2

    # Compute initial crop coordinates centered on the rectangle.
    x_start = int(round(center_x - crop_size / 2))
    y_start = int(round(center_y - crop_size / 2))
    x_end = x_start + crop_size
    y_end = y_start + crop_size

    # Get image dimensions.
    img_height, img_width = image.shape[:2]

    # Adjust the crop if it would fall outside the image boundaries.
    if x_start < 0:
        x_start = 0
        x_end = crop_size
    if y_start < 0:
        y_start = 0
        y_end = crop_size
    if x_end > img_width:
        x_end = img_width
        x_start = img_width - crop_size
    if y_end > img_height:
        y_end = img_height
        y_start = img_height - crop_size

    # (Optional) Final check to ensure the crop fully contains the rectangle.
    if not (x_start <= left and right <= x_end and y_start <= top and bottom <= y_end):
        raise ValueError("Unable to position the crop so that it fully contains the rectangle.")

    # Return the cropped square.
    return image[y_start:y_end, x_start:x_end]


if __name__ == '__main__':

    im_path = "tina_output.png"
    output_im_path = f"blurred_{im_path}"
    masked_output = f"masked_{output_im_path}"

    image = cv2.imread(im_path)
    if image is None:
        raise FileNotFoundError(f"Could not load image from path: {im_path}")

    # Define the rectangle and kernel size.
    x1, y1 = 320, 150
    x2, y2 = 400, 250
    rect = y1, x2, y2, x1
    kernel_size = (11, 11)
    kernel_sigma = 4

    # Apply the Gaussian blur to the specified rectangle.
    try:
        output_img = apply_gaussian_blur(image, rect, kernel_size, kernel_sigma)
        masked_img = generate_transparent_mask(image, rect)
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)

    # Save the resulting image.
    if cv2.imwrite(output_im_path, crop_square_containing_rect(output_img, rect, allowed_sizes=(512,))):
        print(f"Processed image saved to {output_im_path}")
    else:
        print("Failed to save the processed image.")

    if cv2.imwrite(masked_output, crop_square_containing_rect(masked_img, rect, allowed_sizes=(512,))):
        print(f"Processed image saved to {masked_output}")
    else:
        print("Failed to save the processed image.")

# build_face(image).save("blurred_face")