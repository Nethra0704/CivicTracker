"""
CivicTrack-AI - Database Seeder & Realistic Vector Graphic Generator
Generates sample road defects in Coimbatore, Tamil Nadu and across India.
"""

import os
from models import init_db, create_user, create_report, add_comment, update_report_status, save_route_history

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Generate high quality SVGs representing road hazards
SAMPLE_IMAGES = {
    'pothole_crater.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="100%" height="100%">
  <defs>
    <linearGradient id="road" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1f2937"/>
      <stop offset="100%" stop-color="#111827"/>
    </linearGradient>
    <radialGradient id="hole" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#030712"/>
      <stop offset="70%" stop-color="#1f2937"/>
      <stop offset="100%" stop-color="#374151"/>
    </radialGradient>
    <linearGradient id="warningG" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ef4444"/>
      <stop offset="100%" stop-color="#b91c1c"/>
    </linearGradient>
  </defs>
  <rect width="800" height="500" fill="url(#road)"/>
  <!-- Lane markings -->
  <line x1="0" y1="250" x2="180" y2="250" stroke="#fbbf24" stroke-width="8" stroke-dasharray="25,15"/>
  <line x1="620" y1="250" x2="800" y2="250" stroke="#fbbf24" stroke-width="8" stroke-dasharray="25,15"/>
  <!-- Pothole crater -->
  <ellipse cx="400" cy="270" rx="190" ry="110" fill="url(#hole)" stroke="#0f172a" stroke-width="6"/>
  <path d="M 240 250 Q 280 200 370 210 Q 480 190 560 260 Q 530 330 420 360 Q 270 340 240 250 Z" fill="#090d16" opacity="0.9"/>
  <!-- Fractures and cracks -->
  <path d="M 230 240 L 160 210 L 120 230" stroke="#4b5563" stroke-width="4" fill="none"/>
  <path d="M 570 270 L 660 300 L 710 280" stroke="#4b5563" stroke-width="4" fill="none"/>
  <path d="M 410 370 L 430 430 L 400 460" stroke="#4b5563" stroke-width="4" fill="none"/>
  <!-- AI Detection Box Overlay -->
  <rect x="190" y="160" width="420" height="230" fill="none" stroke="#ef4444" stroke-width="2.5" stroke-dasharray="8,4" rx="10"/>
  <rect x="190" y="125" width="230" height="32" fill="url(#warningG)" rx="6"/>
  <text x="202" y="147" fill="#ffffff" font-family="Arial, sans-serif" font-weight="bold" font-size="14">AI: CRITICAL POTHOLE 96.4%</text>
  <text x="400" y="470" fill="#9ca3af" font-family="sans-serif" font-size="14" text-anchor="middle">CivicTrack-AI Vision Telemetry • Avinashi Road</text>
</svg>''',

    'waterlogging_flood.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="100%" height="100%">
  <defs>
    <linearGradient id="waterSky" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="#1e293b"/>
    </linearGradient>
    <linearGradient id="waterFlow" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0284c7" stop-opacity="0.8"/>
      <stop offset="50%" stop-color="#0369a1" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#0c4a6e" stop-opacity="0.95"/>
    </linearGradient>
  </defs>
  <rect width="800" height="500" fill="url(#waterSky)"/>
  <!-- Submerged highway -->
  <polygon points="0,200 800,200 800,500 0,500" fill="#1e293b"/>
  <!-- Water body layer -->
  <path d="M 0 240 Q 200 220 400 245 T 800 230 L 800 500 L 0 500 Z" fill="url(#waterFlow)"/>
  <path d="M 0 290 Q 250 270 500 295 T 800 280 L 800 500 L 0 500 Z" fill="#0284c7" opacity="0.3"/>
  <!-- Submerged divider reflection -->
  <line x1="400" y1="200" x2="400" y2="350" stroke="#e0f2fe" stroke-width="4" opacity="0.6" stroke-dasharray="10,10"/>
  <!-- AI Detection Tag -->
  <rect x="220" y="160" width="360" height="260" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="6,4" rx="8"/>
  <rect x="220" y="125" width="230" height="32" fill="#0284c7" rx="6"/>
  <text x="232" y="147" fill="#ffffff" font-family="sans-serif" font-weight="bold" font-size="14">AI: SEVERE WATERLOGGING</text>
  <text x="400" y="475" fill="#bae6fd" font-family="sans-serif" font-size="13" text-anchor="middle">Depth &gt; 25cm • Gandhipuram Underpass</text>
</svg>''',

    'open_manhole.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="100%" height="100%">
  <rect width="800" height="500" fill="#111827"/>
  <circle cx="400" cy="250" r="130" fill="#000000" stroke="#dc2626" stroke-width="8"/>
  <circle cx="400" cy="250" r="100" fill="#030712"/>
  <!-- Warning Barricade strip -->
  <rect x="200" y="240" width="400" height="20" fill="#facc15" stroke="#000" stroke-width="2"/>
  <polygon points="200,240 230,240 210,260 180,260" fill="#000"/>
  <polygon points="260,240 290,240 270,260 240,260" fill="#000"/>
  <polygon points="320,240 350,240 330,260 300,260" fill="#000"/>
  <polygon points="380,240 410,240 390,260 360,260" fill="#000"/>
  <polygon points="440,240 470,240 450,260 420,260" fill="#000"/>
  <polygon points="500,240 530,240 510,260 480,260" fill="#000"/>
  <!-- Detection Box -->
  <rect x="210" y="100" width="380" height="300" fill="none" stroke="#ef4444" stroke-width="3" rx="12"/>
  <rect x="210" y="65" width="220" height="32" fill="#ef4444" rx="6"/>
  <text x="222" y="87" fill="#ffffff" font-family="sans-serif" font-weight="bold" font-size="14">AI: OPEN MANHOLE HAZARD</text>
  <text x="400" y="450" fill="#f87171" font-family="sans-serif" font-weight="bold" font-size="14" text-anchor="middle">FATAL RISK FOR TWO-WHEELERS</text>
</svg>''',

    'broken_guardrail.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="100%" height="100%">
  <rect width="800" height="500" fill="#18181b"/>
  <!-- Road pavement -->
  <polygon points="100,500 250,200 550,200 700,500" fill="#27272a"/>
  <!-- Broken metallic guardrail -->
  <path d="M 80 400 L 220 280 L 320 290 L 390 380 L 460 260 L 680 370" stroke="#a1a1aa" stroke-width="14" fill="none"/>
  <circle cx="390" cy="380" r="16" fill="#f59e0b"/>
  <!-- Detection box -->
  <rect x="180" y="210" width="380" height="210" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="6,4" rx="10"/>
  <rect x="180" y="175" width="240" height="32" fill="#f59e0b" rx="6"/>
  <text x="192" y="197" fill="#000000" font-family="sans-serif" font-weight="bold" font-size="13">AI: STRUCTURAL BARRIER IMPACT</text>
  <text x="400" y="470" fill="#a1a1aa" font-family="sans-serif" font-size="14" text-anchor="middle">Western Express Highway • Guardrail Breach</text>
</svg>''',

    'road_cracks.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="100%" height="100%">
  <rect width="800" height="500" fill="#1e293b"/>
  <!-- Alligator cracking network -->
  <path d="M 200 150 L 310 220 L 280 340 L 400 370 L 490 260 L 580 310 L 640 210" stroke="#0f172a" stroke-width="8" fill="none"/>
  <path d="M 310 220 L 420 240 L 490 260 L 460 160 L 340 180" stroke="#0f172a" stroke-width="6" fill="none"/>
  <path d="M 280 340 L 350 420 L 470 410 L 400 370" stroke="#0f172a" stroke-width="7" fill="none"/>
  <!-- Detection Box -->
  <rect x="160" y="120" width="510" height="320" fill="none" stroke="#3b82f6" stroke-width="2.5" stroke-dasharray="8,4" rx="10"/>
  <rect x="160" y="85" width="240" height="32" fill="#3b82f6" rx="6"/>
  <text x="172" y="107" fill="#ffffff" font-family="sans-serif" font-weight="bold" font-size="13">AI: ALLIGATOR FATIGUE CRACKING</text>
  <text x="400" y="475" fill="#94a3b8" font-family="sans-serif" font-size="13" text-anchor="middle">Outer Ring Road • Subsurface Failure Risk</text>
</svg>''',

    'streetlight_outage.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="100%" height="100%">
  <rect width="800" height="500" fill="#030712"/>
  <!-- Dark road with single moon glint -->
  <line x1="400" y1="200" x2="400" y2="500" stroke="#374151" stroke-width="4" stroke-dasharray="20,15"/>
  <!-- Lamppost without light -->
  <path d="M 600 500 L 600 150 Q 600 90 530 90 L 510 90" stroke="#475569" stroke-width="8" fill="none"/>
  <ellipse cx="500" cy="95" rx="20" ry="10" fill="#1e293b" stroke="#64748b" stroke-width="2"/>
  <!-- AI warning -->
  <rect x="150" y="150" width="300" height="150" fill="none" stroke="#8b5cf6" stroke-width="2" stroke-dasharray="6,4" rx="8"/>
  <rect x="150" y="115" width="220" height="32" fill="#7c3aed" rx="6"/>
  <text x="162" y="137" fill="#ffffff" font-family="sans-serif" font-weight="bold" font-size="13">AI: ILLUMINATION OUTAGE</text>
  <text x="400" y="460" fill="#6b7280" font-family="sans-serif" font-size="14" text-anchor="middle">DB Road, RS Puram, Coimbatore • Dark Blindspot</text>
</svg>'''
}

