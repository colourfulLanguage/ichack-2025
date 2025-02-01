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

model_id_or_path = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionImg2ImgPipeline.from_pretrained(model_id_or_path, torch_dtype=torch.float16)
pipe = pipe.to(device)

# url = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/transformers/tasks/cat.jpg"
# image = Image.open(requests.get(url, stream=True).raw)
image = Image.open("test_portrait.jpg")

print(image.size)
upscaled=pipe(prompt="Blur this persons face",image=image, strength=0.75).images
upscaled[0].save("test_test_portrait.jpg")