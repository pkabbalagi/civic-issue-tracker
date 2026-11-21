import os
import uuid
import datetime

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'civictrack.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(base_dir, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 30 * 1024 * 1024
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-this-secret-in-production')
db = SQLAlchemy(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='citizen', nullable=False)

class Complaint(db.Model):
    id = db.Column(db.String(20), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(30), default='Submitted', nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    address = db.Column(db.String(250))
    image_url = db.Column(db.String(250))
    ai_summary = db.Column(db.Text)
    ai_source = db.Column(db.String(30), default='Fallback')
    resolution_note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

with app.app_context():
    db.create_all()

    # Upgrade databases created by the earlier version without dropping existing data.
    connection = db.engine.raw_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("PRAGMA table_info(complaint)")
        complaint_columns = {row[1] for row in cursor.fetchall()}
        if 'user_id' not in complaint_columns:
            cursor.execute("ALTER TABLE complaint ADD COLUMN user_id INTEGER")
        if 'ai_source' not in complaint_columns:
            cursor.execute("ALTER TABLE complaint ADD COLUMN ai_source VARCHAR(30) DEFAULT 'Fallback'")
        connection.commit()
    finally:
        connection.close()

    admin_email = os.getenv('ADMIN_EMAIL', 'admin@civictrack.local')
    admin_password = os.getenv('ADMIN_PASSWORD', 'Admin@123')
    if not db.session.scalar(db.select(User).where(User.email == admin_email)):
        db.session.add(User(name='CivicTrack Administrator', email=admin_email,
                            password_hash=generate_password_hash(admin_password), role='admin'))
        db.session.commit()

CATEGORIES = {
    'Pothole': ('Roads Department', 'High'),
    'Garbage': ('Sanitation Department', 'Medium'),
    'Water Leakage': ('Water Supply Department', 'High'),
    'Streetlight': ('Electrical Department', 'Medium'),
    'Drainage': ('Drainage Department', 'High'),
    'Pollution': ('Pollution Control Board', 'Critical'),
    'Public Property': ('Public Works Department', 'Medium'),
    'Other': ('Municipal Services', 'Low')
}

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

def bearer_user():
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return None
    try:
        payload = serializer.loads(auth[7:], max_age=7 * 24 * 3600)
        return db.session.get(User, payload['uid'])
    except (BadSignature, SignatureExpired, KeyError):
        return None

def auth_required(role=None):
    user = bearer_user()
    if not user:
        return None, (jsonify({'error': 'Authentication required'}), 401)
    if role and user.role != role:
        return None, (jsonify({'error': 'Administrator access required'}), 403)
    return user, None

def analyze_with_gemini(description, category, image_path=None):
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return fallback_analysis(description, category)
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            'Analyze this civic complaint. Return only valid JSON with keys category, severity, department, summary. '
            'Category must be Pothole, Garbage, Water Leakage, Streetlight, Drainage, Pollution, Public Property or Other. '
            'Severity must be Critical, High, Medium or Low. '
            f'Description: {description or "No description"}. Selected category: {category}. '
            'The summary should be concise and in English.'
        )
        if image_path:
            from PIL import Image
            image = Image.open(image_path)
            response = model.generate_content([prompt, image])
        else:
            response = model.generate_content(prompt)
        import json
        parsed = json.loads(response.text.strip().replace('```json', '').replace('```', '').strip())
        cat = parsed.get('category') if parsed.get('category') in CATEGORIES else (category if category in CATEGORIES else 'Other')
        sev = parsed.get('severity') if parsed.get('severity') in ('Critical', 'High', 'Medium', 'Low') else 'Low'
        dept = parsed.get('department') or CATEGORIES[cat][0]
        return cat, sev, dept, parsed.get('summary') or description[:160], 'Gemini'
    except Exception:
        return fallback_analysis(description, category)

def fallback_analysis(description, category):
    text = (description or '').lower()
    cat = category if category in CATEGORIES else 'Other'
    dept, severity = CATEGORIES[cat]
    if any(word in text for word in ('accident', 'burst', 'fire', 'danger', 'major', 'blocked', 'electrocution')):
        severity = 'Critical'
    elif any(word in text for word in ('large', 'deep', 'leak', 'injury', 'continuous')):
        severity = 'High'
    summary = description[:160] if description else f'{cat} reported in the area.'
    return cat, severity, dept, summary, 'Fallback'

@app.get('/api/health')
def health():
    return jsonify({'status': 'ok'})

@app.post('/api/auth/register')
def register():
    data = request.get_json(silent=True) or {}
    name = str(data.get('name', '')).strip()
    email = str(data.get('email', '')).strip().lower()
    password = str(data.get('password', ''))
    if len(name) < 2:
        return jsonify({'error': 'Enter your full name'}), 400
    if '@' not in email or '.' not in email:
        return jsonify({'error': 'Enter a valid email address'}), 400
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    if db.session.scalar(db.select(User).where(User.email == email)):
        return jsonify({'error': 'An account already exists with this email'}), 409
    user = User(name=name, email=email, password_hash=generate_password_hash(password), role='citizen')
    db.session.add(user)
    db.session.commit()
    token = serializer.dumps({'uid': user.id})
    return jsonify({'token': token, 'user': user_dict(user)}), 201

@app.post('/api/auth/login')
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get('email', '')).strip().lower()
    password = str(data.get('password', ''))
    user = db.session.scalar(db.select(User).where(User.email == email))
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid email or password'}), 401
    token = serializer.dumps({'uid': user.id})
    return jsonify({'token': token, 'user': user_dict(user)})

