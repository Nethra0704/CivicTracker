# 🚦 CivicTracker
### AI-Powered Civic Issue Reporting, Road Infrastructure Monitoring & Safe Journey Platform

CivicTracker is an intelligent civic technology platform designed to bridge the gap between citizens and municipal authorities. It enables people to report road infrastructure problems, analyze their severity using AI-assisted techniques, monitor issue resolution, and plan safer journeys.

The platform combines **Artificial Intelligence, Geographic Information Systems (GIS), Web Development, and Civic Engagement** to create a smarter and safer urban environment.

---

## 🌟 Key Features

### 1. 🛣️ Smart Road Issue Reporting
- Report potholes, road cracks, waterlogging, open manholes, broken guardrails and streetlight failures.
- Upload images of damaged infrastructure.
- Pinpoint issue locations using an interactive map.
- Automatically identify geographical locations through reverse geocoding.

### 2. 🤖 AI-Assisted Severity Assessment
- Analyze reported road issues using image texture and edge-based analysis.
- Evaluate contextual descriptions using heuristic NLP techniques.
- Generate severity scores and priority classifications.
- Categorize reports into High, Medium and Low priority levels.

### 3. 🗺️ Interactive GIS Dashboard
- Interactive maps powered by Leaflet.js and OpenStreetMap.
- Visualize reported road hazards using severity-based markers.
- Detect current location using browser GPS permissions.
- View issue details, images, severity and resolution status.

### 4. 🏛️ Authority Management Portal
- Dedicated dashboard for municipal authorities.
- View and manage citizen-submitted complaints.
- Update issue statuses: Pending, In Progress and Completed.
- Maintain timestamped authority response notes.

### 5. 🚗 Safe Journey Planner
- Calculate routes between selected locations.
- Identify reported hazards along the route.
- Analyze road safety risks using nearby issue reports.
- Display route information, estimated traffic and toll information where available.
- Support safer alternative route suggestions.

### 6. 👥 Citizen Engagement
- Public civic issue feed.
- Community comments and discussions.
- Citizen reporting and issue tracking.
- Improved transparency between citizens and authorities.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python, Flask |
| Database | SQLite3 |
| Mapping | Leaflet.js, OpenStreetMap |
| Geocoding | Nominatim |
| Routing | OSRM |
| AI Analysis | Python, Pillow, heuristic NLP |
| API Integration | Google Gemini API adapter |
| Testing | Python, Flask Test Client |

---

## 🏗️ Project Architecture

```text
CivicTracker/
│
├── app.py
├── models.py
├── ai_engine.py
├── route_engine.py
├── seed_data.py
├── requirements.txt
├── README.md
│
├── static/
│   ├── css/
│   │   ├── main.css
│   │   ├── components.css
│   │   └── map.css
│   │
│   ├── js/
│   │   ├── main.js
│   │   ├── map-utils.js
│   │   ├── feed.js
│   │   ├── report.js
│   │   ├── authority.js
│   │   └── planner.js
│   │
│   └── uploads/
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   ├── report.html
│   ├── report_detail.html
│   ├── authority.html
│   └── journey_planner.html
│
├── test_app.py
├── test_live_server.py
├── run.bat
├── run.ps1
├── test.bat
└── test.ps1
```

---

## ⚙️ Installation and Setup

### Prerequisites
- Python 3.10 or later
- Git
- A modern web browser

### 1. Clone the Repository

```bash
git clone https://github.com/Nethra0704/CivicTracker.git
```

### 2. Navigate to the Project

```bash
cd CivicTracker
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Application

Windows PowerShell:

```powershell
.\run.ps1
```

Alternatively:

```bash
python app.py
```

### 7. Open in Browser

```text
http://127.0.0.1:5000
```

---

## 🧪 Testing

Run the application test suite using:

```powershell
.\test.ps1
```

Alternatively:

```bash
python test_app.py
```

---

## 🌍 Mapping and Location Services

CivicTracker uses open-source mapping technologies:

- **Leaflet.js:** Interactive map visualization.
- **OpenStreetMap:** Map tiles and geographical data.
- **Nominatim:** Location search and reverse geocoding.
- **OSRM:** Route calculation and navigation data.

The mapping implementation does not require a paid Google Maps API key.

---

## 🎯 Project Objectives

- Improve communication between citizens and civic authorities.
- Encourage faster identification of road infrastructure problems.
- Use AI-assisted analysis to prioritize critical road hazards.
- Improve commuter awareness of potentially unsafe routes.
- Promote transparent and technology-driven civic management.

---

## 🔮 Future Enhancements

- Advanced deep learning models for road damage detection.
- Real-time AI image classification.
- Mobile application integration.
- Live traffic data integration.
- Government authority API integration.
- Push notifications for issue updates.
- Community-based report verification.

---

## 👩‍💻 Developed By

**Nethra K**

B.E. Computer Science and Engineering (Internet of Things)

Sri Krishna College of Engineering and Technology (SKCET)

Coimbatore, Tamil Nadu, India.

**GitHub:** https://github.com/Nethra0704

---

## 📌 Project Information

**Project Name:** CivicTracker

**Domain:** Artificial Intelligence | Smart Cities | Civic Technology | Road Safety

**Category:** Full-Stack Web Application

**Development Status:** Prototype

---

*Building smarter roads and safer communities through technology.* 🚦
