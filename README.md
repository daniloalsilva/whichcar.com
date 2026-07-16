# WhichBike 🏍️

WhichBike is a personalized motorcycle aggregator and matching platform designed to help riders find the perfect motorcycle by matching their physical dimensions, experience level, maintenance preferences, usage requirements, and regional constraints.

---

## 🚀 The Vision

Unlike generic motorcycle databases or single-brand recommender tools, **WhichBike** uses a holistic matching algorithm that evaluates four primary pillars:

1.  **Physical Fit (Ergonomics):** Going beyond raw seat height by combining the rider's inseam with the seat's width/profile and the motorcycle's center of gravity to calculate a realistic "Reach Factor" and stoplight stability.
2.  **Rider Profile & Safety:** Mapping the rider's experience level, license tier, and comfort zone to the bike's power-to-weight ratio, throttle response, and safety aids (ABS, Traction Control).
3.  **Ownership & Maintenance:** Helping riders choose based on their mechanical willingness and budget by scoring bikes on parts availability, service complexity (e.g., chain vs. shaft drive), and expected annual maintenance.
4.  **Geographic & Local Constraints:** Adapting recommendations automatically based on IP/selected country to match local availability, import conditions, and licensing rules (e.g., EU A2 limits vs. US rules).

---

## 📊 Market Context & Differentiation

| Feature / Metric | Standard Tools (e.g., Cycle-Ergo, Motonomics) | WhichBike |
| :--- | :--- | :--- |
| **Physical Fit** | Static stick-figure diagrams and seat height numbers. | **Dynamic Fit Index:** Takes seat width, leg arch, and weight distribution into account. |
| **Maintenance** | None (requires searching forums). | **Maintenance Complexity Index:** Estimates ongoing effort and parts costs. |
| **Localization** | Geofenced to US/UK layouts or single brand. | **IP-based Localization:** Adapts to local licensing laws and market availability. |
| **Experience** | Simple "beginner vs. expert" binary scale. | **Power/Safety Profile Match:** Evaluates safety aids and power delivery curves. |

---

## 🗺️ Roadmap

### Phase 1: Interactive Matcher (MVP)
*   **Quiz Flow:** Multi-step wizard collecting rider height, inseam, experience, license class, and style preferences.
*   **Recommendation Engine:** Weighted compatibility scoring for an initial database of popular motorcycles.

### Phase 2: Virtual Garage & Customization
*   **Ergonomic Visualizer:** Modern, accessible posture simulator (2D/3D).
*   **Comparison Engine:** Side-by-side spec and utility comparisons for saved shortlists.

### Phase 3: Localization & Costs
*   Real-world price tracking (new and used markets).
*   Localized license filtering and country-specific availability.
