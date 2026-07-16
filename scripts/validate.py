import yaml
import os

def check_file_yaml(path):
    print(f"Validating YAML: {path}")
    if not os.path.exists(path):
        print(f"Error: File {path} does not exist!")
        return False
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            print(f"Success! Parsed structure: {type(data)}")
            return data
    except Exception as e:
        print(f"YAML Syntax Error in {path}: {e}")
        return None

def test_matching_logic(bikes):
    print("\nRunning matching simulation:")
    # Test case 1: Beginner, height 165cm, inseam 73cm, prefers light, rough road, capital
    height = 165
    inseam = 73
    experience = 'beginner'
    require_abs = False
    prefer_lightweight = True
    road_type = 'rough'
    location = 'capital'
    
    scored = []
    for bike in bikes:
        scores = {'ergonomics': 100, 'safety': 100, 'weight': 100, 'environment': 100}
        
        # 1. Ergonomics
        mult = 1.0
        if bike['seat_width_profile'] == 'medium-narrow': mult = 1.01
        elif bike['seat_width_profile'] == 'medium': mult = 1.02
        elif bike['seat_width_profile'] == 'medium-wide': mult = 1.04
        elif bike['seat_width_profile'] == 'wide': mult = 1.06
        
        eff_height = (bike['seat_height_mm'] * mult) / 10.0
        reach_delta = inseam - eff_height
        
        if reach_delta >= 2.0:
            scores['ergonomics'] = 100
        elif reach_delta >= -3.0:
            scores['ergonomics'] = 85
        elif reach_delta >= -7.0:
            scores['ergonomics'] = 55
            if experience == 'beginner':
                scores['ergonomics'] -= 15
        else:
            scores['ergonomics'] = 20
            
        # 2. Weight
        if prefer_lightweight or experience == 'beginner':
            if bike['wet_weight_kg'] <= 125:
                scores['weight'] = 100
            elif bike['wet_weight_kg'] <= 155:
                scores['weight'] = 80
            elif bike['wet_weight_kg'] <= 180:
                scores['weight'] = 50
            else:
                scores['weight'] = 20
                
        # 3. Experience & Safety
        if experience == 'beginner':
            if bike['power_hp'] > 35:
                scores['safety'] -= 50
            elif bike['power_hp'] > 22:
                scores['safety'] -= 15
                
        # 4. Environment
        if road_type == 'rough':
            if bike['category'] in ['Trail', 'Adventure']:
                scores['environment'] = 100
            elif bike['category'] in ['Scooter', 'CUB']:
                scores['environment'] = 50
            else:
                scores['environment'] = 70
                
        if location == 'capital':
            if bike['theft_risk_index'] == 'critical':
                scores['environment'] -= 20
            elif bike['theft_risk_index'] == 'high':
                scores['environment'] -= 10
                
        composite = round(
            scores['ergonomics'] * 0.35 +
            scores['safety'] * 0.25 +
            scores['weight'] * 0.20 +
            scores['environment'] * 0.20
        )
        label = f"{bike['brand']} {bike['model']} ({bike.get('year', 2026)})"
        scored.append((label, composite, reach_delta, bike['wet_weight_kg']))
        
    scored.sort(key=lambda x: x[1], reverse=True)
    for name, score, delta, weight in scored:
        print(f" - {name:30s}: Score: {score}% | Reach Delta: {delta:+.1f}cm | Weight: {weight}kg")

if __name__ == "__main__":
    config_path = "/home/danilo/Projects/whichbike/website/_config.yml"
    mfr_files = [
        "honda.yml", "yamaha.yml", "suzuki.yml", "kawasaki.yml", "bmw.yml",
        "royal_enfield.yml", "bajaj.yml", "triumph.yml", "harley_davidson.yml",
        "ducati.yml", "dafra.yml", "shineray.yml", "mottu.yml", "avelloz.yml",
        "haojue.yml", "ktm.yml", "kymco.yml", "zontes.yml", "voltz.yml", "vespa.yml"
    ]
    
    check_file_yaml(config_path)
    
    bikes = []
    for file in mfr_files:
        path = f"/home/danilo/Projects/whichbike/website/_data/{file}"
        mfr_data = check_file_yaml(path)
        if mfr_data:
            for bike in mfr_data:
                history_list = bike.get("history", [])
                for var in history_list:
                    flat_bike = bike.copy()
                    flat_bike["fipe_price_brl"] = var["fipe_price_brl"]
                    flat_bike["year"] = var["year"]
                    flat_bike["is_used"] = var["is_used"]
                    flat_bike["has_abs"] = var.get("has_abs", bike.get("has_abs", False))
                    flat_bike["has_cbs"] = var.get("has_cbs", bike.get("has_cbs", False))
                    bikes.append(flat_bike)
            
    if bikes:
        test_matching_logic(bikes)
