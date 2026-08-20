import os
from PIL import Image, ImageDraw, ImageFont

def generate_app_icon():
    os.makedirs("assets", exist_ok=True)
    sizes = [16, 32, 48, 64, 128, 256]
    images = []
    
    for size in sizes:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw modern rounded rectangle background
        pad = max(1, int(size * 0.06))
        radius = max(2, int(size * 0.22))
        
        # Gradient effect (layered rounded rects)
        # Deep Blue to Vibrant Azure
        top_color = (0, 120, 215, 255)      # Windows 11 Blue
        accent_color = (0, 164, 239, 255)   # Light blue
        
        draw.rounded_rectangle(
            [pad, pad, size - pad, size - pad],
            radius=radius,
            fill=top_color,
            outline=(255, 255, 255, 40),
            width=max(1, int(size * 0.02))
        )
        
        # Draw image mountain/sun graphic or camera lens
        # Sun circle
        sun_r = max(2, int(size * 0.12))
        sun_x = int(size * 0.68)
        sun_y = int(size * 0.32)
        draw.ellipse([sun_x - sun_r, sun_y - sun_r, sun_x + sun_r, sun_y + sun_r], fill=(255, 220, 50, 240))
        
        # Mountain / triangle in white/translucent
        p1 = (int(size * 0.2), int(size * 0.68))
        p2 = (int(size * 0.45), int(size * 0.38))
        p3 = (int(size * 0.7), int(size * 0.68))
        draw.polygon([p1, p2, p3], fill=(255, 255, 255, 200))
        
        p4 = (int(size * 0.45), int(size * 0.68))
        p5 = (int(size * 0.65), int(size * 0.48))
        p6 = (int(size * 0.82), int(size * 0.68))
        draw.polygon([p4, p5, p6], fill=(255, 255, 255, 140))
        
        # Badge at the bottom: "JPG"
        badge_h = max(6, int(size * 0.24))
        badge_y = int(size * 0.64)
        draw.rounded_rectangle(
            [int(size * 0.16), badge_y, int(size * 0.84), badge_y + badge_h],
            radius=max(1, int(badge_h * 0.3)),
            fill=(20, 20, 24, 230),
            outline=(255, 255, 255, 60),
            width=1
        )
        
        # Simple text or bar indication
        if size >= 48:
            try:
                # Basic font fallback
                font = ImageFont.truetype("arial.ttf", int(badge_h * 0.75))
            except Exception:
                font = ImageFont.load_default()
            
            text = "JPG"
            bbox = draw.textbbox((0, 0), text, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            tx = (size - w) // 2
            ty = badge_y + (badge_h - h) // 2 - 1
            draw.text((tx, ty), text, fill=(255, 255, 255, 255), font=font)
        
        images.append(img)
    
    # Save highest res as PNG
    images[-1].save("assets/icon.png", format="PNG")
    # Save multi-res ICO
    images[0].save("assets/icon.ico", format="ICO", sizes=[(s, s) for s in sizes], append_images=images[1:])
    print("Icon generated successfully in assets/icon.ico and assets/icon.png")

if __name__ == "__main__":
    generate_app_icon()
