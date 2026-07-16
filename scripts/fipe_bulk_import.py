"""
fipe_bulk_import.py  — uses veiculos.fipe.org.br official API

Strategy to avoid 429s:
  - Fetches ONLY the latest/current price per model (not full year history).
  - On 429: backs off exponentially and ABORTS the current brand after
    MAX_CONSECUTIVE_429 failures, saving a checkpoint file so the next
    run resumes from where it left off.
  - Checkpoint file: scripts/fipe_import_checkpoint.json
    Stores: {"brand_done": ["honda", ...], "in_progress": {"brand": ..., "model_idx": ...}}

Usage:
  python3 scripts/fipe_bulk_import.py             # all brands (resumes from checkpoint)
  python3 scripts/fipe_bulk_import.py honda       # single brand
  python3 scripts/fipe_bulk_import.py --reset     # clear checkpoint and start fresh
"""

import os, re, sys, time, json, yaml, requests

FIPE_BASE  = "https://veiculos.fipe.org.br/api/veiculos"
DATA_DIR   = os.path.join(os.path.dirname(__file__), "..", "website", "_data")
CKPT_FILE  = os.path.join(os.path.dirname(__file__), "fipe_import_checkpoint.json")
MIN_YEAR   = 1995
TIPO_MOTO  = 2
MAX_429    = 5    # abort brand after this many consecutive 429s

HEADERS = {
    "Content-Type": "application/json;charset=UTF-8",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://veiculos.fipe.org.br/",
    "Origin": "https://veiculos.fipe.org.br",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
}

BRAND_MAP = [
    ("honda.yml",           "Honda",           80),
    ("yamaha.yml",          "Yamaha",          101),
    ("kawasaki.yml",        "Kawasaki",        85),
    ("suzuki.yml",          "Suzuki",          99),
    ("bmw.yml",             "BMW",             67),
    ("royal_enfield.yml",   "Royal Enfield",   192),
    ("bajaj.yml",           "Bajaj",           64),
    ("triumph.yml",         "Triumph",         100),
    ("harley_davidson.yml", "Harley-Davidson", 77),
    ("ducati.yml",          "Ducati",          74),
    ("ktm.yml",             "KTM",             87),
    ("vespa.yml",           "Vespa",           256),
    ("dafra.yml",           "Dafra",           145),
    ("haojue.yml",          "Haojue",          203),
    ("kymco.yml",           "Kymco",           204),
    ("zontes.yml",          "Zontes",          242),
    ("avelloz.yml",         "Avelloz",         216),
]

CATEGORY_KEYWORDS = [
    (["trail","xre","nxr","bros","xtz","crosser","tenere","teneré","versys",
       "crf","transalp","lander","himalayan","supermoto","africa twin"], "Trail"),
    (["nmax","pcx","lead","elite","vision","burgman","aerox",
       "downtown","tricity","xmax","tmax","adv ","forza"], "Scooter"),
    (["pop ","biz ","fan ","titan","cub"], "CUB"),
    (["chopper","intruder","shadow","vulcan","drag","rebel","iron ","fat ",
       "springer","heritage","road king","softail","street glide","electra",
       "low rider","roadster","custom","virago","v-star","bolt","eliminator",
       "meteor","classic","bullet","thunderbird","bobber","scrambler",
       "thruxton","hunter","bonneville","street twin"], "Retro"),
    (["gs ","r 12","f 800","f800","f 750","v-strom","vstrom","tiger","multistrada"], "Adventure"),
    (["cbr","ninja","r3","r6","r1 ","yzf","gsxr","gsx-r","hornet",
       "fazer","z300","z400","mt-","duke","rc3","rc 3"], "Sport"),
    (["electric","elétrica","eletrica","volt"], "Electric"),
]

