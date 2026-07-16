import os
import yaml

data_dir = "/home/danilo/Projects/whichbike/website/_data"

def get_enrichment_data(bike_id, category):
    cat = category.lower()
    b_id = bike_id.lower()
    
    # Defaults
    image_path = "/assets/images/generated/cg_160.png"
    wheel_size = 'D: 17" / T: 17"'
    ground_clearance = 145
    
    # 1. Sport/Naked
    if cat == "sport":
        image_path = "/assets/images/generated/hornet_600.png"
        wheel_size = 'D: 17" / T: 17"'
        ground_clearance = 135 if "bandit" in b_id or "gsx" in b_id else 140
        if "mt03" in b_id or "mt-03" in b_id:
            image_path = "/assets/images/generated/mt03.png"
        elif "fazer" in b_id or "fz2" in b_id:
            image_path = "/assets/images/generated/fazer_250.png"
        elif "duke" in b_id:
            image_path = "/assets/images/generated/ktm_390_duke.png"
            
    # 2. Trail/Adventure
    elif cat in ["trail", "adventure"]:
        image_path = "/assets/images/generated/lander_250.png"
        if "v-strom" in b_id or "g-310-gs" in b_id or "tiger" in b_id or "f-800-gs" in b_id or "f-750-gs" in b_id or "r-12" in b_id:
            wheel_size = 'D: 19" / T: 17"'
            ground_clearance = 180
            if "v-strom" in b_id:
                image_path = "/assets/images/generated/vstrom_650.png"
            elif "tiger" in b_id:
                image_path = "/assets/images/generated/tiger_900.png"
            elif "f-750-gs" in b_id:
                image_path = "/assets/images/generated/f_750_gs.png"
            elif "r-12" in b_id:
                image_path = "/assets/images/generated/r_1250_gs.png"
            else:
                image_path = "/assets/images/generated/f_800_gs.png"
        else:
            wheel_size = 'D: 21" / T: 18"'
            ground_clearance = 220
        if "lander" in b_id:
            image_path = "/assets/images/generated/lander_250.png"
        elif "sahara" in b_id or "xre" in b_id:
            image_path = "/assets/images/generated/sahara_300.png"
        elif "falcon" in b_id or "nx4" in b_id:
            image_path = "/assets/images/generated/falcon_nx4.png"
            
    # 3. Scooter/CUB
    elif cat in ["cub", "scooter"]:
        image_path = "/assets/images/generated/nmax_160.png"
        if "nmax" in b_id:
            wheel_size = 'D: 13" / T: 13"'
            image_path = "/assets/images/generated/nmax_160.png"
        elif "biz" in b_id:
            wheel_size = 'D: 17" / T: 14"'
            image_path = "/assets/images/generated/honda_biz.png"
        elif "pop" in b_id:
            wheel_size = 'D: 17" / T: 17"'
            image_path = "/assets/images/generated/honda_pop.png"
        elif "vespa" in b_id:
            wheel_size = 'D: 12" / T: 12"'
        elif "xmax" in b_id:
            wheel_size = 'D: 15" / T: 14"'
            image_path = "/assets/images/generated/xmax_250.png"
        else:
            wheel_size = 'D: 16" / T: 14"'
        ground_clearance = 120
        
    # 4. Retro/Cruiser/Custom
    elif cat == "retro":
        image_path = "/assets/images/generated/eliminator_500.png"
        if "eliminator" in b_id:
            wheel_size = 'D: 18" / T: 16"'
            image_path = "/assets/images/generated/eliminator_500.png"
        elif "vulcan" in b_id:
            wheel_size = 'D: 18" / T: 16"'
        elif "iron" in b_id:
            wheel_size = 'D: 19" / T: 16"'
            image_path = "/assets/images/generated/iron_883.png"
        elif "fat-boy" in b_id:
            wheel_size = 'D: 18" / T: 18"'
            image_path = "/assets/images/generated/iron_883.png"
        elif "hunter" in b_id:
            wheel_size = 'D: 17" / T: 17"'
            image_path = "/assets/images/generated/hunter_350.png"
        elif "scrambler" in b_id:
            wheel_size = 'D: 18" / T: 17"'
            image_path = "/assets/images/generated/ducati_scrambler.png"
        else:
            # Classic, Meteor, Chopper
            wheel_size = 'D: 19" / T: 18"'
        ground_clearance = 135
        
    # 5. Scooter overrides
    if "vespa" in b_id:
        image_path = "/assets/images/generated/vespa_primavera.png"

    # 6. Street/Commuter
    if cat == "street":
        image_path = "/assets/images/generated/cg_160.png"
        wheel_size = 'D: 17" / T: 17"'
        ground_clearance = 150
        if "titan" in b_id:
            image_path = "/assets/images/generated/cg_160.png"
        if "mottu" in b_id or "tv-sport" in b_id:
            image_path = "/assets/images/generated/mottu_sport.png"
        if "xy-50" in b_id or "xy50" in b_id:
            image_path = "/assets/images/generated/shineray_xy_50.png"
            
    return image_path, wheel_size, ground_clearance

def generate_yoy_history(launch_year, current_price, is_used):
    if not is_used or launch_year >= 2026:
        return [{"calendar_year": 2026, "price": current_price}]
        
    prices = {}
    price = 100.0  # arbitrary starting point
    prices[launch_year] = price
    
    for y in range(launch_year + 1, 2027):
        if y < 2020:
            price *= 0.94  # 6% depreciation per year
        elif y <= 2024:
            price *= 1.12  # 12% covid-era surge
        else:
            price *= 1.02  # 2% post-covid stabilization
        prices[y] = price
        
    # Scale so that 2026 matches current_price
    scale = current_price / prices[2026]
    
    yoy_list = []
    for y in range(launch_year, 2027):
        yoy_list.append({
            "calendar_year": y,
            "price": int(round(prices[y] * scale))
        })
    return yoy_list

def enrich_database():
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
                b_id = bike.get("id", "")
                category = bike.get("category", "")
                
                img_path, wheel_sz, clearance = get_enrichment_data(b_id, category)
                
                bike["image_path"] = img_path
                bike["wheel_size"] = wheel_sz
                bike["ground_clearance_mm"] = clearance
                
                if "history" in bike:
                    for var in bike["history"]:
                        yoy = var.get("price_history", [])
                        if not yoy or len(yoy) <= 1:
                            var["price_history"] = generate_yoy_history(
                                var["year"],
                                var["fipe_price_brl"],
                                var["is_used"]
                            )
                updated = True
                
            if updated:
                with open(file_path, "w", encoding="utf-8") as f:
                    yaml.safe_dump(bikes, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
                print(f"Enriched: {file_path}")
        except Exception as e:
            print(f"Error enriching {file_path}: {e}")

if __name__ == "__main__":
    enrich_database()
