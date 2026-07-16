"""
fipe_car_bulk_import.py  — uses veiculos.fipe.org.br official API for CARS (tipo_veiculo = 1)

Strategy to avoid 429s:
  - Fetches ONLY the latest/current price per model (not full year history).
  - On 429: backs off exponentially and ABORTS the current brand after
    MAX_CONSECUTIVE_429 failures, saving a checkpoint file so the next
    run resumes from where it left off.
  - Checkpoint file: scripts/fipe_import_checkpoint.json
"""

import os, re, sys, time, json, yaml, requests

FIPE_BASE  = "https://veiculos.fipe.org.br/api/veiculos"
DATA_DIR   = os.path.join(os.path.dirname(__file__), "..", "website", "_data")
CKPT_FILE  = os.path.join(os.path.dirname(__file__), "fipe_import_checkpoint.json")
MIN_YEAR   = 1995
TIPO_CARRO = 1
MAX_429    = 5

HEADERS = {
    "Content-Type": "application/json;charset=UTF-8",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://veiculos.fipe.org.br/",
    "Origin": "https://veiculos.fipe.org.br",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
}

BRAND_MAP = [
    ("chevrolet.yml",       "Chevrolet",       23),
    ("fiat.yml",            "Fiat",            21),
    ("volkswagen.yml",      "Volkswagen",      59),
    ("toyota.yml",          "Toyota",          56),
    ("ford.yml",            "Ford",            22),
    ("hyundai.yml",         "Hyundai",         26),
    ("honda.yml",           "Honda",           25),
    ("jeep.yml",            "Jeep",            29),
    ("renault.yml",         "Renault",         48),
    ("nissan.yml",          "Nissan",          43),
    ("peugeot.yml",         "Peugeot",         44),
    ("citroen.yml",         "Citroën",         13),
    ("mitsubishi.yml",      "Mitsubishi",      39),
    ("chery.yml",           "Caoa Chery",      161),
    ("byd.yml",             "BYD",             279),
    ("gwm.yml",             "GWM",             288),
    ("bmw.yml",             "BMW",             7),
    ("mercedes_benz.yml",   "Mercedes-Benz",   37),
    ("audi.yml",            "Audi",            6),
    ("volvo.yml",           "Volvo",           58),
]

CATEGORY_KEYWORDS = [
    (["suv","tracker","compass","renegade","creta","t-cross","tcross","nivus",
       "kicks","duster","captur","tiggo","pulse","fastback","hr-v","hrv","wr-v",
       "wrv","corolla cross","cross","sw4","trailblazer","commander","territory",
       "equinox","taos","tiguan"], "SUV"),
    (["picape","strada","toro","hilux","s10","ranger","amarok","l200","frontier",
       "montana","saveiro","oroch","ram ","f150","f-150","maverick"], "Picape"),
    (["sedan","corolla","civic","virtus","cronos","onix plus","versa","hb20s",
       "sentra","jetta","cruze","city sedan","audi a3","audi a4","bmw 3"], "Sedan"),
    (["eletrico","elétrico","hybrid","hibrido","híbrido","byd dolphin","seal",
       "ora 03","dolphin","e-js1","ev ","plug-in"], "Eletrico"),
    (["sport","esportivo","coupe","cupê","m3","m4","m5","porsche","mustang",
       "camaro","tts","rs3","rs4","rs5","rs6","ferrari","amg"], "Esportivo"),
    (["hatch","onix","hb20","polo","argo","yaris","mobi","kwid","city hatchback",
       "sandero","208","c3","mini cooper","golf"], "Hatchback"),
]

DEFAULT_SPECS = {
    "Hatchback": {"engine_cc": 1000, "power_hp": 80,  "wet_weight_kg": 1050, "seat_height_mm": 300, "seat_width_profile": "Hatchback", "maintenance_index": 2, "parts_network_index": 8, "theft_risk_index": "high",   "wheel_size": "R15", "ground_clearance_mm": 140},
    "Sedan":     {"engine_cc": 1600, "power_hp": 120, "wet_weight_kg": 1200, "seat_height_mm": 500, "seat_width_profile": "Sedan",     "maintenance_index": 2, "parts_network_index": 8, "theft_risk_index": "medium", "wheel_size": "R16", "ground_clearance_mm": 150},
    "SUV":       {"engine_cc": 1600, "power_hp": 130, "wet_weight_kg": 1400, "seat_height_mm": 450, "seat_width_profile": "SUV",       "maintenance_index": 3, "parts_network_index": 7, "theft_risk_index": "medium", "wheel_size": "R17", "ground_clearance_mm": 180},
    "Picape":    {"engine_cc": 2000, "power_hp": 170, "wet_weight_kg": 1800, "seat_height_mm": 900, "seat_width_profile": "Picape",    "maintenance_index": 3, "parts_network_index": 7, "theft_risk_index": "high",   "wheel_size": "R16", "ground_clearance_mm": 210},
    "Esportivo": {"engine_cc": 2000, "power_hp": 250, "wet_weight_kg": 1450, "seat_height_mm": 350, "seat_width_profile": "Esportivo", "maintenance_index": 4, "parts_network_index": 5, "theft_risk_index": "medium", "wheel_size": "R18", "ground_clearance_mm": 120},
    "Eletrico":  {"engine_cc": 0,    "power_hp": 150, "wet_weight_kg": 1600, "seat_height_mm": 350, "seat_width_profile": "Eletrico",  "maintenance_index": 2, "parts_network_index": 4, "theft_risk_index": "low",    "wheel_size": "R16", "ground_clearance_mm": 140},
}


def load_checkpoint():
    if os.path.exists(CKPT_FILE):
        with open(CKPT_FILE) as f:
            return json.load(f)
    return {"brands_done": [], "in_progress": None}