DEFAULT_SPECS = {
    "Trail":     {"engine_cc":160,"power_hp":14,"wet_weight_kg":130,"seat_height_mm":840,"seat_width_profile":"narrow","maintenance_index":2,"parts_network_index":7,"theft_risk_index":"medium","wheel_size":'D: 21" / T: 18"',"ground_clearance_mm":210},
    "Scooter":   {"engine_cc":155,"power_hp":15,"wet_weight_kg":128,"seat_height_mm":780,"seat_width_profile":"wide",  "maintenance_index":2,"parts_network_index":7,"theft_risk_index":"medium","wheel_size":'D: 13" / T: 13"',"ground_clearance_mm":125},
    "CUB":       {"engine_cc":110,"power_hp":8, "wet_weight_kg":95, "seat_height_mm":760,"seat_width_profile":"narrow","maintenance_index":1,"parts_network_index":10,"theft_risk_index":"high",  "wheel_size":'D: 17" / T: 14"',"ground_clearance_mm":120},
    "Street":    {"engine_cc":162,"power_hp":15,"wet_weight_kg":125,"seat_height_mm":790,"seat_width_profile":"narrow","maintenance_index":1,"parts_network_index":8, "theft_risk_index":"high",  "wheel_size":'D: 17" / T: 17"',"ground_clearance_mm":150},
    "Retro":     {"engine_cc":500,"power_hp":45,"wet_weight_kg":195,"seat_height_mm":780,"seat_width_profile":"narrow","maintenance_index":3,"parts_network_index":5, "theft_risk_index":"medium","wheel_size":'D: 18" / T: 16"',"ground_clearance_mm":135},
    "Sport":     {"engine_cc":300,"power_hp":38,"wet_weight_kg":165,"seat_height_mm":810,"seat_width_profile":"narrow","maintenance_index":3,"parts_network_index":6, "theft_risk_index":"medium","wheel_size":'D: 17" / T: 17"',"ground_clearance_mm":140},
    "Adventure": {"engine_cc":650,"power_hp":70,"wet_weight_kg":210,"seat_height_mm":850,"seat_width_profile":"wide",  "maintenance_index":3,"parts_network_index":5, "theft_risk_index":"low",   "wheel_size":'D: 19" / T: 17"',"ground_clearance_mm":220},
    "Electric":  {"engine_cc":0,  "power_hp":8, "wet_weight_kg":110,"seat_height_mm":760,"seat_width_profile":"narrow","maintenance_index":2,"parts_network_index":4, "theft_risk_index":"low",   "wheel_size":'D: 14" / T: 14"',"ground_clearance_mm":150},
}


# ── checkpoint ────────────────────────────────────────────────────────────────

def load_checkpoint():
    if os.path.exists(CKPT_FILE):
        with open(CKPT_FILE) as f:
            return json.load(f)
    return {"brands_done": [], "in_progress": None}


def save_checkpoint(ckpt):
    with open(CKPT_FILE, "w") as f:
        json.dump(ckpt, f, indent=2)


# ── API ───────────────────────────────────────────────────────────────────────

consecutive_429 = 0

def fipe_post(endpoint, payload):
    global consecutive_429
    for attempt in range(4):
        try:
            time.sleep(0.8 + attempt * 1.5)
            r = requests.post(f"{FIPE_BASE}/{endpoint}", headers=HEADERS,
                              json=payload, timeout=15)
            if r.status_code == 200:
                consecutive_429 = 0
                return r.json()
            elif r.status_code == 429:
                consecutive_429 += 1
                wait = 5 * (attempt + 1)
                print(f"      [429] #{consecutive_429} — waiting {wait}s...")
                if consecutive_429 >= MAX_429:
                    raise RateLimitAbort(f"Hit {MAX_429} consecutive 429s")
                time.sleep(wait)
            else:
                time.sleep(2)
        except RateLimitAbort:
            raise
        except Exception as e:
            print(f"      [ERR] {e}")
            time.sleep(3)
    return None


class RateLimitAbort(Exception):
    pass


def get_ref_table():
    data = fipe_post("ConsultarTabelaDeReferencia", {})
    return data[0]["Codigo"] if data else 335


def get_models(brand_id, ref):
    data = fipe_post("ConsultarModelos", {
        "codigoTabelaReferencia": ref,
        "codigoTipoVeiculo": TIPO_MOTO,
        "codigoMarca": brand_id,
    })
    return data.get("Modelos", []) if data else []