def seed_database():
    print("Initializing Database schema for CivicTrack-AI...")
    init_db()

    # 1. Create sample SVG image files
    for filename, svg_content in SAMPLE_IMAGES.items():
        filepath = os.path.join(UPLOADS_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(svg_content)
    print("Sample road issue visuals generated in static/uploads/.")

    # 2. Create Users
    users_data = [
        ('citizen1', 'password123', 'Citizen'),
        ('arun_kumar', 'password123', 'Citizen'),
        ('priya_sharma', 'password123', 'Citizen'),
        ('authority_pwd', 'admin123', 'Authority'),
        ('traffic_commissioner', 'admin123', 'Authority'),
        ('admin', 'admin123', 'Admin')
    ]
    
    user_ids = {}
    for username, pwd, role in users_data:
        uid = create_user(username, pwd, role)
        if uid:
            user_ids[username] = uid
        else:
            from models import get_user_by_username
            user = get_user_by_username(username)
            if user:
                user_ids[username] = user['id']

    print(f"Users created/verified: {list(user_ids.keys())}")

    # 3. Create Sample Reports (Centered on Coimbatore, Tamil Nadu & Metro Corridors)
    reports_seed = [
        # Coimbatore Defects (All 4 colors: Red, Orange, Yellow, Green)
        {
            'user_id': user_ids.get('citizen1', 1),
            'image_path': '/static/uploads/pothole_crater.svg',
            'description': 'Massive 18cm deep crater across the middle lane right after Peelamedu signal on Avinashi Road. Extremely dangerous for two-wheelers during peak traffic.',
            'location_name': 'Avinashi Road near Peelamedu, Coimbatore',
            'latitude': 11.0285,
            'longitude': 77.0015,
            'priority': 'High',
            'status': 'Pending',
            'severity_score': 94,
            'confidence_score': 96.4,
            'category': 'Pothole'
        },
        {
            'user_id': user_ids.get('arun_kumar', 2),
            'image_path': '/static/uploads/waterlogging_flood.svg',
            'description': 'Severe knee-deep waterlogging near Cross Cut Road, Gandhipuram underpass causing vehicle stalling and severe traffic congestion.',
            'location_name': 'Cross Cut Road, Gandhipuram, Coimbatore',
            'latitude': 11.0182,
            'longitude': 76.9635,
            'priority': 'Medium',
            'status': 'In Progress',
            'severity_score': 68,
            'confidence_score': 92.1,
            'category': 'Waterlogging'
        },
        {
            'user_id': user_ids.get('priya_sharma', 3),
            'image_path': '/static/uploads/streetlight_outage.svg',
            'description': 'Multiple high-mast street lights out of service creating a hazardous dark pedestrian crossing along DB Road.',
            'location_name': 'DB Road, RS Puram, Coimbatore',
            'latitude': 11.0092,
            'longitude': 76.9490,
            'priority': 'Low',
            'status': 'Pending',
            'severity_score': 32,
            'confidence_score': 88.0,
            'category': 'Streetlight Outage'
        },
        {
            'user_id': user_ids.get('citizen1', 1),
            'image_path': '/static/uploads/pothole_crater.svg',
            'description': 'Pavement collapse near Singanallur bus terminus on Trichy Road. Repaired and verified by local municipal engineers.',
            'location_name': 'Trichy Road near Singanallur, Coimbatore',
            'latitude': 11.0012,
            'longitude': 77.0210,
            'priority': 'Medium',
            'status': 'Completed',
            'severity_score': 60,
            'confidence_score': 93.5,
            'category': 'Pothole'
        },
        {
            'user_id': user_ids.get('priya_sharma', 3),
            'image_path': '/static/uploads/open_manhole.svg',
            'description': 'Open stormwater drain manhole with missing cast iron cover. Only a thin tree branch has been placed as a warning marker.',
            'location_name': '100 Feet Road, Koramangala 4th Block, Bengaluru',
            'latitude': 12.9348,
            'longitude': 77.6251,
            'priority': 'High',
            'status': 'In Progress',
            'severity_score': 98,
            'confidence_score': 98.7,
            'category': 'Open Manhole'
        },
        {
            'user_id': user_ids.get('citizen1', 1),
            'image_path': '/static/uploads/broken_guardrail.svg',
            'description': 'Crash barrier collapsed and bent into traffic lane following an overnight collision. Sharp jagged metal edges exposed.',
            'location_name': 'Western Express Highway near Andheri East, Mumbai',
            'latitude': 19.1172,
            'longitude': 72.8550,
            'priority': 'Medium',
            'status': 'Completed',
            'severity_score': 65,
            'confidence_score': 89.1,
            'category': 'Broken Guardrail'
        },
        {
            'user_id': user_ids.get('arun_kumar', 2),
            'image_path': '/static/uploads/road_cracks.svg',
            'description': 'Extensive alligator fatigue cracking along the outer slow lane. Asphalt is peeling off creating loose gravel and skidding hazards.',
            'location_name': 'Outer Ring Road (ORR) Gachibowli, Hyderabad',
            'latitude': 17.4401,
            'longitude': 78.3489,
            'priority': 'Medium',
            'status': 'Pending',
            'severity_score': 54,
            'confidence_score': 87.5,
            'category': 'Road Crack'
        }
    ]

    report_ids = []
    for r in reports_seed:
        rid = create_report(
            user_id=r['user_id'],
            image_path=r['image_path'],
            description=r['description'],
            location_name=r['location_name'],
            latitude=r['latitude'],
            longitude=r['longitude'],
            priority=r['priority'],
            status=r['status'],
            severity_score=r['severity_score'],
            confidence_score=r['confidence_score'],
            category=r['category']
        )
        report_ids.append(rid)

    print(f"Created {len(report_ids)} initial road issue reports.")

    # 4. Add comments and authority updates
    auth_uid = user_ids.get('authority_pwd', 4)
    cit_uid = user_ids.get('citizen1', 1)

    if report_ids:
        # Report 1 (Avinashi Road) comments
        add_comment(report_ids[0], cit_uid, "I noticed two bikes almost lose balance over this crater this morning! Please repair urgently.")
        add_comment(report_ids[0], auth_uid, "Official Note: Coimbatore Municipal Corporation Highway Division has dispatched an inspection unit. Warning cones placed.")
        
        # Report 2 (Gandhipuram) authority update & comments
        update_report_status(report_ids[1], 'In Progress', authority_id=auth_uid, response_notes="High-capacity de-watering suction pumps mobilized. Stormwater drainage clearing underway.")
        add_comment(report_ids[1], auth_uid, "Suction pumps are operational. Water level receding. Normal traffic expected soon.")

        # Report 4 (Trichy Road) completion
        update_report_status(report_ids[3], 'Completed', authority_id=auth_uid, response_notes="Pavement restoration and hot-mix bituminous asphalt patching completed and cured.")
        add_comment(report_ids[3], cit_uid, "Verified on site. Road surface is smooth and repaired. Thank you!")

    # 5. Seed Route History for Coimbatore
    save_route_history(
        user_id=cit_uid,
        start_location='Gandhipuram, Coimbatore',
        destination='Peelamedu, Coimbatore',
        safety_level='Moderate Risk',
        travel_time='16 mins',
        toll_count=0,
        traffic_level='Moderate',
        distance='5.8 km'
    )
    save_route_history(
        user_id=cit_uid,
        start_location='RS Puram, Coimbatore',
        destination='Coimbatore Airport, Coimbatore',
        safety_level='Safe',
        travel_time='28 mins',
        toll_count=0,
        traffic_level='Low',
        distance='13.4 km'
    )

    print("CivicTrack-AI database seeding completed successfully.")

if __name__ == '__main__':
    seed_database()
