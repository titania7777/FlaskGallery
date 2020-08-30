import os
import sys
from PIL import Image
from utils.settings import img_root_path

def img_compressor(file, quality=75):
    img_path = os.path.join(img_root_path, file)
    picture = Image.open(img_path)
    picture.save(os.path.join(img_root_path, 'temp_' + file), "JPEG", optimize=True, quality=quality)
    remove_temp(file)

def remove_temp(file):
    original = os.path.join(img_root_path, file)
    compressed = os.path.join(img_root_path, 'temp_' + file)
    os.remove(original)
    os.rename(original, compressed)

def remove_image(filename):
    os.remove(filename)

def img_compressor_byte(byte, filename, quality=75):
    picture = Image.open(byte)
    picture.save(os.path.join(img_root_path, filename), optimize=True, quality=quality)