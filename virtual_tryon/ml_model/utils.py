import cv2
import numpy as np
from rembg import remove
from PIL import Image

def remove_clothing_bg(image_path):
    """
    Remove background from clothing image using rembg.
    Returns a Pillow Image in RGBA mode.
    """
    pil_img = Image.open(image_path).convert("RGBA")
    out = remove(pil_img)
    return out

def pillow_to_bgra(pil_img):
    """
    Convert Pillow RGBA image to OpenCV BGRA numpy array.
    """
    np_img = np.array(pil_img)
    return cv2.cvtColor(np_img, cv2.COLOR_RGBA2BGRA)

def feather_alpha(img, feather_radius=8):
    """
    Feather the alpha channel for smooth blending.
    """
    if img.shape[2] < 4:
        return img
    alpha = img[:, :, 3]
    blurred = cv2.GaussianBlur(alpha, (0, 0), feather_radius)
    img[:, :, 3] = blurred
    return img

def enhance_image(img):
    """
    Apply sharpening and anti-aliasing for quality.
    """
    kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
    img = cv2.filter2D(img, -1, kernel)
    h, w = img.shape[:2]
    img = cv2.resize(img, (w*2, h*2), interpolation=cv2.INTER_LINEAR)
    img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
    return img
