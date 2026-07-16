import os
import re
import sys
import yaml
import requests
import time

FIPE_API_BASE = "https://parallelum.com.br/fipe/api/v1/motos"

def clean_price_string(price_str):
    # Converts "R$ 19.500,00" -> 19500
    cleaned = re.sub(r"[^\d]", "", price_str)
    if cleaned:
        return int(cleaned) // 100
    return 0

def polite_get(url):
    time.sleep(0.4)  # 400ms politeness gap between calls
    for attempt in range(1, 5):
        try:
            r = requests.get(url, timeout=12)
            if r.status_code == 200:
                return r
            elif r.status_code == 429:
                wait_time = attempt * 3
                print(f"      [Warn] Rate limited (429). Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                time.sleep(1)
        except Exception as e:
            time.sleep(2)
    return None

def fetch_brands():
    r = polite_get(f"{FIPE_API_BASE}/marcas")
    if r:
        return r.json()
    return []

def fetch_models(brand_id):
    r = polite_get(f"{FIPE_API_BASE}/marcas/{brand_id}/modelos")
    if r:
        return r.json().get("modelos", [])
    return []

def fetch_years(brand_id, model_id):
    r = polite_get(f"{FIPE_API_BASE}/marcas/{brand_id}/modelos/{model_id}/anos")
    if r:
        return r.json()
    return []

def fetch_price(brand_id, model_id, year_code):
    r = polite_get(f"{FIPE_API_BASE}/marcas/{brand_id}/modelos/{model_id}/anos/{year_code}")
    if r:
        return r.json()
    return None

def find_best_model_match(models, target_model_name):
    # Normalize model names for better comparison
    target = target_model_name.lower().replace(" ", "").replace("-", "")
    
    # Try exact matches first
    for m in models:
        name = m["nome"].lower().replace(" ", "").replace("-", "")
        if target in name or name in target:
            return m
            
    # Try partial token matching
    target_tokens = set(target_model_name.lower().split())
    best_match = None
    best_overlap = 0
    
    for m in models:
        m_tokens = set(m["nome"].lower().split())
        overlap = len(target_tokens.intersection(m_tokens))
        if overlap > best_overlap:
            best_overlap = overlap
            best_match = m
            
    if best_overlap >= 1:
        return best_match
        
    return None

def update_manufacturer_prices(yaml_path):
    print(f"\nProcessing database file: {yaml_path}")
    if not os.path.exists(yaml_path):
        print(f"Error: File {yaml_path} does not exist!")
        return

    with open(yaml_path, "r", encoding="utf-8") as f:
        bikes = yaml.safe_load(f)

    if not bikes:
        print("No bikes found in file.")
        return

    # Fetch brands once
    brands = fetch_brands()
    if not brands:
        print("Could not load brands list from FIPE. Aborting.")
        return

    brand_name = bikes[0]["brand"]
    # Match brand
    brand_id = None
    for b in brands:
        if b["nome"].lower() == brand_name.lower():
            brand_id = b["codigo"]
            break
            
    if not brand_id:
        # Fuzzy match brand name
        for b in brands:
            if brand_name.lower() in b["nome"].lower():
                brand_id = b["codigo"]
                break

    if not brand_id:
        print(f"Could not find FIPE brand ID for: {brand_name}")
        return

    print(f"Matched FIPE Brand: {brand_name} (ID: {brand_id})")
    
    # Fetch models for this brand
    models = fetch_models(brand_id)
    if not models:
        print("Could not retrieve models list.")
        return

    updated_any = False
    for bike in bikes:
        model_name = bike["model"]
        print(f" -> Querying price for: {brand_name} {model_name}...")
        
        # Match model
        matched_model = find_best_model_match(models, model_name)
        if not matched_model:
            print(f"    [Warn] No matching FIPE model found for '{model_name}'. Skipping.")
            continue
            
        print(f"    Matched to FIPE Model: '{matched_model['nome']}' (ID: {matched_model['codigo']})")
        
        # Fetch years
        years = fetch_years(brand_id, matched_model["codigo"])
        if not years:
            print("    [Warn] No years retrieved. Skipping.")
            continue
            
        history_list = bike.get("history", [])
        if not history_list:
            continue
            
        for var in history_list:
            target_year = var.get("year", 2026)
            is_used = var.get("is_used", False)
            year_code = None
            
            # 1. Try to find exact year match (e.g. 2012)
            for y in years:
                year_match = re.search(r"\b(19\d{2}|20\d{2})\b", y["nome"])
                if year_match:
                    fipe_yr = int(year_match.group(1))
                    if fipe_yr == target_year:
                        year_code = y["codigo"]
                        break
                        
            # 2. If it's a new bike, try to look for Zero Km code (32000)
            if not is_used:
                for y in years:
                    if "32000" in y["codigo"] or "32000-1" in y["codigo"]:
                        year_code = y["codigo"]
                        break
                        
            # 3. Fallback to closest year
            if not year_code:
                closest_code = years[0]["codigo"]
                min_diff = 9999
                for y in years:
                    if "32000" in y["codigo"]:
                        fipe_yr = 2026
                    else:
                        year_match = re.search(r"\b(19\d{2}|20\d{2})\b", y["nome"])
                        fipe_yr = int(year_match.group(1)) if year_match else 2026
                    diff = abs(fipe_yr - target_year)
                    if diff < min_diff:
                        min_diff = diff
                        closest_code = y["codigo"]
                year_code = closest_code
                
            # Resolve resolved year name for printing
            year_name = next((y["nome"] for y in years if y["codigo"] == year_code), "Desconhecido")
            print(f"    Year {target_year}: matched '{year_name}' (Code: {year_code})")
            
            # Fetch price
            price_data = fetch_price(brand_id, matched_model["codigo"], year_code)
            if price_data:
                price_val = clean_price_string(price_data["Valor"])
                if price_val > 0:
                    print(f"      Current FIPE Price: R$ {price_val:,} (was R$ {var['fipe_price_brl']:,})")
                    old_price = var.get("fipe_price_brl", 0)
                    var["fipe_price_brl"] = price_val
                    updated_any = True
                    
                    # Update & scale YoY price history curve
                    yoy_history = var.get("price_history", [])
                    if yoy_history:
                        old_2026 = yoy_history[-1]["price"] if yoy_history[-1]["price"] > 0 else old_price
                        scale = price_val / old_2026 if old_2026 > 0 else 1.0
                        for h in yoy_history:
                            h["price"] = int(round(h["price"] * scale))
                else:
                    print("      [Warn] Price resolved as 0.")
            else:
                print("      [Warn] Price details fetch failed.")

    if updated_any:
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(bikes, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        print(f"Success: Updated pricing database in {yaml_path}")
    else:
        print("No prices updated.")

if __name__ == "__main__":
    data_dir = "/home/danilo/Projects/whichbike/website/_data"
    mfr_files = [
        "honda.yml", "yamaha.yml", "suzuki.yml", "kawasaki.yml", "bmw.yml",
        "royal_enfield.yml", "bajaj.yml", "triumph.yml", "harley_davidson.yml",
        "ducati.yml", "dafra.yml", "shineray.yml", "mottu.yml", "avelloz.yml",
        "haojue.yml", "ktm.yml", "kymco.yml", "zontes.yml", "voltz.yml", "vespa.yml"
    ]
    
    print("WhichBike FIPE Pricing Database Auto-Updater")
    print("=============================================")
    
    # If a specific manufacturer file is specified as argument, only process that one
    if len(sys.argv) > 1:
        target_arg = sys.argv[1]
        if not target_arg.endswith(".yml"):
            target_arg = f"{target_arg}.yml"
        if target_arg in mfr_files:
            update_manufacturer_prices(os.path.join(data_dir, target_arg))
        else:
            print(f"Invalid manufacturer file specified: {target_arg}")
    else:
        for file in mfr_files:
            update_manufacturer_prices(os.path.join(data_dir, file))
