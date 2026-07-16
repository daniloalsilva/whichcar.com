import os
import yaml

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
            price *= 1.12  # 12% covid-era and inflation market surge in Brazil
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

# Base dataset for 20 manufacturers
database = {
    "honda": [
        {
            "id": "honda-cg-160-titan", "brand": "Honda", "model": "CG 160 Titan", "category": "Street", 
            "engine_cc": 162.7, "power_hp": 15.1, "wet_weight_kg": 121, "seat_height_mm": 790, "seat_width_profile": "narrow", 
            "maintenance_index": 1, "parts_network_index": 10, "theft_risk_index": "critical",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 19500, "has_abs": False, "has_cbs": True}
            ]
        },
        {
            "id": "honda-biz-125", "brand": "Honda", "model": "Biz 125", "category": "CUB", 
            "engine_cc": 124.9, "power_hp": 9.2, "wet_weight_kg": 100, "seat_height_mm": 753, "seat_width_profile": "narrow", 
            "maintenance_index": 1, "parts_network_index": 10, "theft_risk_index": "high",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 17800, "has_abs": False, "has_cbs": True}
            ]
        },
        {
            "id": "honda-pop-110i", "brand": "Honda", "model": "Pop 110i ES", "category": "CUB", 
            "engine_cc": 109.1, "power_hp": 8.4, "wet_weight_kg": 87, "seat_height_mm": 749, "seat_width_profile": "narrow", 
            "maintenance_index": 1, "parts_network_index": 10, "theft_risk_index": "medium",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 11500, "has_abs": False, "has_cbs": True}
            ]
        },
        {
            "id": "honda-nxr-160-bros", "brand": "Honda", "model": "NXR 160 Bros", "category": "Trail", 
            "engine_cc": 162.7, "power_hp": 14.7, "wet_weight_kg": 122, "seat_height_mm": 836, "seat_width_profile": "medium-narrow", 
            "maintenance_index": 2, "parts_network_index": 10, "theft_risk_index": "high",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 21900, "has_abs": False, "has_cbs": True}
            ]
        },
        {
            "id": "honda-sahara-300", "brand": "Honda", "model": "Sahara 300 Standard", "category": "Trail", 
            "engine_cc": 293.5, "power_hp": 25.2, "wet_weight_kg": 147, "seat_height_mm": 859, "seat_width_profile": "medium-narrow", 
            "maintenance_index": 3, "parts_network_index": 10, "theft_risk_index": "high",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 30500, "has_abs": True, "has_cbs": False}
            ]
        },
        {
            "id": "honda-cb-300f-twister", "brand": "Honda", "model": "CB 300F Twister ABS", "category": "Street", 
            "engine_cc": 293.5, "power_hp": 24.7, "wet_weight_kg": 139, "seat_height_mm": 789, "seat_width_profile": "medium", 
            "maintenance_index": 2, "parts_network_index": 10, "theft_risk_index": "high",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 23900, "has_abs": True, "has_cbs": False}
            ]
        },
        {
            "id": "honda-nc-750x", "brand": "Honda", "model": "NC 750X", "category": "Adventure", 
            "engine_cc": 745.0, "power_hp": 58.6, "wet_weight_kg": 214, "seat_height_mm": 802, "seat_width_profile": "medium-wide", 
            "maintenance_index": 5, "parts_network_index": 10, "theft_risk_index": "medium-high",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 52900, "has_abs": True, "has_cbs": False}
            ]
        },
        {
            "id": "honda-xre-300", "brand": "Honda", "model": "XRE 300", "category": "Trail", 
            "engine_cc": 291.6, "power_hp": 25.4, "wet_weight_kg": 148, "seat_height_mm": 860, "seat_width_profile": "medium-narrow", 
            "maintenance_index": 3, "parts_network_index": 10, "theft_risk_index": "high",
            "history": [
                {"year": 2023, "is_used": True, "fipe_price_brl": 28900, "has_abs": True, "has_cbs": False},
                {"year": 2018, "is_used": True, "fipe_price_brl": 20045, "has_abs": True, "has_cbs": False},
                {"year": 2012, "is_used": True, "fipe_price_brl": 14500, "has_abs": False, "has_cbs": False}
            ]
        },
        {
            "id": "honda-hornet-600", "brand": "Honda", "model": "CB 600F Hornet", "category": "Sport", 
            "engine_cc": 599.0, "power_hp": 102.0, "wet_weight_kg": 198, "seat_height_mm": 800, "seat_width_profile": "medium-wide", 
            "maintenance_index": 6, "parts_network_index": 9, "theft_risk_index": "critical",
            "history": [
                {"year": 2014, "is_used": True, "fipe_price_brl": 38000, "has_abs": True, "has_cbs": False},
                {"year": 2012, "is_used": True, "fipe_price_brl": 34000, "has_abs": True, "has_cbs": False},
                {"year": 2007, "is_used": True, "fipe_price_brl": 26000, "has_abs": False, "has_cbs": False}
            ]
        }
    ],
    "yamaha": [
        {
            "id": "yamaha-factor-150", "brand": "Yamaha", "model": "Factor 150 UBS", "category": "Street", 
            "engine_cc": 149.0, "power_hp": 12.2, "wet_weight_kg": 127, "seat_height_mm": 785, "seat_width_profile": "narrow", 
            "maintenance_index": 2, "parts_network_index": 9, "theft_risk_index": "high",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 16900, "has_abs": False, "has_cbs": True}
            ]
        },
        {
            "id": "yamaha-fazer-fz25", "brand": "Yamaha", "model": "Fazer FZ25", "category": "Street", 
            "engine_cc": 249.0, "power_hp": 21.3, "wet_weight_kg": 149, "seat_height_mm": 790, "seat_width_profile": "medium", 
            "maintenance_index": 3, "parts_network_index": 9, "theft_risk_index": "critical",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 24900, "has_abs": True, "has_cbs": False}
            ]
        },
        {
            "id": "yamaha-xtz-250-lander", "brand": "Yamaha", "model": "XTZ 250 Lander", "category": "Trail", 
            "engine_cc": 249.0, "power_hp": 20.9, "wet_weight_kg": 153, "seat_height_mm": 875, "seat_width_profile": "medium", 
            "maintenance_index": 3, "parts_network_index": 9, "theft_risk_index": "high",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 28900, "has_abs": True, "has_cbs": False},
                {"year": 2020, "is_used": True, "fipe_price_brl": 21000, "has_abs": True, "has_cbs": False},
                {"year": 2012, "is_used": True, "fipe_price_brl": 14000, "has_abs": False, "has_cbs": False}
            ]
        },
        {
            "id": "yamaha-nmax-160", "brand": "Yamaha", "model": "NMAX 160", "category": "Scooter", 
            "engine_cc": 155.0, "power_hp": 15.4, "wet_weight_kg": 131, "seat_height_mm": 765, "seat_width_profile": "wide", 
            "maintenance_index": 4, "parts_network_index": 9, "theft_risk_index": "medium-high",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 22500, "has_abs": True, "has_cbs": False}
            ]
        },
        {
            "id": "yamaha-fluo-125", "brand": "Yamaha", "model": "Fluo 125 ABS", "category": "Scooter", 
            "engine_cc": 125.0, "power_hp": 9.5, "wet_weight_kg": 102, "seat_height_mm": 780, "seat_width_profile": "medium-wide", 
            "maintenance_index": 3, "parts_network_index": 9, "theft_risk_index": "medium",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 16200, "has_abs": True, "has_cbs": False}
            ]
        },
        {
            "id": "yamaha-crosser-150", "brand": "Yamaha", "model": "XTZ 150 Crosser ABS", "category": "Trail", 
            "engine_cc": 149.0, "power_hp": 12.2, "wet_weight_kg": 134, "seat_height_mm": 845, "seat_width_profile": "medium-narrow", 
            "maintenance_index": 2, "parts_network_index": 9, "theft_risk_index": "medium-high",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 20900, "has_abs": True, "has_cbs": False}
            ]
        },
        {
            "id": "yamaha-mt03", "brand": "Yamaha", "model": "MT-03 ABS", "category": "Sport", 
            "engine_cc": 321.0, "power_hp": 42.0, "wet_weight_kg": 169, "seat_height_mm": 780, "seat_width_profile": "medium", 
            "maintenance_index": 4, "parts_network_index": 9, "theft_risk_index": "high",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 32500, "has_abs": True, "has_cbs": False}
            ]
        },
        {
            "id": "yamaha-xt-660r", "brand": "Yamaha", "model": "XT 660R", "category": "Trail", 
            "engine_cc": 660.0, "power_hp": 48.0, "wet_weight_kg": 181, "seat_height_mm": 865, "seat_width_profile": "medium-narrow", 
            "maintenance_index": 4, "parts_network_index": 8, "theft_risk_index": "critical",
            "history": [
                {"year": 2018, "is_used": True, "fipe_price_brl": 41000, "has_abs": False, "has_cbs": False},
                {"year": 2014, "is_used": True, "fipe_price_brl": 36000, "has_abs": False, "has_cbs": False},
                {"year": 2008, "is_used": True, "fipe_price_brl": 24000, "has_abs": False, "has_cbs": False}
            ]
        }
    ],
    "suzuki": [
        {
            "id": "suzuki-v-strom-650", "brand": "Suzuki", "model": "V-Strom 650 XT", "category": "Adventure", 
            "engine_cc": 645.0, "power_hp": 71.0, "wet_weight_kg": 216, "seat_height_mm": 835, "seat_width_profile": "medium-wide", 
            "maintenance_index": 6, "parts_network_index": 6, "theft_risk_index": "medium",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 55900, "has_abs": True, "has_cbs": False}
            ]
        },
        {
            "id": "suzuki-gsx-s750", "brand": "Suzuki", "model": "GSX-S750", "category": "Sport", 
            "engine_cc": 749.0, "power_hp": 114.0, "wet_weight_kg": 213, "seat_height_mm": 820, "seat_width_profile": "medium", 
            "maintenance_index": 6, "parts_network_index": 6, "theft_risk_index": "high",
            "history": [
                {"year": 2021, "is_used": True, "fipe_price_brl": 52900, "has_abs": True, "has_cbs": False}
            ]
        },
        {
            "id": "suzuki-yes-125", "brand": "Suzuki", "model": "EN 125 Yes", "category": "Street", 
            "engine_cc": 124.0, "power_hp": 12.0, "wet_weight_kg": 112, "seat_height_mm": 735, "seat_width_profile": "narrow", 
            "maintenance_index": 1, "parts_network_index": 7, "theft_risk_index": "low",
            "history": [
                {"year": 2012, "is_used": True, "fipe_price_brl": 7500, "has_abs": False, "has_cbs": False},
                {"year": 2010, "is_used": True, "fipe_price_brl": 6500, "has_abs": False, "has_cbs": False},
                {"year": 2006, "is_used": True, "fipe_price_brl": 4500, "has_abs": False, "has_cbs": False}
            ]
        },
        {
            "id": "suzuki-bandit-650", "brand": "Suzuki", "model": "Bandit 650 S", "category": "Sport", 
            "engine_cc": 656.0, "power_hp": 85.0, "wet_weight_kg": 240, "seat_height_mm": 790, "seat_width_profile": "wide", 
            "maintenance_index": 5, "parts_network_index": 6, "theft_risk_index": "medium-high",
            "history": [
                {"year": 2015, "is_used": True, "fipe_price_brl": 31000, "has_abs": True, "has_cbs": False},
                {"year": 2012, "is_used": True, "fipe_price_brl": 26900, "has_abs": True, "has_cbs": False},
                {"year": 2008, "is_used": True, "fipe_price_brl": 19000, "has_abs": False, "has_cbs": False}
            ]
        }
    ],
    "kawasaki": [
        {
            "id": "kawasaki-eliminator", "brand": "Kawasaki", "model": "Eliminator", "category": "Retro", 
            "engine_cc": 451.0, "power_hp": 51.0, "wet_weight_kg": 176, "seat_height_mm": 735, "seat_width_profile": "medium", 
            "maintenance_index": 6, "parts_network_index": 4, "theft_risk_index": "medium",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 39900, "has_abs": True, "has_cbs": False}
            ]
        },
        {
            "id": "kawasaki-versys-x-300", "brand": "Kawasaki", "model": "Versys-X 300", "category": "Trail", 
            "engine_cc": 296.0, "power_hp": 40.0, "wet_weight_kg": 175, "seat_height_mm": 815, "seat_width_profile": "medium", 
            "maintenance_index": 6, "parts_network_index": 4, "theft_risk_index": "medium",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 35900, "has_abs": True, "has_cbs": False}
            ]
        },
        {
            "id": "kawasaki-ninja-400", "brand": "Kawasaki", "model": "Ninja 400", "category": "Sport", 
            "engine_cc": 399.0, "power_hp": 48.0, "wet_weight_kg": 168, "seat_height_mm": 785, "seat_width_profile": "medium-narrow", 
            "maintenance_index": 6, "parts_network_index": 4, "theft_risk_index": "high",
            "history": [
                {"year": 2023, "is_used": True, "fipe_price_brl": 34900, "has_abs": True, "has_cbs": False},
                {"year": 2020, "is_used": True, "fipe_price_brl": 28900, "has_abs": True, "has_cbs": False}
            ]
        },
        {
            "id": "kawasaki-vulcan-s", "brand": "Kawasaki", "model": "Vulcan S 650", "category": "Retro", 
            "engine_cc": 649.0, "power_hp": 61.0, "wet_weight_kg": 226, "seat_height_mm": 705, "seat_width_profile": "medium", 
            "maintenance_index": 6, "parts_network_index": 4, "theft_risk_index": "medium",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 44500, "has_abs": True, "has_cbs": False}
            ]
        }
    ],
    "bmw": [
        {
            "id": "bmw-g-310-gs", "brand": "BMW", "model": "G 310 GS", "category": "Adventure", 
            "engine_cc": 313.0, "power_hp": 34.0, "wet_weight_kg": 175, "seat_height_mm": 835, "seat_width_profile": "medium-wide", 
            "maintenance_index": 8, "parts_network_index": 3, "theft_risk_index": "critical",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 38900, "has_abs": True, "has_cbs": False}
            ]
        },
        {
            "id": "bmw-g-310-r", "brand": "BMW", "model": "G 310 R", "category": "Street", 
            "engine_cc": 313.0, "power_hp": 34.0, "wet_weight_kg": 164, "seat_height_mm": 785, "seat_width_profile": "medium", 
            "maintenance_index": 8, "parts_network_index": 3, "theft_risk_index": "high",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 35900, "has_abs": True, "has_cbs": False}
            ]
        },
        {
            "id": "bmw-f-800-gs", "brand": "BMW", "model": "F 800 GS", "category": "Adventure", 
            "engine_cc": 798.0, "power_hp": 85.0, "wet_weight_kg": 214, "seat_height_mm": 880, "seat_width_profile": "medium-wide", 
            "maintenance_index": 8, "parts_network_index": 3, "theft_risk_index": "critical",
            "history": [
                {"year": 2017, "is_used": True, "fipe_price_brl": 44000, "has_abs": True, "has_cbs": False},
                {"year": 2015, "is_used": True, "fipe_price_brl": 39900, "has_abs": True, "has_cbs": False},
                {"year": 2011, "is_used": True, "fipe_price_brl": 31000, "has_abs": True, "has_cbs": False}
            ]
        },
        {
            "id": "bmw-f-900-r", "brand": "BMW", "model": "F 900 R", "category": "Sport", 
            "engine_cc": 895.0, "power_hp": 85.0, "wet_weight_kg": 211, "seat_height_mm": 815, "seat_width_profile": "medium", 
            "maintenance_index": 9, "parts_network_index": 3, "theft_risk_index": "critical",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 64900, "has_abs": True, "has_cbs": False}
            ]
        }
    ],
    "royal_enfield": [
        {
            "id": "royal-enfield-hunter-350", "brand": "Royal Enfield", "model": "Hunter 350", "category": "Retro", 
            "engine_cc": 349.0, "power_hp": 20.2, "wet_weight_kg": 181, "seat_height_mm": 790, "seat_width_profile": "medium", 
            "maintenance_index": 4, "parts_network_index": 4, "theft_risk_index": "low",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 21900, "has_abs": True, "has_cbs": False}
            ]
        },
        {
            "id": "royal-enfield-classic-350", "brand": "Royal Enfield", "model": "Classic 350", "category": "Retro", 
            "engine_cc": 349.0, "power_hp": 20.2, "wet_weight_kg": 195, "seat_height_mm": 805, "seat_width_profile": "medium-wide", 
            "maintenance_index": 4, "parts_network_index": 4, "theft_risk_index": "low",
            "history": [
                {"year": 2024, "is_used": True, "fipe_price_brl": 22900, "has_abs": True, "has_cbs": False}
            ]
        },
        {
            "id": "royal-enfield-meteor-350", "brand": "Royal Enfield", "model": "Meteor 350", "category": "Retro", 
            "engine_cc": 349.0, "power_hp": 20.2, "wet_weight_kg": 191, "seat_height_mm": 765, "seat_width_profile": "medium-wide", 
            "maintenance_index": 4, "parts_network_index": 4, "theft_risk_index": "low",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 23900, "has_abs": True, "has_cbs": False}
            ]
        },
        {
            "id": "royal-enfield-himalayan", "brand": "Royal Enfield", "model": "Himalayan 411", "category": "Trail", 
            "engine_cc": 411.0, "power_hp": 24.3, "wet_weight_kg": 191, "seat_height_mm": 800, "seat_width_profile": "medium", 
            "maintenance_index": 5, "parts_network_index": 4, "theft_risk_index": "low",
            "history": [
                {"year": 2021, "is_used": True, "fipe_price_brl": 25900, "has_abs": True, "has_cbs": False}
            ]
        }
    ],
    "bajaj": [
        {
            "id": "bajaj-dominar-160", "brand": "Bajaj", "model": "Dominar 160", "category": "Street", 
            "engine_cc": 160.3, "power_hp": 17.0, "wet_weight_kg": 154, "seat_height_mm": 805, "seat_width_profile": "medium", 
            "maintenance_index": 3, "parts_network_index": 3, "theft_risk_index": "low-medium",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 16900, "has_abs": True, "has_cbs": False}
            ]
        },
        {
            "id": "bajaj-dominar-200", "brand": "Bajaj", "model": "Dominar 200", "category": "Street", 
            "engine_cc": 199.5, "power_hp": 24.5, "wet_weight_kg": 154, "seat_height_mm": 805, "seat_width_profile": "medium", 
            "maintenance_index": 3, "parts_network_index": 3, "theft_risk_index": "medium",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 19900, "has_abs": True, "has_cbs": False}
            ]
        },
        {
            "id": "bajaj-dominar-400", "brand": "Bajaj", "model": "Dominar 400", "category": "Sport", 
            "engine_cc": 373.3, "power_hp": 40.0, "wet_weight_kg": 193, "seat_height_mm": 800, "seat_width_profile": "medium", 
            "maintenance_index": 5, "parts_network_index": 3, "theft_risk_index": "medium",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 26393, "has_abs": True, "has_cbs": False}
            ]
        }
    ],
    "triumph": [
        {
            "id": "triumph-tiger-sport-660", "brand": "Triumph", "model": "Tiger Sport 660", "category": "Adventure", 
            "engine_cc": 660.0, "power_hp": 81.0, "wet_weight_kg": 206, "seat_height_mm": 835, "seat_width_profile": "medium-wide", 
            "maintenance_index": 7, "parts_network_index": 3, "theft_risk_index": "high",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 56900, "has_abs": True, "has_cbs": False}
            ]
        },
        {
            "id": "triumph-trident-660", "brand": "Triumph", "model": "Trident 660", "category": "Sport", 
            "engine_cc": 660.0, "power_hp": 81.0, "wet_weight_kg": 189, "seat_height_mm": 805, "seat_width_profile": "medium", 
            "maintenance_index": 7, "parts_network_index": 3, "theft_risk_index": "high",
            "history": [
                {"year": 2023, "is_used": True, "fipe_price_brl": 49900, "has_abs": True, "has_cbs": False}
            ]
        }
    ],
    "harley_davidson": [
        {
            "id": "harley-davidson-iron-883", "brand": "Harley-Davidson", "model": "Iron 883", "category": "Retro", 
            "engine_cc": 883.0, "power_hp": 52.0, "wet_weight_kg": 256, "seat_height_mm": 760, "seat_width_profile": "medium-wide", 
            "maintenance_index": 7, "parts_network_index": 4, "theft_risk_index": "low",
            "history": [
                {"year": 2020, "is_used": True, "fipe_price_brl": 48900, "has_abs": True, "has_cbs": False}
            ]
        },
        {
            "id": "harley-davidson-fat-boy", "brand": "Harley-Davidson", "model": "Fat Boy 114", "category": "Retro", 
            "engine_cc": 1868.0, "power_hp": 94.0, "wet_weight_kg": 317, "seat_height_mm": 675, "seat_width_profile": "wide", 
            "maintenance_index": 8, "parts_network_index": 4, "theft_risk_index": "low",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 105000, "has_abs": True, "has_cbs": False}
            ]
        }
    ],
    "ducati": [
        {
            "id": "ducati-scrambler-icon", "brand": "Ducati", "model": "Scrambler Icon", "category": "Retro", 
            "engine_cc": 803.0, "power_hp": 73.0, "wet_weight_kg": 189, "seat_height_mm": 798, "seat_width_profile": "medium", 
            "maintenance_index": 8, "parts_network_index": 2, "theft_risk_index": "medium",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 54900, "has_abs": True, "has_cbs": False}
            ]
        }
    ],
    "dafra": [
        {
            "id": "dafra-citycom-300i", "brand": "Dafra", "model": "Citycom 300i", "category": "Scooter", 
            "engine_cc": 263.0, "power_hp": 23.0, "wet_weight_kg": 185, "seat_height_mm": 800, "seat_width_profile": "medium-wide", 
            "maintenance_index": 4, "parts_network_index": 6, "theft_risk_index": "medium",
            "history": [
                {"year": 2018, "is_used": True, "fipe_price_brl": 22900, "has_abs": True, "has_cbs": False}
            ]
        },
        {
            "id": "dafra-nh-190", "brand": "Dafra", "model": "NH 190", "category": "Trail", 
            "engine_cc": 183.0, "power_hp": 18.0, "wet_weight_kg": 141, "seat_height_mm": 820, "seat_width_profile": "medium", 
            "maintenance_index": 3, "parts_network_index": 6, "theft_risk_index": "medium",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 17900, "has_abs": False, "has_cbs": True}
            ]
        }
    ],
    "shineray": [
        {
            "id": "shineray-jet-125", "brand": "Shineray", "model": "Jet 125 SS", "category": "CUB", 
            "engine_cc": 123.6, "power_hp": 7.2, "wet_weight_kg": 95, "seat_height_mm": 750, "seat_width_profile": "narrow", 
            "maintenance_index": 2, "parts_network_index": 7, "theft_risk_index": "medium",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 10500, "has_abs": False, "has_cbs": True}
            ]
        },
        {
            "id": "shineray-worker-125", "brand": "Shineray", "model": "Worker 125", "category": "Street", 
            "engine_cc": 123.6, "power_hp": 7.2, "wet_weight_kg": 98, "seat_height_mm": 740, "seat_width_profile": "narrow", 
            "maintenance_index": 1, "parts_network_index": 7, "theft_risk_index": "low",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 8900, "has_abs": False, "has_cbs": False}
            ]
        }
    ],
    "mottu": [
        {
            "id": "mottu-sport-110", "brand": "Mottu", "model": "Sport 110i", "category": "Street", 
            "engine_cc": 109.7, "power_hp": 8.3, "wet_weight_kg": 110, "seat_height_mm": 760, "seat_width_profile": "narrow", 
            "maintenance_index": 1, "parts_network_index": 6, "theft_risk_index": "medium-high",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 9900, "has_abs": False, "has_cbs": True}
            ]
        }
    ],
    "avelloz": [
        {
            "id": "avelloz-az1", "brand": "Avelloz", "model": "AZ1", "category": "CUB", 
            "engine_cc": 49.0, "power_hp": 5.0, "wet_weight_kg": 90, "seat_height_mm": 745, "seat_width_profile": "narrow", 
            "maintenance_index": 1, "parts_network_index": 5, "theft_risk_index": "low",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 9500, "has_abs": False, "has_cbs": True}
            ]
        }
    ],
    "haojue": [
        {
            "id": "haojue-chopper-150", "brand": "Haojue", "model": "Chopper Road 150", "category": "Retro", 
            "engine_cc": 149.0, "power_hp": 11.2, "wet_weight_kg": 130, "seat_height_mm": 740, "seat_width_profile": "narrow", 
            "maintenance_index": 2, "parts_network_index": 7, "theft_risk_index": "low",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 15900, "has_abs": False, "has_cbs": True}
            ]
        },
        {
            "id": "haojue-dr-160", "brand": "Haojue", "model": "DR 160 FI", "category": "Street", 
            "engine_cc": 162.0, "power_hp": 15.0, "wet_weight_kg": 148, "seat_height_mm": 790, "seat_width_profile": "medium", 
            "maintenance_index": 2, "parts_network_index": 7, "theft_risk_index": "medium",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 18900, "has_abs": False, "has_cbs": True}
            ]
        }
    ],
    "ktm": [
        {
            "id": "ktm-duke-200", "brand": "KTM", "model": "Duke 200", "category": "Street", 
            "engine_cc": 199.5, "power_hp": 26.0, "wet_weight_kg": 148, "seat_height_mm": 810, "seat_width_profile": "medium", 
            "maintenance_index": 5, "parts_network_index": 3, "theft_risk_index": "medium",
            "history": [
                {"year": 2019, "is_used": True, "fipe_price_brl": 16900, "has_abs": True, "has_cbs": False}
            ]
        },
        {
            "id": "ktm-duke-390", "brand": "KTM", "model": "Duke 390", "category": "Sport", 
            "engine_cc": 373.2, "power_hp": 44.0, "wet_weight_kg": 163, "seat_height_mm": 830, "seat_width_profile": "medium", 
            "maintenance_index": 5, "parts_network_index": 3, "theft_risk_index": "medium-high",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 29900, "has_abs": True, "has_cbs": False}
            ]
        }
    ],
    "kymco": [
        {
            "id": "kymco-downtown-300", "brand": "Kymco", "model": "Downtown 300i ABS", "category": "Scooter", 
            "engine_cc": 299.0, "power_hp": 29.7, "wet_weight_kg": 189, "seat_height_mm": 775, "seat_width_profile": "wide", 
            "maintenance_index": 5, "parts_network_index": 4, "theft_risk_index": "medium",
            "history": [
                {"year": 2018, "is_used": True, "fipe_price_brl": 18900, "has_abs": True, "has_cbs": False}
            ]
        }
    ],
    "zontes": [
        {
            "id": "zontes-r310", "brand": "Zontes", "model": "R-310", "category": "Street", 
            "engine_cc": 312.0, "power_hp": 35.0, "wet_weight_kg": 159, "seat_height_mm": 795, "seat_width_profile": "medium", 
            "maintenance_index": 5, "parts_network_index": 3, "theft_risk_index": "low-medium",
            "history": [
                {"year": 2024, "is_used": True, "fipe_price_brl": 26900, "has_abs": True, "has_cbs": False}
            ]
        }
    ],
    "voltz": [
        {
            "id": "voltz-evs", "brand": "Voltz", "model": "EVS", "category": "Street", 
            "engine_cc": 0.0, "power_hp": 10.0, "wet_weight_kg": 130, "seat_height_mm": 800, "seat_width_profile": "medium", 
            "maintenance_index": 3, "parts_network_index": 2, "theft_risk_index": "medium",
            "history": [
                {"year": 2022, "is_used": True, "fipe_price_brl": 19900, "has_abs": False, "has_cbs": True}
            ]
        }
    ],
    "vespa": [
        {
            "id": "vespa-primavera-150", "brand": "Vespa", "model": "Primavera 150", "category": "Scooter", 
            "engine_cc": 155.0, "power_hp": 12.9, "wet_weight_kg": 126, "seat_height_mm": 790, "seat_width_profile": "medium-wide", 
            "maintenance_index": 7, "parts_network_index": 3, "theft_risk_index": "medium",
            "history": [
                {"year": 2026, "is_used": False, "fipe_price_brl": 32900, "has_abs": True, "has_cbs": False}
            ]
        }
    ]
}

