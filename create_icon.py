#!/usr/bin/env python3
"""
Generate Genesis app icon with futuristic DNA helix theme
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import math
except ImportError:
    print("Installing Pillow...")
    import subprocess
    subprocess.run(["pip3", "install", "pillow"], check=True)
    from PIL import Image, ImageDraw, ImageFont
    import math

def create_genesis_icon(size=512):
    """Create futuristic Genesis icon with DNA helix"""
    # Create image with dark background
    img = Image.new('RGBA', (size, size), (10, 10, 30, 255))
    draw = ImageDraw.Draw(img)

    center_x, center_y = size // 2, size // 2

    # Draw glowing background circle
    for i in range(20, 0, -1):
        alpha = int(255 * (i / 20) * 0.3)
        radius = size // 2.5 + i * 3
        draw.ellipse(
            [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
            fill=(10, 80, 128, alpha)
        )

    # Draw main circle background
    main_radius = size // 2.5
    draw.ellipse(
        [center_x - main_radius, center_y - main_radius,
         center_x + main_radius, center_y + main_radius],
        fill=(15, 25, 50, 255)
    )

    # Draw DNA helix
    helix_height = size * 0.6
    helix_width = size * 0.15
    start_y = center_y - helix_height // 2

    # Number of base pairs
    num_pairs = 8

    for i in range(num_pairs * 4):
        t = i / (num_pairs * 4)
        y = start_y + helix_height * t

        # Calculate helix positions
        angle = t * math.pi * 4
        x1 = center_x - helix_width * math.cos(angle)
        x2 = center_x + helix_width * math.cos(angle)

        # Draw connection lines at base pairs
        if i % 4 == 0:
            # Cyan connection
            draw.line([(x1, y), (x2, y)], fill=(0, 255, 255, 180), width=3)

        # Draw helix strands with gradient
        progress = i / (num_pairs * 4)
        color1 = (
            int(0 + progress * 100),
            int(255 - progress * 100),
            int(255),
            255
        )
        color2 = (
            int(255 - progress * 100),
            int(0 + progress * 200),
            int(255),
            255
        )

        # Left strand
        if i > 0:
            prev_t = (i - 1) / (num_pairs * 4)
            prev_y = start_y + helix_height * prev_t
            prev_angle = prev_t * math.pi * 4
            prev_x1 = center_x - helix_width * math.cos(prev_angle)
            draw.line([(prev_x1, prev_y), (x1, y)], fill=color1, width=5)

        # Right strand
        if i > 0:
            prev_t = (i - 1) / (num_pairs * 4)
            prev_y = start_y + helix_height * prev_t
            prev_angle = prev_t * math.pi * 4
            prev_x2 = center_x + helix_width * math.cos(prev_angle)
            draw.line([(prev_x2, prev_y), (x2, y)], fill=color2, width=5)

    # Draw border with glow
    border_radius = size // 2.5
    for width in range(5, 0, -1):
        alpha = int(255 * (width / 5))
        draw.ellipse(
            [center_x - border_radius, center_y - border_radius,
             center_x + border_radius, center_y + border_radius],
            outline=(0, 200, 255, alpha),
            width=width
        )

    # Add "G" letter in the center
    try:
        # Try to use a nice font
        font_size = size // 4
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()

        # Draw "G" with glow effect
        text = "G"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = center_x - text_width // 2
        text_y = center_y - text_height // 2 - size // 15

        # Glow effect
        for offset in range(8, 0, -1):
            alpha = int(255 * (offset / 8) * 0.5)
            for dx in [-offset, 0, offset]:
                for dy in [-offset, 0, offset]:
                    draw.text((text_x + dx, text_y + dy), text,
                            fill=(0, 255, 255, alpha), font=font)

        # Main text
        draw.text((text_x, text_y), text, fill=(0, 255, 255, 255), font=font)
    except Exception as e:
        print(f"Could not add text: {e}")

    return img

if __name__ == '__main__':
    print("Creating Genesis app icon...")

    # Create 512x512 icon
    icon = create_genesis_icon(512)
    icon.save('icon.png')
    print("✓ Created icon.png (512x512)")

    # Create additional sizes for Android
    sizes = [192, 144, 96, 72, 48]
    for size in sizes:
        icon_resized = icon.resize((size, size), Image.Resampling.LANCZOS)
        icon_resized.save(f'icon_{size}.png')
        print(f"✓ Created icon_{size}.png")

    print("\nAll icons created successfully!")
