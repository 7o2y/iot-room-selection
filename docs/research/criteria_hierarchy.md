# Criteria Hierarchy Design

> **Design document for the AHP criteria hierarchy used in the IoT Room Selection system.**

## Hierarchy Structure

```
Select Best Room (Goal)
├─ Comfort (40%)
│  ├─ Temperature
│  ├─ Lighting
│  ├─ Noise
│  └─ Humidity
├─ Health (35%)
│  ├─ CO2
│  ├─ Air Quality (AQI)
│  └─ VOC
└─ Usability (25%)
   ├─ Seating Capacity
   ├─ Equipment (computers)
   └─ A/V Facilities (projector)
```

Each leaf node maps directly to the inputs expected by `AHPEngine.SUB_CRITERIA`, ensuring
the documentation stays in sync with the FastAPI backend module.

---

## Main Criteria Weights

| Criterion | Default Weight | Justification |
|-----------|----------------|---------------|
| **Comfort** | 40% | Physical comfort directly impacts productivity and satisfaction |
| **Health** | 35% | Poor air quality impairs cognitive function (studies show 15-50% decline) |
| **Usability** | 25% | Must meet basic functional requirements |

---

## Sub-Criteria Details

### Comfort (40%)

| Sub-Criterion | Local Weight | Global Weight | Data Source |
|---------------|--------------|---------------|-------------|
| Temperature | 35% | 14.0% | `temperature_sensor_data.json` |
| Lighting | 25% | 10.0% | `LightIntensity_sensor_data.json` |
| Noise | 25% | 10.0% | `sound_sensor_data.json` |
| Humidity | 15% | 6.0% | `humidity_sensor_data.json` |

### Health (35%)

| Sub-Criterion | Local Weight | Global Weight | Data Source |
|---------------|--------------|---------------|-------------|
| CO2 Level | 50% | 17.5% | `co2_sensor_data.json` |
| Air Quality | 30% | 10.5% | `air_quality_sensor_data.json` |
| VOC | 20% | 7.0% | `voc_sensor_data.json` |

### Usability (25%)

| Sub-Criterion | Local Weight | Global Weight | Data Source |
|---------------|--------------|---------------|-------------|
| Seating Capacity | 50% | 12.5% | `room_facilities_data.json` |
| Equipment | 30% | 7.5% | `room_facilities_data.json` |
| A/V Facilities | 20% | 5.0% | `room_facilities_data.json` |

---

## Pairwise Comparison Matrices

### Main Criteria Matrix

```
            Comfort  Health  Usability
Comfort   [   1      1.2     2.0   ]
Health    [  0.83    1       1.5   ]
Usability [  0.5    0.67     1     ]
```
CR = 0.003 ✓

### Comfort Sub-Criteria Matrix

```
              Temp   Light   Noise   Humidity
Temperature [  1      2       2        3     ]
Lighting    [ 0.5     1       1        2     ]
Noise       [ 0.5     1       1        2     ]
Humidity    [ 0.33   0.5     0.5       1     ]
```
CR = 0.008 ✓

### Health Sub-Criteria Matrix

```
               CO2    AirQuality   VOC
CO2         [  1        2          2    ]
AirQuality  [ 0.5       1          1.5  ]
VOC         [ 0.5      0.67        1    ]
```
CR = 0.005 ✓

### Usability Sub-Criteria Matrix

```
                 Seating   Equipment   A/V
SeatingCapacity [   1         2         3   ]
Equipment       [  0.5        1         2   ]
AVFacilities    [ 0.33       0.5        1   ]
```
CR = 0.009 ✓

---

## User Customization

Users can adjust weights via pairwise comparisons using the Saaty 1-9 scale:

| Preference Statement | Saaty Value |
|---------------------|-------------|
| "Temperature is equally important as Lighting" | 1 |
| "Health is moderately more important than Comfort" | 3 |
| "Noise is much more important than Humidity" | 5 |
| "CO2 is extremely more important than VOC" | 9 |

Example UI adjustment:
```
"How much more important is Health compared to Comfort?"
[ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ] [ 8 ] [ 9 ]
  ↑                 ↑                             ↑
Equal          Moderate                      Extreme
```