data_dir = "/home/danilo/Projects/whichbike/website/_data"
os.makedirs(data_dir, exist_ok=True)

def get_enrichment_data(bike_id, category):
    cat = category.lower()
    b_id = bike_id.lower()
    
    # Defaults
    image_path = "/assets/images/generated/cg_160.png"
    wheel_size = 'D: 17" / T: 17"'
    ground_clearance = 145
    
    if cat == "sport":
        image_path = "/assets/images/generated/hornet_600.png"
        wheel_size = 'D: 17" / T: 17"'
        ground_clearance = 135 if "bandit" in b_id or "gsx" in b_id else 140
    elif cat in ["trail", "adventure"]:
        image_path = "/assets/images/generated/lander_250.png"
        if "v-strom" in b_id or "g-310-gs" in b_id or "tiger" in b_id:
            wheel_size = 'D: 19" / T: 17"'
            ground_clearance = 180
        else:
            wheel_size = 'D: 21" / T: 18"'
            ground_clearance = 220
    elif cat in ["cub", "scooter"]:
        image_path = "/assets/images/generated/nmax_160.png"
        if "nmax" in b_id:
            wheel_size = 'D: 13" / T: 13"'
        elif "biz" in b_id:
            wheel_size = 'D: 17" / T: 14"'
        elif "pop" in b_id:
            wheel_size = 'D: 17" / T: 17"'
        elif "vespa" in b_id:
            wheel_size = 'D: 12" / T: 12"'
        else:
            wheel_size = 'D: 16" / T: 14"'
        ground_clearance = 120
    elif cat == "retro":
        image_path = "/assets/images/generated/eliminator_500.png"
        if "eliminator" in b_id or "vulcan" in b_id:
            wheel_size = 'D: 18" / T: 16"'
        elif "iron" in b_id:
            wheel_size = 'D: 19" / T: 16"'
        elif "fat-boy" in b_id:
            wheel_size = 'D: 18" / T: 18"'
        elif "hunter" in b_id:
            wheel_size = 'D: 17" / T: 17"'
        else:
            wheel_size = 'D: 19" / T: 18"'
        ground_clearance = 135
    else:
        image_path = "/assets/images/generated/cg_160.png"
        wheel_size = 'D: 17" / T: 17"'
        ground_clearance = 150
        
    return image_path, wheel_size, ground_clearance

for mfr, bikes in database.items():
    for bike in bikes:
        b_id = bike.get("id", "")
        category = bike.get("category", "")
        img_path, wheel_sz, clearance = get_enrichment_data(b_id, category)
        
        # Hydrate model-level attributes
        bike["image_path"] = img_path
        bike["wheel_size"] = wheel_sz
        bike["ground_clearance_mm"] = clearance
        
        # Hydrate each history variant with price_history list
        for var in bike["history"]:
            var["price_history"] = generate_yoy_history(var["year"], var["fipe_price_brl"], var["is_used"])

    file_path = os.path.join(data_dir, f"{mfr}.yml")
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(bikes, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"Generated: {file_path} ({len(bikes)} bikes)")
