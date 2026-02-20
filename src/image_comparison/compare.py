import os

import cv2
import numpy as np
from rich import print as rprint


def get_image_file_names(path: str):
    return [f for f in os.listdir(path) if f.endswith((".jpg", ".jpeg", ".png"))]


def build_images(directory_path: str, file_names: list[str]):
    return [cv2.imread(os.path.join(directory_path, f)) for f in file_names]


def unique_pixels(img: cv2.typing.MatLike):
    return np.unique(img.reshape(-1, img.shape[2]), axis=0).shape[0]


def main(p: str):
    """
    p:str
    this is your directory path where the images are.
    it will output your most unique and most uniform images.
    this isn't a perfect, but a cool representation of interesting images
    """
    files = get_image_file_names(p)
    rprint(f"Found {len(files)} files in {p}")
    images = build_images(p, files)
    rprint("[yellow]Built images")
    rprint("[yellow]Determining pixel uniqueness")
    uniqueness = np.array([unique_pixels(i) for i in images])
    most_unique_file = files[uniqueness.argmax()]
    most_uniform_file = files[uniqueness.argmin()]
    t5_idx = np.argpartition(uniqueness, -5)[-5:]
    t5_files = [f"{os.path.join(p + files[i])}" for i in t5_idx]
    b5_idx = np.argpartition(uniqueness, 5)[:5]
    b5_files = [f"{os.path.join(p + files[i])}" for i in b5_idx]
    print(f"MOST UNIQUE: {p + most_unique_file}")
    print(f"MOST UNIFORM: {p + most_uniform_file}")
    print("TOP 5 UNIQUE:")
    [print(f) for f in t5_files]
    print("TOP 5 UNIFORM:")
    [print(f) for f in b5_files]
