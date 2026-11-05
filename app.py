import os
import uuid
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, send_from_directory
)
from werkzeug.utils import secure_filename
from models import (
    init_db, verify_user, create_user, get_user_by_id, get_user_by_username,
    create_report, get_all_reports, get_report_by_id, get_reports_by_user,
    update_report_status, get_report_stats, add_comment, get_comments_by_report,
    get_authority_updates, save_route_history, get_user_route_history
)
from ai_engine import get_ai_engine
from route_engine import plan_safe_journey

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'civictrack-ai-secure-platform-secret-2026')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif', 'svg', 'mp4', 'mov', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Context processor for templates
@app.context_processor
def inject_user():
    user = None
    if 'user_id' in session:
        user = get_user_by_id(session['user_id'])
    return {'current_user': user}

# Auth Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def authority_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access the Authority portal.', 'warning')
            return redirect(url_for('login', next=request.url))
        role = session.get('role')
        if role not in ['Authority', 'Admin']:
            flash('Access denied. Authority privileges required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# PAGE ROUTES
# ==========================================

@app.route('/')
def index():
    reports = get_all_reports(limit=9)
    stats = get_report_stats()
    return render_template('index.html', reports=reports, stats=stats)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = verify_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash(f"Welcome back, {user['username']}! Logged in as {user['role']}.", 'success')
            
            next_url = request.args.get('next')
            if next_url:
                return redirect(next_url)
            if user['role'] in ['Authority', 'Admin']:
                return redirect(url_for('authority_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
            
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    role = request.form.get('role', 'Citizen')
    
    if not username or not password:
        flash('Username and password are required.', 'danger')
        return redirect(url_for('login'))
        
    if role not in ['Citizen', 'Authority']:
        role = 'Citizen'
        
    existing = get_user_by_username(username)
    if existing:
        flash('Username already exists. Please pick another one.', 'danger')
        return redirect(url_for('login'))
        
    user_id = create_user(username, password, role)
    if user_id:
        session['user_id'] = user_id
        session['username'] = username
        session['role'] = role
        flash(f'Account created successfully! Welcome to CivicTrack-AI, {username}.', 'success')
        return redirect(url_for('authority_dashboard') if role == 'Authority' else url_for('dashboard'))
    else:
        flash('Failed to create account. Please try again.', 'danger')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    my_reports = get_reports_by_user(user_id)
    stats = get_report_stats()
    route_history = get_user_route_history(user_id, limit=5)
    return render_template('dashboard.html', my_reports=my_reports, stats=stats, route_history=route_history)

@app.route('/report', methods=['GET', 'POST'])
@login_required
def report_issue():
    if request.method == 'POST':
        description = request.form.get('description', '').strip()
        location_name = request.form.get('location_name', '').strip()
        lat_str = request.form.get('latitude', '')
        lon_str = request.form.get('longitude', '')
        category = request.form.get('category', 'Pothole')
        
        if not description or not location_name or not lat_str or not lon_str:
            flash('Please fill in description, location name, and pinpoint on the map.', 'danger')
            return redirect(url_for('report_issue'))
            
        try:
            latitude = float(lat_str)
            longitude = float(lon_str)
        except ValueError:
            flash('Invalid coordinates provided.', 'danger')
            return redirect(url_for('report_issue'))
            
        # File handling
        image_path = '/static/uploads/pothole_crater.svg' # default
        sample_choice = request.form.get('sample_image')
        
        if 'media_file' in request.files and request.files['media_file'].filename != '':
            file = request.files['media_file']
            if file and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                unique_name = f"report_{uuid.uuid4().hex[:10]}.{ext}"
                save_dest = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
                file.save(save_dest)
                image_path = f"/static/uploads/{unique_name}"
        elif sample_choice:
            image_path = f"/static/uploads/{sample_choice}"
            
        # AI Engine Analysis
        ai_engine = get_ai_engine()
        # local disk path for AI engine inspection
        local_img_path = os.path.join(BASE_DIR, image_path.lstrip('/'))
        analysis = ai_engine.analyze(local_img_path, description, category)
        
        report_id = create_report(
            user_id=session['user_id'],
            image_path=image_path,
            description=description,
            location_name=location_name,
            latitude=latitude,
            longitude=longitude,
            priority=analysis['priority'],
            status='Pending',
            severity_score=analysis['severity_score'],
            confidence_score=analysis['confidence_score'],
            category=category
        )
        
        flash(f"Report submitted successfully! CivicTrack-AI classified this as {analysis['priority']} Priority ({analysis['confidence_score']}% confidence).", 'success')
        return redirect(url_for('report_detail', report_id=report_id))
        
    return render_template('report.html')

@app.route('/report/<int:report_id>')
def report_detail(report_id):
    report = get_report_by_id(report_id)
    if not report:
        flash('Report not found.', 'danger')
        return redirect(url_for('index'))
        
    comments = get_comments_by_report(report_id)
    updates = get_authority_updates(report_id)
    return render_template('report_detail.html', report=report, comments=comments, updates=updates)

@app.route('/authority')
@authority_required
def authority_dashboard():
    priority_filter = request.args.get('priority', 'All')
    status_filter = request.args.get('status', 'All')
    search_query = request.args.get('search', '').strip()
    
    reports = get_all_reports(priority=priority_filter, status=status_filter, search=search_query, limit=100)
    stats = get_report_stats()
    return render_template('authority.html', reports=reports, stats=stats,
                           active_priority=priority_filter, active_status=status_filter,
                           search_query=search_query)

@app.route('/journey-planner')
def journey_planner():
    recent_searches = get_user_route_history(session.get('user_id'), limit=5)
    return render_template('journey_planner.html', recent_searches=recent_searches)

# ==========================================
# REST API ENDPOINTS
# ==========================================

@app.route('/api/reports', methods=['GET'])
def api_get_reports():
    priority = request.args.get('priority')
    status = request.args.get('status')
    search = request.args.get('search')
    reports = get_all_reports(priority=priority, status=status, search=search, limit=100)
    return jsonify({'success': True, 'count': len(reports), 'reports': reports})

@app.route('/api/reports/<int:report_id>', methods=['GET'])
def api_get_single_report(report_id):
    report = get_report_by_id(report_id)
    if not report:
        return jsonify({'success': False, 'error': 'Not found'}), 404
    comments = get_comments_by_report(report_id)
    updates = get_authority_updates(report_id)
    return jsonify({
        'success': True,
        'report': report,
        'comments': comments,
        'authority_updates': updates
    })

@app.route('/api/reports/<int:report_id>/comments', methods=['GET', 'POST'])
def api_report_comments(report_id):
    if request.method == 'POST':
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Unauthorized. Please login.'}), 401
            
        data = request.get_json(silent=True) or request.form
        comment_text = data.get('comment', '').strip()
        if not comment_text:
            return jsonify({'success': False, 'error': 'Comment cannot be empty'}), 400
            
        comment_id = add_comment(report_id, session['user_id'], comment_text)
        comments = get_comments_by_report(report_id)
        return jsonify({
            'success': True,
            'comment_id': comment_id,
            'message': 'Comment posted successfully',
            'comments': comments
        })
        
    comments = get_comments_by_report(report_id)
    return jsonify({'success': True, 'comments': comments})

@app.route('/api/reports/<int:report_id>/status', methods=['POST'])
@authority_required
def api_update_status(report_id):
    data = request.get_json(silent=True) or request.form
    new_status = data.get('status')
    response_notes = data.get('notes', '').strip()
    
    if new_status not in ['Pending', 'In Progress', 'Completed']:
        return jsonify({'success': False, 'error': 'Invalid status'}), 400
        
    success = update_report_status(
        report_id=report_id,
        new_status=new_status,
        authority_id=session['user_id'],
        response_notes=response_notes
    )
    
    if success:
        return jsonify({'success': True, 'message': f'Status updated to {new_status}'})
    return jsonify({'success': False, 'error': 'Report not found'}), 404

@app.route('/api/journey/plan', methods=['POST'])
def api_plan_journey():
    data = request.get_json(silent=True) or request.form
    start_loc = data.get('start_location', '').strip()
    dest_loc = data.get('destination', '').strip()
    
    if not start_loc or not dest_loc:
        return jsonify({'success': False, 'error': 'Start location and destination are required'}), 400
        
    result = plan_safe_journey(start_loc, dest_loc, session.get('user_id'))
    
    # Save to route history
    save_route_history(
        user_id=session.get('user_id'),
        start_location=result['start_location'],
        destination=result['destination'],
        safety_level=result['safety_level'],
        travel_time=result['travel_time'],
        toll_count=result['toll_count'],
        traffic_level=result['traffic_level'],
        distance=f"{result['distance_km']} km"
    )
    
    return jsonify({'success': True, 'plan': result})

@app.route('/api/ai/analyze-preview', methods=['POST'])
def api_ai_preview():
    data = request.get_json(silent=True) or request.form
    description = data.get('description', '')
    category = data.get('category', 'Pothole')
    sample_image = data.get('sample_image')
    
    image_path = None
    if sample_image:
        image_path = os.path.join(UPLOAD_FOLDER, sample_image)
        
    ai = get_ai_engine()
    analysis = ai.analyze(image_path, description, category)
    return jsonify({'success': True, 'analysis': analysis})

@app.route('/api/stats', methods=['GET'])
def api_get_stats():
    return jsonify({'success': True, 'stats': get_report_stats()})

if __name__ == '__main__':
    init_db()
    print("=" * 60)
    print("🚦 CivicTrack-AI - Civic Infrastructure Platform Launching")
    print("Serving on http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=True)
