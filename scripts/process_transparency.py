import sys
import os
from PIL import Image

def convert_to_transparent(input_path, output_path):
    print(f"Keying background for: {input_path}")
    if not os.path.exists(input_path):
        print(f"Error: Input path {input_path} does not exist.")
        return False
        
    try:
        img = Image.open(input_path).convert("RGBA")
        datas = img.getdata()
        
        new_data = []
        for item in datas:
            # Check if pixel is very close to white (RGB > 242)
            if item[0] > 242 and item[1] > 242 and item[2] > 242:
                # Make it transparent
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
                
        img.putdata(new_data)
        
        # Crop empty bounding box to trim margins and align perfectly
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
            
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path, "PNG")
        print(f"Success: Saved transparent cropped image to {output_path}")
        return True
    except Exception as e:
        print(f"Failed to process image transparency: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 process_transparency.py <input_img> <output_png>")
        sys.exit(1)
    convert_to_transparent(sys.argv[1], sys.argv[2])
