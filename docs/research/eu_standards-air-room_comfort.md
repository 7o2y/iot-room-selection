# EU Indoor Environmental Quality Standards Research

> **Reference Standard:** **EN 16798-1:2019** - Energy performance of buildings - Ventilation for buildings - Part 1: Indoor environmental input parameters for design and assessment of energy performance of buildings addressing indoor air quality, thermal environment, lighting and acoustics.

This document summarizes the recommended threshold values for indoor environmental quality (IEQ) categories, specifically focusing on **Category II (Normal Expectation)** which is the standard target for new buildings and renovations.

## 1. Thermal Environment (Temperature)

Based on operative temperature for office-like spaces.

| Category | Season | Recommended Range (°C) | Description |
|----------|--------|------------------------|-------------|
| **I** (High) | Winter | 21.0 - 23.0 | Spaces occupied by very sensitive and fragile persons |
| **I** (High) | Summer | 23.5 - 25.5 | |
| **II** (Normal) | **Winter** | **20.0 - 24.0** | **New buildings and renovations (Standard)** |
| **II** (Normal) | **Summer** | **23.0 - 26.0** | |
| **III** (Moderate)| Winter | 19.0 - 25.0 | Be existing buildings |
| **III** (Moderate)| Summer | 22.0 - 27.0 | |

> **Note:** "Summer" values typically assume cooling systems. For free-running (non-cooled) buildings, adaptive thermal comfort models apply.

## 2. Indoor Air Quality (CO2 & Ventilation)

CO2 levels are used as a proxy for ventilation adequacy. The values below are **above outdoor concentration** (typically 400 ppm).

| Category | CO2 Above Outdoor (ppm) | Total CO2 Est. (ppm)* | Ventilation Rate per Person (l/s) |
|----------|-------------------------|-----------------------|-----------------------------------|
| I | 550 | < 950 | 10 |
| **II** | **800** | **< 1200** | **7** |
| III | 1350 | < 1750 | 4 |
| IV | > 1350 | > 1750 | < 4 |

*Assuming outdoor CO2 is approx. 400 ppm.

## 3. Humidity

Relative Humidity (RH) ranges for health and comfort.

| Category | Design Dehumidification (Max) | Design Humidification (Min) |
|----------|-------------------------------|-----------------------------|
| I | 50% | 30% |
| **II** | **60%** | **25%** |
| III | 70% | 20% |

> **General Recommendation:** Keep between **30% - 60%**.

## 4. Lighting (EN 12464-1)

Reference: **EN 12464-1** - Light and lighting - Lighting of work places.

| Type of Area | Lux (Illuminance) | UGR (Glare Limit) | Ra (Color Rendering) |
|--------------|-------------------|-------------------|----------------------|
| Classrooms/Tutorial rooms | 300 - 500 | 19 | 80 |
| Offices (Writing/Typing) | 500 | 19 | 80 |
| Corridors | 100 | 28 | 40 |

> **Target:** **300 - 500 Lux** for study/work areas.

## 5. Acoustics (noise)

Reference: EN 16798-1 & WHO Guidelines. Values are A-weighted equivalent sound pressure levels ($L_{Aeq}$).

| Category | Maximum Noise Level (dBA) |
|----------|---------------------------|
| I | 30 - 35 |
| **II** | **35 - 40** |
| III | 40 - 45 |

> **Target:** **< 40 dBA** for concentration; **< 35 dBA** for high comfort.

## 6. Volatile Organic Compounds (VOCs)

While EN 16798-1 focuses on ventilation rates, other standards (like WELL or national regulations) provide specific limits.

| Contaminant | Limit (ppb approx) | Limit (µg/m³) |
|-------------|--------------------|---------------|
| Total VOCs | < 300 ppb | < 500 µg/m³ |
| Formaldehyde| < 80 ppb | < 100 µg/m³ |

---

## Summary of "Comfortable Room" Criteria (Category II)

For the Room Selection Algorithm, a "Comfortable Room" is defined as:

1.  **Temperature:** 20.0°C - 26.0°C (Season dependent)
2.  **CO2:** < 1200 ppm
3.  **Humidity:** 30% - 60%
4.  **Lighting:** 300 - 500 Lux
5.  **Sound:** < 40 dBA
