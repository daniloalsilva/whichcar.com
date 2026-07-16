import os
import yaml

data_dir = "/home/danilo/Projects/whichcar/website/_data"

def get_enrichment_data(car_id, category):
    cat = category.lower()
    c_id = car_id.lower()
    
    # Defaults
    image_path = "/assets/images/generated/polo.png"
    wheel_size = "R15"
    ground_clearance = 140
    
    # 1. Hatchback
    if cat == "hatchback":
        image_path = "/assets/images/generated/polo.png"
        wheel_size = "R15"
        ground_clearance = 140
        if "onix" in c_id:
            image_path = "/assets/images/generated/onix.png"
            wheel_size = "R15"
            ground_clearance = 142
        elif "hb20" in c_id:
            image_path = "/assets/images/generated/hb20.png"
            wheel_size = "R15"
            ground_clearance = 145
            
    # 2. Sedan
    elif cat == "sedan":
        image_path = "/assets/images/generated/corolla.png"
        wheel_size = "R16"
        ground_clearance = 150
        if "corolla" in c_id:
            image_path = "/assets/images/generated/corolla.png"
            wheel_size = "R16"
            ground_clearance = 148
        elif "civic" in c_id:
            image_path = "/assets/images/generated/civic.png"
            wheel_size = "R16"
            ground_clearance = 145
            
    # 3. SUV
    elif cat == "suv":
        image_path = "/assets/images/generated/compass.png"
        wheel_size = "R17"
        ground_clearance = 180
        if "compass" in c_id:
            image_path = "/assets/images/generated/compass.png"
            wheel_size = "R18"
            ground_clearance = 200
        elif "renegade" in c_id:
            image_path = "/assets/images/generated/renegade.png"
            wheel_size = "R17"
            ground_clearance = 186
            
    # 4. Picape
    elif cat == "picape":
        image_path = "/assets/images/generated/hilux.png"
        wheel_size = "R16"
        ground_clearance = 210
        if "hilux" in c_id:
            image_path = "/assets/images/generated/hilux.png"
            wheel_size = "R18"
            ground_clearance = 225
        elif "strada" in c_id:
            image_path = "/assets/images/generated/strada.png"
            wheel_size = "R15"
            ground_clearance = 171
            
    # 5. Esportivo
    elif cat == "esportivo":
        image_path = "/assets/images/generated/porsche.png"
        wheel_size = "R18"
        ground_clearance = 120
        
    # 6. Eletrico
    elif cat == "eletrico":
        image_path = "/assets/images/generated/byd_dolphin.png"
        wheel_size = "R16"
        ground_clearance = 140
        if "dolphin" in c_id:
            image_path = "/assets/images/generated/byd_dolphin.png"
            wheel_size = "R16"
            ground_clearance = 120
            
    return image_path, wheel_size, ground_clearance

def generate_yoy_history(launch_year, current_price, is_used):
    if not is_used or launch_year >= 2026:
        return [{"calendar_year": 2026, "price": current_price}]
        
    prices = {}
    price = 100.0  # arbitrary starting point
    prices[launch_year] = price
    
    for y in range(launch_year + 1, 2027):
        if y < 2020:
            price *= 0.92  # 8% depreciation per year for cars
        elif y <= 2024:
            price *= 1.15  # 15% covid-era car price surge
        else:
            price *= 0.95  # 5% post-covid stabilization/drop
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
                cars = yaml.safe_load(f)
                
            if not cars or not isinstance(cars, list):
                continue
                
            updated = False
            for car in cars:
                c_id = car.get("id", "")
                category = car.get("category", "")
                
                img_path, wheel_sz, clearance = get_enrichment_data(c_id, category)
                
                car["image_path"] = img_path
                car["wheel_size"] = wheel_sz
                car["ground_clearance_mm"] = clearance
                
                if "history" in car:
                    for var in car["history"]:
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
                    yaml.safe_dump(cars, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
                print(f"Enriched: {file_path}")
        except Exception as e:
            print(f"Error enriching {file_path}: {e}")

if __name__ == "__main__":
    enrich_database()