@app.get('/api/auth/me')
def me():
    user, error = auth_required()
    if error:
        return error
    return jsonify({'user': user_dict(user)})

@app.get('/api/complaints')
def list_complaints():
    category = request.args.get('category')
    status = request.args.get('status')
    search = request.args.get('search', '').strip().lower()
    mine = request.args.get('mine') == 'true'
    query = Complaint.query
    if mine:
        user, error = auth_required()
        if error:
            return error
        query = query.filter_by(user_id=user.id)
    if category and category != 'All':
        query = query.filter_by(category=category)
    if status and status != 'All':
        query = query.filter_by(status=status)
    items = query.order_by(Complaint.created_at.desc()).all()
    result = [to_dict(item) for item in items]
    if search:
        result = [item for item in result if search in ' '.join(str(item.get(key, '')) for key in ('id', 'title', 'description', 'category', 'address', 'department')).lower()]
    return jsonify(result)

@app.get('/api/complaints/<complaint_id>')
def detail(complaint_id):
    complaint = db.session.get(Complaint, complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404
    return jsonify(to_dict(complaint))

@app.post('/api/complaints')
def create():
    user, error = auth_required()
    if error:
        return error
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    if len(title) < 5:
        return jsonify({'error': 'Title must be at least 5 characters'}), 400
    if len(description) < 10:
        return jsonify({'error': 'Description must be at least 10 characters'}), 400
    category = request.form.get('category', 'Other')
    if category not in CATEGORIES:
        category = 'Other'
    image_url = None
    saved_image_path = None
    file = request.files.get('image')
    if file and file.filename:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            return jsonify({'error': 'Only JPG, PNG and WEBP images are accepted'}), 400
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filename = f'{uuid.uuid4().hex}{ext}'
        saved_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(saved_image_path)
        from PIL import Image
        try:
            with Image.open(saved_image_path) as image:
                image.verify()
        except Exception:
            os.remove(saved_image_path)
            return jsonify({'error': 'The uploaded file is not a valid image'}), 400
        image_url = f'/uploads/{filename}'
    category, severity, department, summary, source = analyze_with_gemini(description, category, saved_image_path)
    complaint_id = 'CT-' + uuid.uuid4().hex[:8].upper()
    complaint = Complaint(id=complaint_id, user_id=user.id, title=title, description=description,
                          category=category, severity=severity, department=department,
                          latitude=parse_float(request.form.get('latitude')), longitude=parse_float(request.form.get('longitude')),
                          address=request.form.get('address', '').strip() or None, image_url=image_url,
                          ai_summary=summary, ai_source=source)
    db.session.add(complaint)
    db.session.commit()
    return jsonify(to_dict(complaint)), 201

@app.patch('/api/complaints/<complaint_id>')
def update(complaint_id):
    user, error = auth_required('admin')
    if error:
        return error
    complaint = db.session.get(Complaint, complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404
    data = request.get_json(silent=True) or {}
    if 'status' in data:
        if data['status'] not in ('Submitted', 'In Progress', 'Resolved', 'Closed'):
            return jsonify({'error': 'Invalid status'}), 400
        complaint.status = data['status']
    if 'department' in data:
        complaint.department = str(data['department']).strip() or complaint.department
    if 'severity' in data:
        if data['severity'] in ('Critical', 'High', 'Medium', 'Low'):
            complaint.severity = data['severity']
    if 'category' in data:
        if data['category'] in CATEGORIES:
            complaint.category = data['category']
    if 'resolution_note' in data:
        complaint.resolution_note = str(data['resolution_note']).strip()
    db.session.commit()
    return jsonify(to_dict(complaint))

@app.get('/api/dashboard')
def dashboard():
    items = Complaint.query.all()
    categories = {category: 0 for category in CATEGORIES}
    severities = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
    statuses = {'Submitted': 0, 'In Progress': 0, 'Resolved': 0, 'Closed': 0}
    for complaint in items:
        categories[complaint.category] = categories.get(complaint.category, 0) + 1
        severities[complaint.severity] = severities.get(complaint.severity, 0) + 1
        statuses[complaint.status] = statuses.get(complaint.status, 0) + 1
    return jsonify({'total': len(items),
                    'pending': sum(statuses[key] for key in ('Submitted', 'In Progress')),
                    'resolved': statuses['Resolved'] + statuses['Closed'],
                    'categories': categories, 'severities': severities, 'statuses': statuses})

@app.get('/uploads/<filename>')
def uploaded(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def parse_float(value):
    try:
        parsed = float(value)
        return parsed if -90 <= parsed <= 90 else None if 'lat' in str(value).lower() else parsed
    except (TypeError, ValueError):
        return None

def user_dict(user):
    return {'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role}

def to_dict(complaint):
    owner = db.session.get(User, complaint.user_id) if complaint.user_id else None
    return {'id': complaint.id, 'title': complaint.title, 'description': complaint.description,
            'category': complaint.category, 'severity': complaint.severity, 'department': complaint.department,
            'status': complaint.status, 'latitude': complaint.latitude, 'longitude': complaint.longitude,
            'address': complaint.address, 'imageUrl': complaint.image_url, 'aiSummary': complaint.ai_summary,
            'aiSource': complaint.ai_source, 'resolutionNote': complaint.resolution_note,
            'citizenName': owner.name if owner else None, 'createdAt': complaint.created_at.isoformat() if complaint.created_at else None}

@app.errorhandler(413)
def too_large(_error):
    return jsonify({'error': 'The uploaded file exceeds the 30 MB limit'}), 413

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
