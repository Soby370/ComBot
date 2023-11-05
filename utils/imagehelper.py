import os
from random import choice
from PIL import Image, ImageDraw, ImageFont

SHAPES = "assets/shapes/"


def pickImage():
    path = os.path.join(SHAPES, choice(os.listdir(SHAPES)))
    image = Image.open(path)
    return image


accent_colors_hex = [
    "#E0115F",
    "#0067A5",
    "#50C878",
    "#DAA520",
    "#9966CC",
    "#FF6F61",
    "#008080",
    "#FF00FF",
    "#40E0D0",
    "#4B0082",
    "#7FFF00",
    "#E6E6FA",
    "#E97451",
    "#FF91A4",
    "#007FFF",
    "#808000",
    "#FFA500",
    "#8E4585",
]


def create_level_thumb(name, level, role, file_name):
    image = Image.new("RGB", (800, 450), color=choice(accent_colors_hex))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("assets\BungeeSpice-Regular.ttf", size=50)
    #    img = pickImage()
    #    for _ in range(1, 4):
    #       for h in range(1, 4):
    #          image.paste(img, (image.width // _ , image.height // h), mask=img)
    draw.text(
        (image.width // 2, image.height // 2.85), f"{name}", anchor="mm", font=font
    )
    draw.text(
        (image.width // 2, image.height // 2.15),
        "is now",
        font=ImageFont.truetype("assets\Exo2-VariableFont_wght.ttf", size=25),
        anchor="mm",
    )
    draw.text((image.width // 2, image.height // 1.7), role, font=font, anchor="mm")
    image.save(file_name)
    return file_name