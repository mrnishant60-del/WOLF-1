from PIL import Image, ImageDraw, ImageFont
import json

# Load measured positions
with open("slot_positions.json", "r") as f:
    positions = json.load(f)

# Standardize all positions - right column is correct, fix left column to match quality
all_positions = {}

# Corrected positions for ALL slots with consistent centering
# Left column blue box center: x=68, white rect start: x=108
# Right column uses measured positions (they're already correct)
corrected_positions = {
    1: {"blue_box": {"center_x": 68, "center_y": 558}, "white_rect": {"left": 108, "center_y": 558}},
    2: {"blue_box": {"center_x": 560, "center_y": 573}, "white_rect": {"left": 600, "center_y": 573}},
    3: {"blue_box": {"center_x": 68, "center_y": 624}, "white_rect": {"left": 108, "center_y": 624}},
    4: {"blue_box": {"center_x": 560, "center_y": 638}, "white_rect": {"left": 600, "center_y": 638}},
    5: {"blue_box": {"center_x": 68, "center_y": 707}, "white_rect": {"left": 108, "center_y": 707}},
    6: {"blue_box": {"center_x": 562, "center_y": 703}, "white_rect": {"left": 604, "center_y": 703}},
    7: {"blue_box": {"center_x": 68, "center_y": 773}, "white_rect": {"left": 108, "center_y": 773}},
    8: {"blue_box": {"center_x": 561, "center_y": 768}, "white_rect": {"left": 602, "center_y": 768}},
    9: {"blue_box": {"center_x": 68, "center_y": 836}, "white_rect": {"left": 108, "center_y": 836}},
    10: {"blue_box": {"center_x": 562, "center_y": 834}, "white_rect": {"left": 603, "center_y": 834}},
    11: {"blue_box": {"center_x": 68, "center_y": 899}, "white_rect": {"left": 108, "center_y": 899}},
    12: {"blue_box": {"center_x": 561, "center_y": 899}, "white_rect": {"left": 602, "center_y": 899}},
    13: {"blue_box": {"center_x": 68, "center_y": 964}, "white_rect": {"left": 108, "center_y": 964}},
    14: {"blue_box": {"center_x": 560, "center_y": 964}, "white_rect": {"left": 601, "center_y": 964}},
    15: {"blue_box": {"center_x": 68, "center_y": 1029}, "white_rect": {"left": 108, "center_y": 1029}},
    16: {"blue_box": {"center_x": 567, "center_y": 1029}, "white_rect": {"left": 601, "center_y": 1029}},
    17: {"blue_box": {"center_x": 68, "center_y": 1094}, "white_rect": {"left": 108, "center_y": 1094}},
    18: {"blue_box": {"center_x": 561, "center_y": 1094}, "white_rect": {"left": 601, "center_y": 1094}},
    19: {"blue_box": {"center_x": 68, "center_y": 1160}, "white_rect": {"left": 108, "center_y": 1160}},
    20: {"blue_box": {"center_x": 562, "center_y": 1160}, "white_rect": {"left": 602, "center_y": 1160}},
    21: {"blue_box": {"center_x": 68, "center_y": 1224}, "white_rect": {"left": 108, "center_y": 1224}},
    22: {"blue_box": {"center_x": 562, "center_y": 1224}, "white_rect": {"left": 601, "center_y": 1224}},
    23: {"blue_box": {"center_x": 68, "center_y": 1289}, "white_rect": {"left": 108, "center_y": 1289}},
    24: {"blue_box": {"center_x": 562, "center_y": 1289}, "white_rect": {"left": 601, "center_y": 1289}},
}

for slot_num, pos_data in corrected_positions.items():
    all_positions[slot_num] = {"slot": slot_num, "blue_box": pos_data["blue_box"], "white_rect": pos_data["white_rect"]}

# Generate team names
slots_data = {}
for i in range(1, 25):
    slots_data[i] = f"Team {i}"

# Open the base image
image = Image.open("slotlist_base.png")
image = image.convert("RGB")

# Load fonts - smaller sizes
try:
    slot_font = ImageFont.truetype("robo-bold.ttf", 32)
    team_font = ImageFont.truetype("robo-bold.ttf", 26)
except:
    slot_font = ImageFont.load_default()
    team_font = ImageFont.load_default()

draw = ImageDraw.Draw(image)

# Draw text using measured positions
for slot_num in range(1, 25):
    if slot_num not in all_positions:
        print(f"WARNING: Slot {slot_num} position not found")
        continue
    
    pos = all_positions[slot_num]
    team_name = slots_data[slot_num]
    
    # Get measured positions - use them directly without overrides
    blue_center_x = pos["blue_box"]["center_x"]
    blue_center_y = pos["blue_box"]["center_y"]
    white_start_x = pos["white_rect"]["left"]
    white_center_y = pos["white_rect"]["center_y"]
    
    # Draw slot number (centered in blue box)
    slot_text = str(slot_num)
    bbox = draw.textbbox((0, 0), slot_text, font=slot_font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    slot_x = blue_center_x - text_width // 2
    slot_y = blue_center_y - text_height // 2
    
    draw.text((slot_x, slot_y), slot_text, fill=(255, 255, 255), font=slot_font)
    
    # Draw team name (left-aligned in white rectangle)
    team_bbox = draw.textbbox((0, 0), team_name, font=team_font)
    team_text_height = team_bbox[3] - team_bbox[1]
    
    team_x = white_start_x + 8
    team_y = white_center_y - team_text_height // 2
    
    draw.text((team_x, team_y), team_name, fill=(0, 0, 0), font=team_font)

# Save the result
image.save("slotlist_output.png")
print("Slotlist created with measured positions!")
print(f"All 24 slots filled successfully")
