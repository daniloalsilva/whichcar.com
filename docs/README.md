# WhichBike 🏍️ | Technical & Operational Documentation

Welcome to the **WhichBike** documentation. This guide details how the repository works, how to run local development, how to manage the motorcycle database, and how the automated deployment pipeline is structured.

---

## 📂 Repository Structure

The project uses a clean modular structure separating backend update tools, documentation, and the static website:

```
/whichbike/
├── .agents/                    # Custom agent custom skills
│   └── skills/
│       └── motorcycle_fipe_updater/
│           └── SKILL.md        # AI update skill description
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions CI/CD deployment
├── docs/
│   └── README.md               # This technical documentation
├── Makefile                    # Task automation entry point
├── scripts/
│   ├── fipe_updater.py         # Crawler fetching prices from Tabela FIPE
│   └── validate.py             # Parses databases and validates calculations
└── website/                    # Jekyll static site root
    ├── _config.yml             # Jekyll configs and page metadata
    ├── Gemfile                 # Ruby gem bundle requirements
    ├── index.html              # Quiz interface & Liquid aggregator
    ├── _data/
    │   ├── honda.yml           # Database files split by manufacturer
    │   ├── yamaha.yml
    │   ├── royal_enfield.yml
    │   ├── bajaj.yml
    │   ├── bmw.yml
    │   └── kawasaki.yml
    ├── _includes/
    │   └── head/
    │       └── custom.html     # Custom script & style links
    ├── _sass/
    │   └── minimal-mistakes/
    │       └── skins/
    │           └── _whichbike.scss # Color palette customization
    └── assets/
        ├── css/
        │   └── custom.scss     # CSS design overrides and quiz animations
        └── js/
            └── matcher.js      # Core matching algorithm engine
```

---

## 💻 Local Development

### Prerequisites
You need **Ruby** (v3.2+) and **Python 3** installed locally.

### Setup and Running
Use the root `Makefile` to run standard operations:
*   **Install dependencies:**
    ```bash
    make install
    ```
*   **Run local Jekyll server:**
    ```bash
    make serve
    ```
    *Open `http://localhost:4000/whichbike.com` in your browser.*
*   **Clean build caches:**
    ```bash
    make clean
    ```

---

## 🗄️ Database Management & Updates

The motorcycle database is split into separate manufacturer files inside `website/_data/` (e.g. `honda.yml`, `yamaha.yml`).

### How to Add a New Motorcycle
1. Create or open the corresponding manufacturer file: `website/_data/{manufacturer}.yml`.
2. Add a new block matching the schema:
   ```yaml
   - id: kawasaki-eliminator
     brand: "Kawasaki"
     model: "Eliminator"
     category: "Retro"
     engine_cc: 451.0
     power_hp: 51.0
     wet_weight_kg: 176
     seat_height_mm: 735
     seat_width_profile: "medium" # Options: narrow, medium-narrow, medium, medium-wide, wide
     has_abs: true
     has_cbs: false
     fipe_price_brl: 40000        # Approximate price (updated by scraper)
     maintenance_index: 6         # Complexity 1 (Biz) to 10 (Premium BMW)
     parts_network_index: 4       # Support coverage 1 (Weak rural) to 10 (Honda)
     theft_risk_index: "medium"   # Options: low, medium, high, critical
   ```
3. If this is a new manufacturer, open `website/index.html` and append the manufacturer name to the Liquid aggregator list:
   ```liquid
   {% assign manufacturers = "honda,yamaha,royal_enfield,bajaj,bmw,kawasaki,new_brand" | split: "," %}
   ```
4. Do the same in the python validator list `mfr_files` in `scripts/validate.py` and `scripts/fipe_updater.py`.

### How to Auto-Update Tabela FIPE Prices
We query the public **Parallelum FIPE API** to update pricing.
*   **Run pricing sync for all models:**
    ```bash
    make update-fipe
    ```
*   **Run manual update for a single manufacturer:**
    ```bash
    python3 scripts/fipe_updater.py honda
    ```
    *(The script will perform fuzzy matching on model names, retrieve the latest Year or "Zero Km" price, and update the YAML fields).*

### How to Validate Changes
Run the schema check tool to ensure syntax validity and matching scoring safety:
```bash
python3 scripts/validate.py
```

---

## 🧠 The Matching Algorithm Engine

The matcher runs client-side inside [`matcher.js`](file:///whichbike/website/assets/js/matcher.js) and scores bikes from `0` to `100` across five pillars:

1.  **Physical Fit (35% weight):** Combines rider inseam against the seat height. The seat height is multiplied by a **Seat Width Profile** multiplier (e.g. `wide = 1.06`) because wide seats push the rider's legs outwards, increasing the reach needed. Deltas below `-2cm` are penalized for beginners.
2.  **Weight & Control (20% weight):** Assesses the bike's `wet_weight_kg`. Novices and safety-focused users receive a penalty on models above `150kg` to ensure the bike is easy to lift back up if dropped.
3.  **Safety & Experience (25% weight):** Beginner profiles receive heavy penalties on models with power output above `35 hp` or if `require-abs` is checked and the bike only has CBS (Combined Braking) or no ABS.
4.  **Uso & Localidade (20% weight):** 
    *   *Roads:* Trail/Adventure models get a boost on rough roads (`road-type: rough`), while Scooters and Streets get penalties.
    *   *Capital:* Metropolitan areas trigger insurance cost warnings and deduct score points for high-theft models.
    *   *Interior:* Deducts score points for niche brands with sparse parts network indices outside major capitals.
5.  **Budget Limits (Constraint & Adjuster):**
    *   If **"Ocultar motos que excedem meu orçamento"** is checked, any model with a FIPE price exceeding the slider value is strictly filtered out.
    *   If unchecked, over-budget models remain visible but suffer a `-25` score penalty and show a warning badge displaying the FIPE pricing conflict.

---

## 🚀 Deployment Pipeline (CI/CD)

The CI/CD pipeline runs automatically via GitHub Actions:
1.  **Trigger:** Pushes to the `main` branch modifying `website/**` or `.github/workflows/deploy.yml`.
2.  **Build:** Spin up an Ubuntu container, installs Ruby 3.2, bundles standard gems, and compiles Jekyll (`bundle exec jekyll build`).
3.  **Deploy:** The Action pushes the compiled `website/_site/` output directly to the `main` branch of your target hosting repository **daniloalsilva/whichbike.com** using `peaceiris/actions-gh-pages@v3`.
4.  **Prerequisite:** Ensure a repository secret named `DEPLOY_TOKEN` (a Personal Access Token with write access to `daniloalsilva/whichbike.com`) is configured in the source repository settings.
