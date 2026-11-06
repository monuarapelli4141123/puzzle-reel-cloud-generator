import math
from PIL import Image, ImageDraw, ImageFont

def make_puzzle_base():
    # 1080x1920 vertical canvas
    W, H = 1080, 1920
    img = Image.new("RGB", (W, H), color=(26, 26, 46)) # Deep cozy navy/indigo
    draw = ImageDraw.Draw(img)

    # 1. Header Card
    # Banner background
    draw.rounded_rectangle([60, 100, 1020, 320], radius=30, fill=(40, 44, 76), outline=(255, 204, 0), width=4)
    
    # Try default or standard fonts
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 60)
        font_sub = ImageFont.truetype("arialbd.ttf", 38)
        font_tag = ImageFont.truetype("arial.ttf", 30)
    except:
        font_title = font_sub = font_tag = ImageFont.load_default()

    draw.text((W/2, 170), "FIND THE ODD ONE OUT!", fill=(255, 215, 0), font=font_title, anchor="mm")
    draw.text((W/2, 245), "Can you spot the winking cub before time runs out?", fill=(255, 255, 255), font=font_sub, anchor="mm")

    # 2. Draw 4x5 Grid of 20 Cute 3D Teddy Bear Cub Avatars
    # Rows: 5, Cols: 4 = 20 cards
    cols, rows = 4, 5
    grid_top = 370
    card_w, card_h = 190, 210
    pad_x = (W - (cols * card_w)) / (cols + 1) # spacing
    pad_y = 35

    # Pick the target odd one (e.g., Row 3, Col 2 -> 1-based: row index 2, col index 1)
    target_r, target_c = 2, 2 # Center area (Row 3, Column 3)
    target_box = None

    for r in range(rows):
        for c in range(cols):
            x = pad_x + c * (card_w + pad_x)
            y = grid_top + r * (card_h + pad_y)

            # Draw card rounded background
            draw.rounded_rectangle([x, y, x + card_w, y + card_h], radius=24, fill=(53, 59, 102), outline=(80, 88, 145), width=2)

            cx = x + card_w / 2
            cy = y + card_h / 2

            # Is this the odd one?
            is_odd = (r == target_r and c == target_c)
            if is_odd:
                target_box = (int(x), int(y), int(card_w), int(card_h))

            # Draw Cute Bear Face
            # Ears
            draw.ellipse([cx - 70, cy - 70, cx - 30, cy - 30], fill=(210, 140, 70))
            draw.ellipse([cx - 60, cy - 60, cx - 40, cy - 40], fill=(240, 180, 120))
            draw.ellipse([cx + 30, cy - 70, cx + 70, cy - 30], fill=(210, 140, 70))
            draw.ellipse([cx + 40, cy - 60, cx + 60, cy - 40], fill=(240, 180, 120))

            # Head
            draw.ellipse([cx - 65, cy - 50, cx + 65, cy + 55], fill=(210, 140, 70))

            # Snout
            draw.ellipse([cx - 30, cy - 5, cx + 30, cy + 40], fill=(250, 220, 175))
            # Nose
            draw.ellipse([cx - 12, cy + 5, cx + 12, cy + 22], fill=(60, 40, 25))
            # Smile
            draw.arc([cx - 15, cy + 18, cx + 15, cy + 34], start=0, end=180, fill=(60, 40, 25), width=3)

            # Cheeks blush
            draw.ellipse([cx - 50, cy + 8, cx - 30, cy + 24], fill=(255, 150, 150, 120))
            draw.ellipse([cx + 30, cy + 8, cx + 50, cy + 24], fill=(255, 150, 150, 120))

            # EYES
            # Left Eye: Normal for everyone
            draw.ellipse([cx - 38, cy - 25, cx - 18, cy - 5], fill=(40, 25, 15))
            draw.ellipse([cx - 34, cy - 23, cx - 26, cy - 15], fill=(255, 255, 255)) # highlight

            if not is_odd:
                # Normal Right Eye (Both eyes open)
                draw.ellipse([cx + 18, cy - 25, cx + 38, cy - 5], fill=(40, 25, 15))
                draw.ellipse([cx + 22, cy - 23, cx + 30, cy - 15], fill=(255, 255, 255))
            else:
                # ODD ONE: Winking Right Eye! (Cute curved wink arc 😉)
                draw.arc([cx + 14, cy - 20, cx + 42, cy - 5], start=180, end=360, fill=(40, 25, 15), width=5)

    # 3. Bottom instructions & challenge callout
    draw.rounded_rectangle([80, 1660, 1000, 1740], radius=20, fill=(255, 75, 75))
    draw.text((W/2, 1700), "🔥 98% of people miss it! Look closely! 🔥", fill=(255, 255, 255), font=font_sub, anchor="mm")

    img.save(r"C:\antigravity\media\puzzle-reel-cloud-generator\real_puzzle_image.jpg", quality=95)
    print("Target box coordinates:", target_box)
    return target_box

if __name__ == "__main__":
    make_puzzle_base()

