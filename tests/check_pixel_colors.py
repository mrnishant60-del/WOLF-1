from PIL import Image

image = Image.open("slotlist_base.png")
pixels = image.load()

test_points = [
    (50, 575),   # Expected left column first blue box
    (560, 575),  # Expected right column first blue box
]

print("Checking pixel colors at expected box positions:")
for x, y in test_points:
    pixel = pixels[x, y]
    print(f"Position ({x}, {y}): RGB = {pixel[:3]}")
