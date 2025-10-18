from PIL import Image
import json

image = Image.open("slotlist_base.png")
pixels = image.load()
width, height = image.size

print(f"Image size: {width}x{height}")

def is_blue_box(pixel):
    r, g, b = pixel[:3]
    # Light blue (right column)
    if 50 < r < 150 and 140 < g < 220 and 200 < b < 255:
        return True
    # Dark blue (left column)
    if r < 30 and 20 < g < 60 and 40 < b < 80:
        return True
    return False

def is_white(pixel):
    r, g, b = pixel[:3]
    return r > 220 and g > 220 and b > 220

slot_positions = []

left_col_scan_x = 65
right_col_scan_x = 565

start_y = 560
spacing_approx = 69

row = 0
for slot_num in range(1, 25):
    is_left_column = (slot_num % 2 == 1)
    
    if is_left_column:
        scan_x = left_col_scan_x
    else:
        scan_x = right_col_scan_x
    
    search_y = start_y + row * spacing_approx
    
    found = False
    for offset in range(-15, 30):
        test_y = search_y + offset
        if test_y < 0 or test_y >= height:
            continue
        
        pixel = pixels[scan_x, test_y]
        if is_blue_box(pixel):
            blue_box_left = scan_x
            while blue_box_left > 0 and is_blue_box(pixels[blue_box_left, test_y]):
                blue_box_left -= 1
            blue_box_left += 1
            
            blue_box_right = scan_x
            while blue_box_right < width - 1 and is_blue_box(pixels[blue_box_right, test_y]):
                blue_box_right += 1
            blue_box_right -= 1
            
            blue_box_top = test_y
            while blue_box_top > 0 and is_blue_box(pixels[scan_x, blue_box_top]):
                blue_box_top -= 1
            blue_box_top += 1
            
            blue_box_bottom = test_y
            while blue_box_bottom < height - 1 and is_blue_box(pixels[scan_x, blue_box_bottom]):
                blue_box_bottom += 1
            blue_box_bottom -= 1
            
            blue_box_center_x = (blue_box_left + blue_box_right) // 2
            blue_box_center_y = (blue_box_top + blue_box_bottom) // 2
            
            white_rect_left = blue_box_right + 8
            white_rect_right = white_rect_left
            mid_y = blue_box_center_y
            while white_rect_right < width - 1 and is_white(pixels[white_rect_right, mid_y]):
                white_rect_right += 1
            white_rect_right -= 1
            
            slot_positions.append({
                "slot": slot_num,
                "blue_box": {
                    "center_x": blue_box_center_x,
                    "center_y": blue_box_center_y,
                    "width": blue_box_right - blue_box_left + 1,
                    "height": blue_box_bottom - blue_box_top + 1
                },
                "white_rect": {
                    "left": white_rect_left,
                    "center_y": blue_box_center_y,
                    "width": white_rect_right - white_rect_left + 1
                }
            })
            
            print(f"Slot {slot_num:2d}: Blue center ({blue_box_center_x:3d}, {blue_box_center_y:3d}), White start {white_rect_left:3d}")
            found = True
            break
    
    if not found:
        print(f"WARNING: Could not find slot {slot_num}")
    
    if not is_left_column:
        row += 1

with open("slot_positions.json", "w") as f:
    json.dump(slot_positions, f, indent=2)

print(f"\nDetected {len(slot_positions)} slots")
print("Positions saved to slot_positions.json")
