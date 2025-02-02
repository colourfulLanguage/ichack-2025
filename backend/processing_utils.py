import cv2
import face_recognition

def blur_image(image_name, box_coord, padding=30):
  # image_name is the original picture
  image = cv2.imread(image_name)
  blurred_image = image.copy()

  top, right, bottom, left = box_coord
  top = max(0, top - padding)
  bottom = min(h_img, bottom + padding)
  left = max(0, left - padding)
  right = min(w_img, right + padding)
  
  face_region = image[top:bottom, left:right]

  blurred_face = cv2.GaussianBlur(face_region, (99, 99), 30)
  h, w = face_region.shape[:2]
  mask = np.zeros((h, w), dtype=np.float32)

  for i in range(h):
    for j in range(w):
      distance = np.sqrt((i - h//2)**2 + (j - w//2)**2)
      mask[i, j] = max(0, 1 - (distance / (max(h, w) / 2)))

  mask = cv2.GaussianBlur(mask, (99, 99), 30)  # Smooth mask edges
  mask = cv2.merge([mask, mask, mask])  # Convert to 3 channels

  # Blend original and blurred image using the mask
  blended_face = (face_region * (1 - mask) + blurred_face * mask).astype(np.uint8)

  # Replace the face region with the blended version
  blurred_image[top:bottom, left:right] = blended_face

  cv2.imwrite("output_blurred.jpg", blurred_image)
  print("Saved: output_blurred.jpg")
  return blurred_image


  