def get_years(brand_id, model_id, ref):
    data = fipe_post("ConsultarAnoModelo", {
        "codigoTabelaReferencia": ref,
        "codigoTipoVeiculo": TIPO_MOTO,
        "codigoMarca": brand_id,
        "codigoModelo": model_id,
    })
    return data if isinstance(data, list) else []


def get_price_for_year(brand_id, model_id, year_int, year_code, ref):
    data = fipe_post("ConsultarValorComTodosParametros", {
        "codigoTabelaReferencia": ref,
        "codigoTipoVeiculo": TIPO_MOTO,
        "codigoMarca": brand_id,
        "codigoModelo": model_id,
        "ano": year_code,
        "codigoTipoCombustivel": 1,
        "anoModelo": year_int,
        "tipoConsulta": "tradicional",
    })
    if data and "Valor" in data:
        cleaned = re.sub(r"[^\d]", "", data["Valor"])
        return int(cleaned) // 100 if cleaned else 0
    return 0


# ── helpers ───────────────────────────────────────────────────────────────────

def slugify(text):
    text = text.lower()
    for src, dst in [("àáâãä","a"),("èéêë","e"),("ìíîï","i"),("òóôõö","o"),("ùúûü","u")]:
        for ch in src: text = text.replace(ch, dst)
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def guess_category(name):
    n = name.lower()
    for keywords, cat in CATEGORY_KEYWORDS:
        for kw in keywords:
            if kw in n:
                return cat
    return "Street"


def build_entry(brand_display, label, brand_id, model_id, years_list, ref):
    """
    Fetches ONLY the best single price (Zero Km preferred, else latest year).
    Returns a minimal entry with a single-point price_history.
    """
    category = guess_category(label)
    defaults = DEFAULT_SPECS.get(category, DEFAULT_SPECS["Street"])

    # Prefer Zero Km code
    zero_km = next((y for y in years_list if y["Label"] == "32000"), None)
    best_year_entry = None
    is_new = False

    if zero_km:
        best_year_entry = zero_km
        is_new = True
    else:
        # Pick most recent valid year
        candidates = [(int(y["Label"]), y) for y in years_list
                      if y["Label"].isdigit() and int(y["Label"]) >= MIN_YEAR]
        if not candidates:
            return None
        candidates.sort(reverse=True)
        best_year_entry = candidates[0][1]

    year_int = 2026 if is_new else int(best_year_entry["Label"])
    price = get_price_for_year(brand_id, model_id, year_int,
                               best_year_entry["Value"], ref)
    if price == 0:
        return None

    return {
        "id": slugify(f"{brand_display} {label}"),
        "brand": brand_display,
        "model": label,
        "category": category,
        "engine_cc": defaults["engine_cc"],
        "power_hp": defaults["power_hp"],
        "wet_weight_kg": defaults["wet_weight_kg"],
        "seat_height_mm": defaults["seat_height_mm"],
        "seat_width_profile": defaults["seat_width_profile"],
        "maintenance_index": defaults["maintenance_index"],
        "parts_network_index": defaults["parts_network_index"],
        "theft_risk_index": defaults["theft_risk_index"],
        "history": [{
            "year": year_int,
            "is_used": not is_new,
            "fipe_price_brl": price,
            "has_abs": False,
            "has_cbs": False,
            "price_history": [{"calendar_year": year_int, "price": price}],
        }],
        "image_path": None,
        "wheel_size": defaults["wheel_size"],
        "ground_clearance_mm": defaults["ground_clearance_mm"],
    }


# ── brand importer ────────────────────────────────────────────────────────────

