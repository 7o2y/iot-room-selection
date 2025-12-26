# UI/UX Documentation - IoT Room Selection

## Overview

This document provides comprehensive documentation for the user interface and user experience of the IoT Room Selection Decision Support System.

**Project:** IoT Room Selection Decision Support System
**Team:** Anthony (Backend), Fede (AHP Algorithm), Filip (Frontend/UI)
**Tech Stack:** React (Vite), Tailwind CSS v4, Lucide React Icons
**Academic Year:** 2025-2026, University of Luxembourg

---

## Table of Contents

1. [Design Philosophy](#design-philosophy)
2. [User Flow](#user-flow)
3. [Pages & Components](#pages--components)
4. [Design System](#design-system)
5. [Responsive Design](#responsive-design)
6. [Accessibility](#accessibility)
7. [User Testing](#user-testing)

---

## Design Philosophy

### Goals

1. **Simplicity First**: The system must be intuitive for students and teachers without technical training
2. **Immediate Feedback**: Users see results in real-time as they adjust preferences
3. **Transparency**: Clear explanations of how the AHP algorithm works
4. **Trust Building**: Visual confidence indicators (consistency ratio, score breakdowns)

### Design Principles

- **Progressive Disclosure**: Show simple controls first, detailed breakdowns on demand
- **Visual Hierarchy**: Important elements (final scores, rankings) stand out
- **Consistent Patterns**: Same interaction patterns throughout the app
- **Helpful Defaults**: EU standards pre-filled, but adjustable

---

## User Flow

### Primary User Journey

```
┌─────────────┐
│  Home Page  │
│  - Welcome  │
│  - Overview │
└──────┬──────┘
       │ Click "Get Started"
       ▼
┌──────────────────────────────────┐
│    Room Selection Page           │
│  ┌────────────┬────────────────┐ │
│  │  Saaty     │  Environmental │ │
│  │  Sliders   │  Thresholds    │ │
│  │  (Left)    │  (Right)       │ │
│  └────────────┴────────────────┘ │
│         │                         │
│         ▼ Click "Evaluate Rooms"  │
│  ┌────────────────────────────┐  │
│  │    Room Rankings Table     │  │
│  │  - Scores & Badges         │  │
│  │  - Expandable Breakdowns   │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘
```

### Secondary Flows

**API Documentation Flow:**
```
Navigation → "API Docs" → Swagger UI Page
```

**Preference Adjustment Flow:**
```
Rankings → Unsatisfied → Adjust Sliders → Re-evaluate → New Rankings
```

---

## Pages & Components

### 1. Home Page (`HomePage.jsx`)

**Purpose:** Landing page introducing the system

**Key Elements:**
- Hero section with title and description
- "Get Started" call-to-action button
- Feature highlights (EU standards, AHP algorithm, real-time data)

**User Actions:**
- Click "Get Started" → Navigate to Room Selection page

---

### 2. Room Selection Page (`RoomSelection.jsx`)

**Purpose:** Main interface for selecting rooms based on preferences

#### Layout Structure

```
┌────────────────────────────────────────────────────────┐
│                     Page Header                        │
│                  "Room Selection"                      │
├───────────────────────┬────────────────────────────────┤
│                       │                                │
│   Preference Matrix   │   Profile Adjuster             │
│   (Saaty Sliders)     │   (Environmental Thresholds)   │
│                       │                                │
│  - Comfort↔Health     │  - Temperature: [====|===]     │
│    [====|========]    │  - CO2: [====|=========]       │
│                       │  - Humidity: [====|====]       │
│  - Comfort↔Usability  │  - Noise: [====|=======]       │
│    [=====|=======]    │  - Light: [====|=======]       │
│                       │                                │
│  - Health↔Usability   │  [Reset Button]                │
│    [====|========]    │                                │
│                       │  Profile Summary:              │
│  Weights:             │  ✓ Temp: ≤24°C                 │
│  • Comfort: 40%       │  ✓ CO2: ≤600 ppm               │
│  • Health: 35%        │  • Humidity: ≤65%              │
│  • Usability: 25%     │                                │
│                       │                                │
│  CR: 0.05 ✓ Consistent│                               │
└───────────────────────┴────────────────────────────────┘
│              [Evaluate Rooms Button]                   │
├────────────────────────────────────────────────────────┤
│                  Room Rankings Table                   │
│                                                        │
│  Rank │ Room   │ Score │ Temp │ CO2  │ Humid │ ...   │
│  ───────────────────────────────────────────────────  │
│   🥇  │ MSA... │ 92%   │ ✓23°C│ ✓695 │ ✓50%  │ [Show]│
│   🥈  │ MSA... │ 88%   │ ✓23°C│ ✓702 │ ✓50%  │ [Show]│
│   🥉  │ MSA... │ 85%   │ ✓23°C│ ✓703 │ ✓50%  │ [Show]│
│                                                        │
└────────────────────────────────────────────────────────┘
```

#### Left Panel: Preference Matrix

**Component:** `PreferenceMatrix.jsx`

**Purpose:** Collect user's pairwise comparisons using Saaty scale (1-9)

**Features:**
- 3 sliders for comparing main criteria
- Real-time weight calculation
- Consistency ratio (CR) display with color coding:
  - Green (CR < 0.1): Consistent ✓
  - Yellow (CR ≥ 0.1): Inconsistent ⚠
- Visual weight distribution bars

**User Actions:**
- Drag sliders to express preferences
- View calculated weights in real-time
- Check consistency ratio

---

#### Right Panel: Profile Adjuster

**Component:** `ProfileAdjuster.jsx`

**Purpose:** Adjust environmental threshold preferences

**Features:**
- 5 sliders for environmental factors
- Visual optimal range (green background on track)
- Dynamic thumb color (green=optimal, orange=outside)
- Reset button to restore EU defaults
- Profile summary showing all thresholds

**Environmental Factors:**
1. **Temperature** (18-26°C, optimal: 20-24°C)
2. **CO2 Level** (0-1000 ppm, optimal: 0-600 ppm)
3. **Humidity** (30-70%, optimal: 40-60%)
4. **Noise Level** (0-45 dBA, optimal: 0-35 dBA)
5. **Light Level** (200-750 lux, optimal: 300-500 lux)

**User Actions:**
- Adjust sliders to set personal thresholds
- Click "Reset" to restore EU standards
- View profile summary

---

#### Evaluate Button

**Purpose:** Trigger room evaluation based on preferences

**States:**
- Default: "Evaluate Rooms" (blue, hover effect)
- Loading: "Evaluating Rooms..." (disabled, lighter blue)
- Error: Shows error message below button

---

#### Room Rankings Component

**Component:** `RoomRanking.jsx`

**Purpose:** Display ranked rooms with scores and details

**Summary Cards (Top):**
```
┌────────────┬────────────┬────────────┬────────────┐
│ Rooms      │ Consistency│ Best       │ Top        │
│ Evaluated  │ Ratio      │ Match      │ Score      │
│    10      │   0.05     │ Room 2     │   92%      │
└────────────┴────────────┴────────────┴────────────┘
```

**Rankings Table:**

| Column | Description | Visual Treatment |
|--------|-------------|------------------|
| Rank | 1-10 position | Badge (gold/silver/bronze for top 3) |
| Room Name | Room identifier | Bold text |
| Overall Score | Final weighted score | Percentage + progress bar |
| Temp | Temperature value | Badge (✓ green, ⚠ yellow, ✗ red) |
| CO2 | CO2 level | Badge (✓ green, ⚠ yellow, ✗ red) |
| Humidity | Humidity percentage | Badge (✓ green, ⚠ yellow, ✗ red) |
| Facilities | Icons for equipment | 📽️💻🤖 + seat count |
| Details | Expand button | "Show ▼" / "Hide ▲" |

**Rank Badges:**
- **🥇 Rank 1**: Gold gradient (yellow-orange)
- **🥈 Rank 2**: Silver gradient (gray)
- **🥉 Rank 3**: Bronze gradient (pink-orange)
- **Rank 4+**: Indigo blue

**Status Badges:**
- **✓ Green**: Value within optimal range
- **⚠ Yellow**: Value acceptable but outside optimal
- **✗ Red**: Value outside acceptable range

---

#### Score Breakdown Component

**Component:** `ScoreBreakdown.jsx`

**Purpose:** Show detailed score components for a room

**Triggered By:** Clicking "Show" button on any ranking row

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│ Detailed Score Breakdown                            │
├───────────────┬───────────────┬─────────────────────┤
│ Comfort Score │ Health Score  │ Usability Score     │
│     89%       │     95%       │      91%            │
│ [====    ]    │ [======   ]   │ [=====    ]         │
├───────────────┼───────────────┼─────────────────────┤
│ Temperature   │ CO2 Level     │ Humidity            │
│   23.0°C      │   695 ppm     │     50.2%           │
├───────────────┼───────────────┼─────────────────────┤
│ Air Quality   │ VOC           │ Noise Level         │
│   25.1 AQI    │   250 ppb     │     32 dBA          │
└───────────────┴───────────────┴─────────────────────┘
│ Room Facilities                                     │
│ [23 Seats] [📽️ Projector] [💻 20 Computers] [🤖 Robots]│
└─────────────────────────────────────────────────────┘
```

**Features:**
- Score breakdown by main criteria (Comfort, Health, Usability)
- Individual environmental readings
- Color-coded progress bars
- Facility badges

---

### 3. API Documentation Page (`SwaggerDocs.jsx`)

**Purpose:** Interactive API documentation

**Modes:**

**Mock Mode (Default):**
- Yellow notice explaining mock API is active
- Instructions to start backend
- List of mock endpoints
- Technology stack information

**Real API Mode:**
- Embedded Swagger UI
- Interactive "Try it out" functionality
- Full OpenAPI specification

---

## Design System

### Color Palette

```css
/* Primary Colors */
--primary-blue: #667eea       /* Main brand color */
--primary-indigo: #4f46e5     /* Buttons, links */

/* Status Colors */
--success-green: #38a169      /* Optimal values, success */
--warning-yellow: #f59e0b     /* Acceptable but not optimal */
--error-red: #e53e3e          /* Out of range, errors */
--info-blue: #3182ce         /* Information notices */

/* Neutral Colors */
--gray-50: #f7fafc           /* Background */
--gray-100: #edf2f7          /* Card backgrounds */
--gray-200: #e2e8f0          /* Borders */
--gray-600: #4a5568          /* Secondary text */
--gray-900: #1a202c          /* Primary text */

/* Gradient Badges */
--gold-gradient: linear-gradient(135deg, #f6d365 0%, #fda085 100%)
--silver-gradient: linear-gradient(135deg, #d7d2cc 0%, #304352 100%)
--bronze-gradient: linear-gradient(135deg, #ed6ea0 0%, #ec8c69 100%)
```

### Typography

**Font Family:**
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

**Font Sizes:**
- **Heading 1**: 3xl (30px) - Page titles
- **Heading 2**: 2xl (24px) - Section titles
- **Heading 3**: xl (20px) - Subsection titles
- **Body**: base (16px) - Regular text
- **Small**: sm (14px) - Labels, helper text
- **Extra Small**: xs (12px) - Badges, captions

**Font Weights:**
- **Bold**: 700 - Headings, important values
- **Semibold**: 600 - Subheadings, labels
- **Medium**: 500 - Navigation, buttons
- **Regular**: 400 - Body text

### Spacing

Uses Tailwind's spacing scale (0.25rem increments):
- `p-2` (0.5rem / 8px) - Tight padding
- `p-4` (1rem / 16px) - Default padding
- `p-6` (1.5rem / 24px) - Comfortable padding
- `p-8` (2rem / 32px) - Spacious padding

### Border Radius

- `rounded-sm`: 2px - Small elements
- `rounded`: 4px - Badges
- `rounded-md`: 6px - Buttons
- `rounded-lg`: 8px - Cards
- `rounded-full`: 50% - Circular badges, sliders

### Shadows

```css
/* Cards */
box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

/* Elevated cards */
box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);

/* Buttons on hover */
box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
```

---

## Interactive Elements

### Saaty Sliders

**Design:**
- Horizontal slider (1-9 scale)
- Labels at 0%, 25%, 50%, 75%, 100%
- Tick marks every 1 unit
- Large thumb for easy dragging

**States:**
- Default: Blue thumb
- Hover: Slightly larger thumb
- Active/Dragging: Larger thumb with shadow
- Focus: Blue ring around thumb

**Labels:**
```
Left extreme | Left moderate | Equal | Right moderate | Right extreme
     9              3            1          3                 9
```

### Range Sliders (Environmental Thresholds)

**Design:**
- Horizontal slider with optimal range indicator
- Green background shows optimal range
- Dynamic thumb color (green=optimal, orange=outside)
- Current value displayed above slider

**Visual Feedback:**
```
Temperature Slider (18°C - 26°C)
                    ▼ 22°C ✓
[====|████████████|========]
 18°C   optimal    24°C  26°C
      20-24°C
```

### Buttons

**Primary Button (Evaluate Rooms):**
```css
background: #4f46e5
hover: #4338ca
padding: 1rem 2rem
border-radius: 8px
font-weight: 600
```

**States:**
- Default: Indigo background
- Hover: Darker indigo + scale(1.05)
- Active: Even darker
- Disabled: Light indigo, no hover effect
- Loading: Light indigo + spinner

**Secondary Button (Reset):**
```css
background: #edf2f7
hover: #e2e8f0
color: #4a5568
```

---

## Responsive Design

### Breakpoints

```css
/* Mobile */
@media (min-width: 640px) { ... }   /* sm */

/* Tablet */
@media (min-width: 768px) { ... }   /* md */

/* Desktop */
@media (min-width: 1024px) { ... }  /* lg */

/* Large Desktop */
@media (min-width: 1280px) { ... }  /* xl */
```

### Layout Adaptations

**Room Selection Page:**

**Desktop (≥1024px):**
```
┌────────────────┬────────────────┐
│  Saaty         │  Environmental │
│  Sliders       │  Thresholds    │
│  (50%)         │  (50%)         │
└────────────────┴────────────────┘
```

**Tablet/Mobile (<1024px):**
```
┌────────────────────────────────┐
│  Saaty Sliders                 │
│  (100% width)                  │
└────────────────────────────────┘
┌────────────────────────────────┐
│  Environmental Thresholds      │
│  (100% width, stacked below)   │
└────────────────────────────────┘
```

**Rankings Table:**

**Desktop:** Full table with all columns

**Tablet:** Slightly condensed, smaller fonts

**Mobile:**
- Horizontal scroll enabled
- Priority columns shown (Rank, Room, Score)
- Other columns scrollable

---

## Accessibility

### Keyboard Navigation

**Sliders:**
- `Tab`: Focus next slider
- `Shift+Tab`: Focus previous slider
- `Arrow Left/Right`: Adjust value
- `Home/End`: Min/max value

**Buttons:**
- `Tab`: Focus next button
- `Enter/Space`: Activate button

**Table:**
- `Tab`: Navigate through interactive elements
- `Enter`: Expand/collapse breakdown

### Screen Reader Support

**ARIA Labels:**
```jsx
<button aria-label="Evaluate rooms based on preferences">
  Evaluate Rooms
</button>

<input
  type="range"
  aria-label="Temperature threshold, current value 22 degrees Celsius"
  aria-valuemin="18"
  aria-valuemax="26"
  aria-valuenow="22"
/>
```

**Semantic HTML:**
- `<nav>` for navigation
- `<main>` for main content
- `<table>` with `<thead>` and `<tbody>` for data tables
- `<button>` for interactive elements (not `<div>` with click handlers)

### Color Contrast

All text meets WCAG AA standards:
- Regular text: 4.5:1 contrast ratio
- Large text (18px+): 3:1 contrast ratio
- Interactive elements: Clear focus indicators

---

## User Testing

### Test Scenarios

**Scenario 1: First-time User**
1. Land on home page
2. Click "Get Started"
3. See sliders with default values
4. Click "Evaluate Rooms" without adjustments
5. View rankings
6. Understand results

**Expected:** User should understand system without instructions

**Scenario 2: Preference Adjustment**
1. User wants rooms with strict CO2 limits
2. Adjust CO2 slider to 500 ppm
3. Prioritize Health in Saaty sliders
4. Re-evaluate
5. See different rankings

**Expected:** Rankings should change, reflecting user's health priority

**Scenario 3: Understanding Results**
1. View rankings table
2. Click "Show" on top-ranked room
3. See detailed breakdown
4. Understand why room ranked #1

**Expected:** Breakdown clearly shows which factors contributed

### Usability Metrics

**Task Success Rate:** Can users successfully evaluate rooms?
- Target: >90% success rate

**Time on Task:** How long to complete first evaluation?
- Target: <2 minutes for first-time users

**Error Rate:** Do users make mistakes?
- Target: <5% error rate (e.g., inconsistent preferences)

**Satisfaction:** Would users recommend the system?
- Target: >4/5 satisfaction score

---

## Future Improvements

### Planned Enhancements

1. **Save Preferences**: Allow users to save and load preference profiles
2. **Room Comparison**: Side-by-side comparison of 2-3 rooms
3. **Historical Data**: Show room trends over time
4. **Mobile App**: Native iOS/Android app
5. **Calendar Integration**: Show room availability in real-time
6. **Booking**: Direct booking from rankings

### Known Limitations

1. **No User Accounts**: Currently no login/authentication
2. **No Persistence**: Preferences lost on page refresh
3. **No Booking**: Can only view rankings, not book rooms
4. **No Calendar**: Doesn't check if room is available
5. **Mock API**: Full features require backend integration

---

## References

- [Tailwind CSS v4 Documentation](https://tailwindcss.com/docs)
- [React Router Documentation](https://reactrouter.com/)
- [Lucide React Icons](https://lucide.dev/)
- [WCAG Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [EU IEQ Standards (EN 16798-1)](https://www.en-standard.eu/bs-en-16798-1-2019-energy-performance-of-buildings-ventilation-for-buildings-indoor-environmental-input-parameters-for-design-and-assessment-of-energy-performance-of-buildings-addressing-indoor-air-quality-thermal-environment-lighting-and-acoustics-module-m1-6/)

---

**Document Version:** 1.0
**Last Updated:** 2025-12-20
**Author:** Filip Zekonja
