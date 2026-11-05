# 🚦 CivicTrack-AI
### AI-Powered Civic Road Infrastructure Monitoring & Safe Journey Platform

---

## 🌟 Overview

**CivicTrack-AI** is an intelligent civic road infrastructure monitoring and smart commuter safety platform. It bridges the gap between road users and municipal authorities by combining:

1. **Crowdsourced Hazard Reporting:** Citizens report potholes, waterlogging, open manholes, broken guardrails, and lighting outages with automatic reverse geocoding and interactive map pin-dropping.
2. **AI-Driven Severity Assessment:** Computer vision texture/edge analysis and contextual NLP evaluate the structural risk of reported defects, assigning confidence-backed priority levels (`High`, `Medium`, `Low`).
3. **OpenStreetMap GIS Telemetry:** Interactive Leaflet.js map with official OpenStreetMap tiles centered on Coimbatore, Tamil Nadu (11.0168, 76.9558), featuring a **"Detect My Location"** GPS trigger.
4. **Severity-Based Road Issue Markers:**
   - 🔴 **Red:** High severity
   - 🟠 **Orange:** Medium severity
   - 🟡 **Yellow:** Low severity
   - 🟢 **Green:** Resolved / Completed reports
5. **Closed-Loop Authority Governance:** A dedicated municipal portal enables state PWD and city traffic departments to track, triage, and update defect statuses (`Pending`, `In Progress`, `Completed`) with timestamped audit notes.
6. **Safe Journey Planner:** Commuters calculate driving routes between any two points. The platform scans a 1.2 km buffer corridor along the route, correlates reported hazards, and displays safety risk levels, traffic estimations, toll costs, and safer alternative bypasses.

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | HTML5, Modern CSS3 (Dark Glassmorphic Cyber Theme), Vanilla JavaScript (ES6+) |
| **Backend** | Python Flask (RESTful Architecture, Session Auth) |
| **Database** | SQLite3 with Foreign Keys & Constraint Checking |
| **Maps & GIS** | Leaflet.js with official OpenStreetMap tiles (`https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`), Nominatim Geocoding, OSRM Routing Engine (No paid Google Maps API keys required) |
| **AI Severity Engine** | Modular Vision & NLP Analyzer (`Pillow` Texture/Edge variance + Heuristic Semantics) + Google Gemini API Multi-Modal Adapter Hook |
| **Icons & Fonts** | FontAwesome 6, Plus Jakarta Sans, JetBrains Mono |

---

## 📂 Project Architecture

```
roadintel-ai/
├── app.py                  # Flask Application, routing, sessions, RESTful APIs
├── models.py               # SQLite Schema, ORM helpers, auth, queries
├── ai_engine.py            # Modular AI priority engine (Heuristic CV + Gemini Adapter)
├── route_engine.py         # Safe Journey Planner, corridor buffer & risk calculation
├── seed_data.py            # Database initializer & generator for realistic road hazard SVG graphics
├── test_app.py             # End-to-end test suite
├── run.bat / run.ps1       # 1-Click launcher scripts for Flask server
├── test.bat / test.ps1     # 1-Click launcher scripts for test suite
├── requirements.txt        # Python dependencies
├── README.md               # Documentation & user guide
│
├── static/
│   ├── css/
│   │   ├── main.css        # Dark theme, layout, hero, typography, gradients
│   │   ├── components.css  # Cards, buttons, badges, tables, comments, modals
│   │   └── map.css         # Leaflet styling, severity markers, route polyline
│   ├── js/
│   │   ├── main.js         # Alerts, toasts, modals, demo credential helpers
│   │   ├── map-utils.js    # Leaflet OpenStreetMap engine, GPS tracking, markers & popups
│   │   ├── feed.js         # Dynamic feed rendering, live filtering, AJAX comments
│   │   ├── report.js       # Media upload, sample presets, click-to-pin, AI preview
│   │   ├── authority.js    # Authority dashboard status updater & response notes
│   │   └── planner.js      # Safe Journey Planner, route geometry & hazard overlay
│   └── uploads/            # Uploaded photos & realistic road hazard visuals
│
└── templates/
    ├── base.html           # Universal layout, dark navbar, footer, about modal
    ├── index.html          # Hero section, platform KPIs, GIS hazard map & live feed
    ├── login.html          # Glassmorphic auth card, role selector, demo autofill
    ├── dashboard.html      # Citizen dashboard, live map widget, user reports, recent journeys
    ├── report.html         # Multi-modal report form with live AI diagnostic preview
    ├── report_detail.html  # High-res photo, AI diagnostic card, authority logs, comments
    ├── authority.html      # Authority command center, filterable table, status modal
    └── journey_planner.html# Interactive route map, corridor hazards, tolls, traffic
```

---

## 🗺️ Map & GPS Implementation Details

### 1. OpenStreetMap Integration
- **Official OSM Tile Layer:** `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`
- **Zero Paid Dependencies:** No Google Maps API key required.
- **Center:** Default center set to **Coimbatore, Tamil Nadu (`11.0168, 76.9558`)**.
- **Interactive Controls:** Zoom in/out buttons, mouse dragging, touch pinch-to-zoom, and scroll wheel navigation.
- **Responsive Layout:** Automatically scales on mobile and desktop viewports, with dynamic `invalidateSize()` listeners.

### 2. Severity Marker Color Legend
- 🔴 **Red Pin:** High Priority (`priority = 'High'`)
- 🟠 **Orange Pin:** Medium Priority (`priority = 'Medium'`)
- 🟡 **Yellow Pin:** Low Priority (`priority = 'Low'`)
- 🟢 **Green Pin:** Resolved / Repaired Defect (`status = 'Completed'`)

### 3. Marker Click Popups
Every marker displays:
- **Report ID** (`#1`)
- **Road Issue Type** (Category, e.g., Pothole, Waterlogging)
- **Severity** (Priority level and 0–100 score)
- **Description** (Citizen-submitted details)
- **Location** (Human-readable locality name)
- **Report Status** (`Pending`, `In Progress`, `Completed`)
- **Uploaded Image** (Thumbnail image preview)

### 4. "Detect My Location" Feature
- Prominent button on the map toolbar: **"Detect My Location"**.
- Queries browser `navigator.geolocation` API with high accuracy mode.
- Centers map to the user's coordinates with zoom level 15, drops a glowing pulsing location marker, reverse geocodes the street address, and handles permission denials gracefully.

---

## ⚙️ Setup & Execution Instructions

### 1. Run via Quick Scripts (Easiest)
In your PowerShell or Command Prompt inside the project folder:
```powershell
.\run.ps1
```
*(or double-click `run.bat`)*

### 2. Run the Test Suite
```powershell
.\test.ps1
```
*(or run `python test_app.py`)*

### 3. Re-seed the Database (Optional)
```powershell
python seed_data.py
```

### 4. Open the Web Application
Open your browser and navigate to:  
👉 **`http://127.0.0.1:5000`**

---

## 🔑 Pre-Seeded Demo Accounts

| Role | Username | Password | Access Capabilities |
| :--- | :--- | :--- | :--- |
| **Citizen** | `citizen1` | `password123` | Report hazards, plan journeys, comment on feeds |
| **Authority** | `authority_pwd` | `admin123` | Access Authority Portal, update defect status & notes |
| **Admin** | `admin` | `admin123` | Full system access across all portals |

*(Use the 1-click demo buttons on `/login` for instantaneous access!)*