def import_brand(yaml_file, brand_display, brand_id, ref, ckpt, start_model_idx=0):
    global consecutive_429

    yaml_path = os.path.join(DATA_DIR, yaml_file)
    print(f"\n{'='*62}")
    print(f"  {brand_display}  (FIPE ID: {brand_id})  →  {yaml_file}")
    if start_model_idx > 0:
        print(f"  Resuming from model index {start_model_idx}")
    print(f"{'='*62}")

    existing = []
    if os.path.exists(yaml_path):
        with open(yaml_path, "r", encoding="utf-8") as f:
            existing = yaml.safe_load(f) or []

    known = {slugify(b["model"]) for b in existing}
    print(f"  Existing: {len(existing)} models")

    fipe_models = get_models(brand_id, ref)
    if not fipe_models:
        print("  [WARN] Could not fetch models list.")
        return True  # treat as done

    print(f"  FIPE total: {len(fipe_models)} models")

    new_entries = []
    skipped = 0
    aborted = False

    for idx, fm in enumerate(fipe_models):
        if idx < start_model_idx:
            skipped += 1
            continue

        label = fm["Label"]
        model_id = fm["Value"]
        slug = slugify(label)

        if slug in known:
            skipped += 1
            # Update checkpoint progress
            ckpt["in_progress"] = {"brand": yaml_file, "model_idx": idx + 1}
            save_checkpoint(ckpt)
            continue

        years_list = get_years(brand_id, model_id, ref)

        # Filter: only import models with years >= 1995 or Zero Km
        numeric = [int(y["Label"]) for y in years_list
                   if y["Label"].isdigit() and int(y["Label"]) >= MIN_YEAR]
        has_zk = any(y["Label"] == "32000" for y in years_list)
        if not numeric and not has_zk:
            skipped += 1
            continue

        yr_range = f"{min(numeric)}-{max(numeric)}" if numeric else "ZeroKm only"
        print(f"  [{idx+1}/{len(fipe_models)}] {label}  [{yr_range}]")

        # Update checkpoint BEFORE the price fetch (most likely to 429)
        ckpt["in_progress"] = {"brand": yaml_file, "model_idx": idx}
        save_checkpoint(ckpt)

        try:
            entry = build_entry(brand_display, label, brand_id, model_id, years_list, ref)
            if entry:
                new_entries.append(entry)
                known.add(slug)
            consecutive_429 = 0  # reset on success
        except RateLimitAbort:
            print(f"\n  ⚠️  Rate limit abort at model index {idx} ({label})")
            print(f"  Checkpoint saved — resume with: python3 scripts/fipe_bulk_import.py")
            aborted = True
            break

    # Save whatever we got so far
    if new_entries:
        all_bikes = existing + new_entries
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(all_bikes, f, allow_unicode=True,
                           default_flow_style=False, sort_keys=False)
        print(f"  ✅ Saved {len(new_entries)} new entries → {len(all_bikes)} total")

    if not aborted:
        ckpt["brands_done"].append(yaml_file)
        ckpt["in_progress"] = None
        save_checkpoint(ckpt)
        print(f"  ✅ Brand complete.")

    return not aborted  # True = completed, False = aborted


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]

    if "--reset" in args:
        if os.path.exists(CKPT_FILE):
            os.remove(CKPT_FILE)
            print("Checkpoint cleared.")
        sys.exit(0)

    print("WhichBike — FIPE Bulk Importer (checkpoint-aware)")
    print("=" * 62)

    ref = get_ref_table()
    print(f"Reference table: {ref}")

    ckpt = load_checkpoint()
    if ckpt["brands_done"]:
        print(f"Already done: {', '.join(ckpt['brands_done'])}")
    if ckpt["in_progress"]:
        ip = ckpt["in_progress"]
        print(f"Resuming: {ip['brand']} at model index {ip['model_idx']}")

    # Single-brand mode
    target = args[0].lower() if args else None

    for yaml_file, brand_display, brand_id in BRAND_MAP:
        if target:
            stem = yaml_file.replace(".yml", "").lower()
            if target not in stem and target not in brand_display.lower():
                continue

        # Skip already completed brands (unless explicitly targeted)
        if not target and yaml_file in ckpt["brands_done"]:
            print(f"\n[skip] {brand_display} — already completed.")
            continue

        # Resume offset
        start_idx = 0
        if ckpt["in_progress"] and ckpt["in_progress"]["brand"] == yaml_file:
            start_idx = ckpt["in_progress"]["model_idx"]

        completed = import_brand(yaml_file, brand_display, brand_id,
                                 ref, ckpt, start_model_idx=start_idx)
        if not completed:
            print("\n🛑 Stopped due to rate limiting. Run the script again to resume.")
            break

    print("\nDone.")
