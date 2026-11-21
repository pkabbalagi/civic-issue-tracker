# CivicTrack AI

CivicTrack AI is a full-stack civic grievance and infrastructure management platform. Citizens can register reports, upload photos, provide geolocation, track complaint progress, and view an interactive public complaint map. Administrators can review AI classifications, assign departments, update statuses, and add resolution notes.

## Features

- Citizen registration and login
- Administrator authentication and management dashboard
- Civic complaint submission with image uploads
- Browser geolocation support
- AI-assisted category, severity, department, and summary analysis
- Automatic fallback analysis when Gemini API credentials are unavailable
- Complaint status and resolution tracking
- Public complaint statistics and charts
- Interactive Leaflet and OpenStreetMap complaint map
- Category and status filtering
- SQLite persistence
- Responsive desktop and mobile interface

## Technology Stack

### Frontend

- React.js
- Vite
- React Router
- Leaflet and React Leaflet
- Recharts
- Lucide React
- Custom responsive CSS

### Backend

- Python 3.11+
- Flask
- Flask-CORS
- Flask-SQLAlchemy
- SQLite
- Pillow
- Google Generative AI SDK

## Project Structure

```text
AI/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── civictrack.db
│   ├── uploads/
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── spec.md
└── README.md
```

## Prerequisites

- Windows 10 or 11
- Python 3.11 or newer
- Node.js 18 or newer
- npm
- Git

## Local Setup on Windows

Open Command Prompt in the project root:

```cmd
cd c:\Users\lenovo\Desktop\AI
```

### 1. Configure Python Virtual Environment

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
```

### 2. Configure Environment Variables

Create `backend\.env` or set variables in Command Prompt.

```cmd
set GEMINI_API_KEY=your_gemini_api_key
set SECRET_KEY=replace-with-a-long-random-secret
set ADMIN_EMAIL=admin@civictrack.local
set ADMIN_PASSWORD=Admin@123
```

A Gemini key is optional. Without it, CivicTrack uses built-in fallback classification.

### 3. Start the Flask Backend

In a terminal with the virtual environment active:

```cmd
cd c:\Users\lenovo\Desktop\AI
.venv\Scripts\activate
python backend\app.py
```

The backend will run at:

```text
http://localhost:5000
```

Test the API health endpoint:

```text
http://localhost:5000/api/health
```

### 4. Start the React Frontend

Open a second Command Prompt:

```cmd
cd c:\Users\lenovo\Desktop\AI\frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## Default Administrator Account

If no administrator account is configured, the backend creates this default account:

```text
Email: admin@civictrack.local
Password: Admin@123
```

Change the administrator password immediately for deployment. Set `ADMIN_PASSWORD` before starting the backend.

## Gemini AI Configuration

Set `GEMINI_API_KEY` before starting Flask:

```cmd
set GEMINI_API_KEY=your_api_key
python backend\app.py
```

Gemini is used to analyze complaint text and uploaded images. If the API is missing or a request fails, the application safely falls back to local keyword and category analysis.

## Main API Routes

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| POST | `/api/auth/register` | Register a citizen |
| POST | `/api/auth/login` | Authenticate a user |
| GET | `/api/auth/me` | Return the authenticated user |
| GET | `/api/complaints` | List and filter complaints |
| GET | `/api/complaints/<id>` | View complaint details |
| POST | `/api/complaints` | Create a complaint |
| PATCH | `/api/complaints/<id>` | Update an complaint; administrator only |
| GET | `/api/dashboard` | Public dashboard statistics |
| GET | `/uploads/<filename>` | Retrieve an uploaded image |

## Production Build

Build the frontend:

```cmd
cd c:\Users\lenovo\Desktop\AI\frontend
npm run build
```

The generated production files are written to `frontend\dist`.

## Deployment Notes

- Set strong `SECRET_KEY`, `ADMIN_PASSWORD`, and `GEMINI_API_KEY` values.
- Never commit `.env`, API keys, database files, or uploaded citizen information.
- SQLite is suitable for local development and demos. Use a managed database for production.
- Deploy the React frontend to Vercel or another static host.
- Deploy the Flask backend to Render or another Python host.
- Update frontend API URLs and CORS settings for the production domains.
- Use HTTPS and secure storage for authentication tokens in a production environment.

## Security

- Passwords are hashed before storage.
- Protected API routes require bearer tokens.
- Administrative updates require an administrator role.
- Uploaded files are restricted to JPG, JPEG, PNG, and WEBP formats.
- The upload request size is limited to 30 MB.
- Location access requires browser permission.
- AI output is advisory and should be verified by an administrator.

## GitHub Setup

```cmd
cd c:\Users\lenovo\Desktop\AI
git add README.md
git commit -m "Add project README"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git branch -M main
git push -u origin main
```

## License

Add an appropriate license before public deployment or release.
