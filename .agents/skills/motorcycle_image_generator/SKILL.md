---
name: Motorcycle Image Generator & Transparency Tool
description: Workflows for generating side-profile motorcycle images, keying out white backgrounds to create transparent PNGs, and mapping them to WhichBike models.
---

# Motorcycle Image Generator & Transparency Tool Skill

This skill defines the process of generating consistent-looking, transparent-background motorcycle assets for the WhichBike comparison page.

## Workflow

### 1. Image Generation Prompting
When generating motorcycle images, use a standardized prompt to ensure a uniform visual perspective:
* **Style:** Professional studio side-profile photo.
* **Orientation:** Facing left.
* **Background:** Solid pure white background.
* **Prompt Template:**
  > "A professional high-resolution side profile studio photo of a [Brand/Model] motorcycle, looking left, isolated on a solid pure white background, crisp details, natural shadows under tires."

### 2. Transparency Processing (Chroma Keying)
Since AI generators do not natively output alpha transparency, use a Python script using Pillow (`PIL`) to key out the white pixels:
1. Open the generated image.
2. Convert to `RGBA` color mode.
3. Replace pixels close to pure white (`RGB > 240, 240, 240`) with transparent alpha values (`0`).
4. Save the resulting image as a `.png` file under `website/assets/images/generated/`.

### 3. Database Mapping
Map the relative asset path (`/assets/images/generated/filename.png`) to the corresponding models in the manufacturer YML files.
* Street Commuters -> `cg_160_titan.png`
* Trail / Adventure -> `lander_250.png` or `f_800_gs.png`
* Custom / Cruiser -> `eliminator_500.png` or `iron_883.png`
* Scooter / CUB -> `nmax_160.png`
* Naked / Sport -> `hornet_600.png`