def save_checkpoint(ckpt):
    with open(CKPT_FILE, "w") as f:
        json.dump(ckpt, f, indent=2)


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
        "codigoTipoVeiculo": TIPO_CARRO,
        "codigoMarca": brand_id,
    })
    return data.get("Modelos", []) if data else []


def get_years(brand_id, model_id, ref):
    data = fipe_post("ConsultarAnoModelo", {
        "codigoTabelaReferencia": ref,
        "codigoTipoVeiculo": TIPO_CARRO,
        "codigoMarca": brand_id,
        "codigoModelo": model_id,
    })
    return data if isinstance(data, list) else []


def get_price_for_year(brand_id, model_id, year_int, year_code, ref):
    parts = year_code.split("-")
    fuel_code = int(parts[1]) if len(parts) > 1 else 1

    data = fipe_post("ConsultarValorComTodosParametros", {
        "codigoTabelaReferencia": ref,
        "codigoTipoVeiculo": TIPO_CARRO,
        "codigoMarca": brand_id,
        "codigoModelo": model_id,
        "ano": year_code,
        "codigoTipoCombustivel": fuel_code,
        "anoModelo": year_int,
        "tipoConsulta": "tradicional",
    })
    if data and "Valor" in data:
        cleaned = re.sub(r"[^\d]", "", data["Valor"])
        return int(cleaned) // 100 if cleaned else 0
    return 0


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
    return "Hatchback"


def build_entry(brand_display, label, brand_id, model_id, years_list, ref):
    category = guess_category(label)
    defaults = DEFAULT_SPECS.get(category, DEFAULT_SPECS["Hatchback"])

    zero_km = next((y for y in years_list if y["Value"].startswith("32000")), None)
    best_year_entry = None
    is_new = False

    if zero_km:
        best_year_entry = zero_km
        is_new = True
    else:
        candidates = []
        for y in years_list:
            val = y["Value"].split("-")[0]
            if val.isdigit() and int(val) >= MIN_YEAR and val != "32000":
                candidates.append((int(val), y))
        if not candidates:
            return None
        candidates.sort(reverse=True)
        best_year_entry = candidates[0][1]

    year_int = 2026 if is_new else int(best_year_entry["Value"].split("-")[0])
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
            "has_abs": True,
            "has_cbs": False,
            "price_history": [{"calendar_year": year_int, "price": price}],
        }],
        "image_path": None,
        "wheel_size": defaults["wheel_size"],
        "ground_clearance_mm": defaults["ground_clearance_mm"],
    }


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
        return True

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
            ckpt["in_progress"] = {"brand": yaml_file, "model_idx": idx + 1}
            save_checkpoint(ckpt)
            continue

        years_list = get_years(brand_id, model_id, ref)

        numeric = []
        for y in years_list:
            val = y["Value"].split("-")[0]
            if val.isdigit() and int(val) >= MIN_YEAR and val != "32000":
                numeric.append(int(val))
        has_zk = any(y["Value"].startswith("32000") for y in years_list)
        if not numeric and not has_zk:
            skipped += 1
            continue

        yr_range = f"{min(numeric)}-{max(numeric)}" if numeric else "ZeroKm only"
        print(f"  [{idx+1}/{len(fipe_models)}] {label}  [{yr_range}]")

        ckpt["in_progress"] = {"brand": yaml_file, "model_idx": idx}
        save_checkpoint(ckpt)

        try:
            entry = build_entry(brand_display, label, brand_id, model_id, years_list, ref)
            if entry:
                new_entries.append(entry)
                known.add(slug)
            consecutive_429 = 0
        except RateLimitAbort:
            print(f"\n  ⚠️  Rate limit abort at model index {idx} ({label})")
            print(f"  Checkpoint saved — resume by running the script again.")
            aborted = True
            break

    if new_entries:
        all_cars = existing + new_entries
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(all_cars, f, allow_unicode=True,
                           default_flow_style=False, sort_keys=False)
        print(f"  ✅ Saved {len(new_entries)} new entries → {len(all_cars)} total")

    if not aborted:
        ckpt["brands_done"].append(yaml_file)
        ckpt["in_progress"] = None
        save_checkpoint(ckpt)
        print(f"  ✅ Brand complete.")

    return not aborted


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--reset" in args:
        if os.path.exists(CKPT_FILE):
            os.remove(CKPT_FILE)
            print("Checkpoint cleared.")
        sys.exit(0)

    print("WhichCar — FIPE Bulk Importer (CARS)")
    print("=" * 62)

    ref = get_ref_table()
    print(f"Reference table: {ref}")

    ckpt = load_checkpoint()
    if ckpt["brands_done"]:
        print(f"Already done: {', '.join(ckpt['brands_done'])}")
    if ckpt["in_progress"]:
        ip = ckpt["in_progress"]
        print(f"Resuming: {ip['brand']} at model index {ip['model_idx']}")

    target = args[0].lower() if args else None

    for yaml_file, brand_display, brand_id in BRAND_MAP:
        if target:
            stem = yaml_file.replace(".yml", "").lower()
            if target not in stem and target not in brand_display.lower():
                continue

        if not target and yaml_file in ckpt["brands_done"]:
            print(f"\n[skip] {brand_display} — already completed.")
            continue

        start_idx = 0
        if ckpt["in_progress"] and ckpt["in_progress"]["brand"] == yaml_file:
            start_idx = ckpt["in_progress"]["model_idx"]

        completed = import_brand(yaml_file, brand_display, brand_id,
                                 ref, ckpt, start_model_idx=start_idx)
        if not completed:
            print("\n🛑 Stopped due to rate limiting. Run the script again to resume.")
            break

    print("\nDone.")
