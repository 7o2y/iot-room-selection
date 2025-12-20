# User Guide - IoT Room Selection

## Welcome!

This guide will help you use the IoT Room Selection system to find the best room for your needs based on environmental conditions and your personal preferences.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Understanding the Interface](#understanding-the-interface)
3. [Step-by-Step Guide](#step-by-step-guide)
4. [Understanding Your Results](#understanding-your-results)
5. [Tips & Best Practices](#tips--best-practices)
6. [FAQ](#faq)

---

## Getting Started

### What is This System?

The IoT Room Selection system helps you find the best room based on:
- **Environmental factors:** Temperature, CO2, humidity, noise, light
- **Facilities:** Projectors, computers, robots, seating capacity
- **Your preferences:** What matters most to you (comfort, health, or usability)?

### Who Should Use This?

- **Students:** Finding a comfortable study room
- **Teachers:** Selecting an optimal classroom
- **Researchers:** Choosing a lab with specific requirements

---

## Understanding the Interface

### Main Page Layout

When you open the Room Selection page, you'll see three sections:

```
┌─────────────────────────────────────────┐
│          1. Preference Sliders          │
│      (What matters most to you?)        │
├─────────────────────────────────────────┤
│       2. Environmental Thresholds       │
│     (Your ideal room conditions)        │
├─────────────────────────────────────────┤
│         3. Evaluate Rooms Button        │
├─────────────────────────────────────────┤
│          4. Room Rankings               │
│        (Your personalized results)      │
└─────────────────────────────────────────┘
```

---

## Step-by-Step Guide

### Step 1: Set Your Priorities (Left Panel)

**Question: What matters most to you?**

You'll see 3 sliders comparing different priorities:

#### Slider 1: Comfort vs Health
- **Move LEFT** if comfort (temperature, noise) is more important
- **Move RIGHT** if health (air quality, CO2) is more important
- **Keep CENTER** if they're equally important

**Example:**
- "I get cold easily" → Move LEFT (prioritize comfort/temperature)
- "I have asthma" → Move RIGHT (prioritize health/air quality)

#### Slider 2: Comfort vs Usability
- **Move LEFT** if comfort is more important
- **Move RIGHT** if facilities (projectors, computers) matter more

**Example:**
- "I just need a quiet place to read" → Move LEFT (comfort)
- "I need a projector for my presentation" → Move RIGHT (usability)

#### Slider 3: Health vs Usability
- Similar logic: Health (air quality) vs Facilities

---

### Understanding the Scale

Each slider uses a 1-9 scale:

```
Left        |    Equal    |        Right
Extreme  Moderate         Moderate  Extreme
   9    7  5  3     1     3  5  7    9
```

**What does it mean?**
- **1 (Center):** Both are equally important
- **3:** One is slightly more important
- **5:** One is moderately more important
- **7:** One is much more important
- **9:** One is extremely more important

**You'll see your weights update automatically:**
- Comfort: 40%
- Health: 35%
- Usability: 25%

**Consistency Ratio:**
- **Green ✓ (< 0.1):** Your preferences are consistent
- **Yellow ⚠ (≥ 0.1):** Your preferences contradict each other - try adjusting

---

### Step 2: Set Your Environmental Preferences (Right Panel)

**Question: What are your ideal room conditions?**

Adjust 5 sliders to set your personal thresholds:

#### 🌡️ Temperature (18°C - 26°C)
- **Optimal:** 20-24°C (EU standard)
- **Move slider** to set your maximum acceptable temperature
- Green thumb = within optimal range

**Example:**
- "I prefer cooler rooms" → Set to 22°C
- "I don't mind warmth" → Set to 26°C

#### 💨 CO2 Level (0 - 1000 ppm)
- **Optimal:** 0-600 ppm (good air quality)
- Lower = fresher air
- Higher = more stuffy

**Example:**
- "I need very fresh air" → Set to 500 ppm
- "I don't mind" → Set to 800 ppm

#### 💧 Humidity (30% - 70%)
- **Optimal:** 40-60% (comfortable)
- Too low = dry air
- Too high = muggy

#### 🔇 Noise Level (0 - 45 dBA)
- **Optimal:** 0-35 dBA (quiet)
- **Example:**
  - "I need absolute silence" → Set to 30 dBA
  - "Background noise is OK" → Set to 45 dBA

#### 💡 Light Level (200 - 750 lux)
- **Optimal:** 300-500 lux (office lighting)
- **Example:**
  - "I prefer dim lighting" → Set to 300 lux
  - "I need bright light" → Set to 600 lux

**Reset Button:**
- Click "Reset" to restore EU standard defaults

---

### Step 3: Evaluate Rooms

Once you've set your preferences:

1. Click the blue **"Evaluate Rooms"** button
2. Wait 1-2 seconds (you'll see "Evaluating Rooms...")
3. Results appear below!

---

## Understanding Your Results

### Summary Cards

At the top, you'll see 4 cards:

```
┌────────────┬────────────┬────────────┬────────────┐
│   Rooms    │ Consistency│   Best     │    Top     │
│ Evaluated  │   Ratio    │   Match    │   Score    │
│     10     │    0.05    │  Room 2    │    92%     │
└────────────┴────────────┴────────────┴────────────┘
```

- **Rooms Evaluated:** Total number of rooms analyzed
- **Consistency Ratio:** How consistent your preferences are
- **Best Match:** The top-ranked room for you
- **Top Score:** How well the best room matches your needs

---

### Rankings Table

Each room shows:

| Column | Meaning |
|--------|---------|
| **Rank** | 🥇🥈🥉 Gold/Silver/Bronze for top 3 |
| **Room Name** | Room identifier (e.g., "MSA 4.450") |
| **Overall Score** | 0-100% match to your preferences |
| **Temp** | ✓ Green = Good, ⚠ Yellow = OK, ✗ Red = Bad |
| **CO2** | Current CO2 level with status |
| **Humidity** | Current humidity with status |
| **Facilities** | 📽️ Projector, 💻 Computers, 🤖 Robots, + seat count |
| **Details** | Click "Show" to see breakdown |

---

### Status Badges

**✓ Green:** Value is in optimal range (ideal for you)
**⚠ Yellow:** Value is acceptable but not ideal
**✗ Red:** Value is outside your acceptable range

---

### Detailed Breakdown

Click **"Show"** on any room to see:

```
┌─────────────────────────────────────────┐
│  Comfort Score: 89%    [█████████ ]     │
│  Health Score:  95%    [██████████]     │
│  Usability Score: 91%  [█████████ ]     │
├─────────────────────────────────────────┤
│  Temperature: 23.0°C                    │
│  CO2 Level: 695 ppm                     │
│  Humidity: 50.2%                        │
│  Air Quality: 25.1 AQI                  │
│  VOC: 250 ppb                           │
├─────────────────────────────────────────┤
│  Facilities:                            │
│  [23 Seats] [📽️ Projector] [💻 20 PCs] │
└─────────────────────────────────────────┘
```

**What do the scores mean?**
- **Comfort Score:** How well temperature, humidity, noise, light match your preferences
- **Health Score:** How good the air quality (CO2, VOC, air quality index) is
- **Usability Score:** How well the facilities match your needs

---

## Tips & Best Practices

### For Students

**Scenario: "I need a quiet place to study"**

1. **Priorities:** Comfort > Health > Usability
   - Comfort↔Health: Move slightly LEFT (comfort priority)
   - Comfort↔Usability: Move LEFT (don't need facilities)

2. **Thresholds:**
   - Noise: Set to 30 dBA (very quiet)
   - Temperature: 22°C (comfortable)
   - CO2: 600 ppm (acceptable)

3. **Result:** Rooms with low noise will rank higher

---

**Scenario: "I need computers for a coding session"**

1. **Priorities:** Usability > Comfort > Health
   - Comfort↔Usability: Move RIGHT (facilities matter)
   - Health↔Usability: Move RIGHT (facilities matter)

2. **Thresholds:** Use defaults or adjust to preference

3. **Result:** Rooms with many computers will rank #1

---

### For Teachers

**Scenario: "I need a large room with good ventilation for a lecture"**

1. **Priorities:** Health > Usability > Comfort
   - Comfort↔Health: Move RIGHT (air quality important)
   - Health↔Usability: Move LEFT (health first, but facilities needed)

2. **Thresholds:**
   - CO2: Set to 500 ppm (strict)
   - Light: 400 lux (good for presentations)

3. **Facilities:** Look for projector icon 📽️ in results

4. **Result:** Large rooms with good air quality rank highest

---

## FAQ

### Q: Why does the #1 room have a red badge for CO2?

**A:** The overall score considers ALL your priorities. If you prioritized Comfort or Usability over Health, a room with slightly high CO2 might still rank #1 due to excellent temperature or facilities.

**Solution:** Increase Health priority or lower CO2 threshold and re-evaluate.

---

### Q: The consistency ratio is yellow (≥0.1). What does this mean?

**A:** Your preferences contradict each other.

**Example:**
- You said Comfort > Health (moved slider left 7)
- You said Health > Usability (moved slider left 5)
- You said Usability > Comfort (moved slider right 6)
- This creates a logical contradiction!

**Solution:** Adjust one slider to make your preferences more consistent.

---

### Q: Can I save my preferences?

**A:** Not currently (v1.0). Preferences are lost when you refresh the page.

**Future:** User accounts with saved profiles planned.

---

### Q: How often is the sensor data updated?

**A:**
- **Mock mode:** Static data from aggregated_rooms.json
- **Live mode:** Real-time sensor readings (when backend is connected)

---

### Q: What if I don't care about one factor?

**A:** Set that threshold to the maximum acceptable range.

**Example:** Don't care about noise?
- Set Noise slider to 45 dBA (maximum)
- This won't penalize noisy rooms

---

### Q: Can I compare two rooms side-by-side?

**A:** Not yet (v1.0), but planned for future versions.

**Workaround:** Open breakdown for both rooms and compare scores manually.

---

### Q: Why do rankings change when I adjust one slider?

**A:** Each slider affects the weights:
- Moving one slider changes the relative importance of all three criteria
- This changes how rooms are scored
- Different weights = different rankings

This is how the AHP algorithm works - it's dynamic!

---

### Q: What's the difference between the sliders on the left vs right?

**Left (Saaty Sliders):**
- Set PRIORITIES (what matters most)
- Affects weight distribution
- Comparative judgments

**Right (Threshold Sliders):**
- Set ACCEPTABLE RANGES (your ideal conditions)
- Affects how rooms are scored
- Absolute values

**Both work together** to find your ideal room!

---

## Getting Help

**Problems?**
- Error message? Check browser console (F12)
- Rankings don't make sense? Check consistency ratio
- Button not working? Refresh the page

**Contact:**
- Technical support: Filip Zekonja (Frontend)
- Algorithm questions: Fede (AHP Implementation)
- Backend/API: Anthony

---

## Next Steps

1. ✅ Try different preference combinations
2. ✅ Explore the detailed breakdowns
3. ✅ Check out the API documentation (click "API Docs" in navigation)
4. ✅ Provide feedback to the development team!

---

**Enjoy finding your perfect room! 🏆**

---

**Version:** 1.0
**Last Updated:** 2024-12-20
