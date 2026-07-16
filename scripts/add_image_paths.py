import os
import yaml

data_dir = "/home/danilo/Projects/whichbike/website/_data"

def get_image_for_category(category):
    cat = category.lower()
    if cat in ["trail", "adventure"]:
        return "/assets/images/generated/lander_250.png"
    elif cat == "street":
        return "/assets/images/generated/cg_160.png"
    elif cat in ["cub", "scooter"]:
        return "/assets/images/generated/nmax_160.png"
    elif cat == "retro":
        return "/assets/images/generated/eliminator_500.png"
    elif cat == "sport":
        return "/assets/images/generated/hornet_600.png"
    return "/assets/images/generated/cg_160.png"

def migrate_yml_files():
    for file in os.listdir(data_dir):
        if not file.endswith(".yml") or file in ["gear.yml", "navigation.yml"]:
            continue
            
        file_path = os.path.join(data_dir, file)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                bikes = yaml.safe_load(f)
                
            if not bikes or not isinstance(bikes, list):
                continue
                
            updated = False
            for bike in bikes:
                # Add image_path to the model level
                category = bike.get("category", "")
                img_path = get_image_for_category(category)
                
                # If specific popular models, we can map them directly
                model_id = bike.get("id", "")
                if "hornet" in model_id:
                    img_path = "/assets/images/generated/hornet_600.png"
                elif "lander" in model_id:
                    img_path = "/assets/images/generated/lander_250.png"
                elif "eliminator" in model_id:
                    img_path = "/assets/images/generated/eliminator_500.png"
                elif "nmax" in model_id:
                    img_path = "/assets/images/generated/nmax_160.png"
                elif "titan" in model_id:
                    img_path = "/assets/images/generated/cg_160.png"
                    
                bike["image_path"] = img_path
                updated = True
                
            if updated:
                with open(file_path, "w", encoding="utf-8") as f:
                    yaml.safe_dump(bikes, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
                print(f"Migrated image_paths in: {file_path}")
        except Exception as e:
            print(f"Error migrating {file_path}: {e}")

if __name__ == "__main__":
    migrate_yml_files()
