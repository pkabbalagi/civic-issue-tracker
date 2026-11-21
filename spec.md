# PROJECT SPECIFICATION SHEET

## 1. Project Name
CivicTrack AI – Smart Civic Grievance & Infrastructure Management System

## 2. Track
Track 1: Civic Pulse, Digital Governance & Public Information

## 3. Selected Problem Statement
Transparent Civic Grievance & Infrastructure Triage System.

## 4. Problem Description
Citizens face difficulties reporting civic problems such as damaged roads, water leakage, garbage accumulation, pollution and broken streetlights.

Traditional complaint systems often lack transparency, proper tracking and efficient prioritization.

## 5. Proposed Solution
Develop an AI-powered web application that allows citizens to report civic problems using images, videos, audio or text.

The AI analyses complaints, identifies the issue, estimates its severity and helps route it to the appropriate authority.

A public dashboard displays complaints, their status and completed resolutions.

## 6. Technology Stack

### Frontend
- React.js – Build the user interface.
- HTML5 – Web page structure.
- Tailwind CSS – Responsive styling.
- JavaScript – Frontend functionality.
- Leaflet.js – Interactive complaint maps.

### Backend
- Python – Backend programming.
- Flask – REST API development.
- Flask-CORS – Frontend-backend communication.

### Artificial Intelligence
- Google Gemini API – Analyse complaint descriptions and uploaded images.
- AI Image Analysis – Identify potholes, garbage, water leakage and other infrastructure problems.
- NLP – Understand complaint descriptions.
- AI Severity Classification – Categorize complaints as Low, Medium, High or Critical.
- AI Classification – Identify the complaint category and suggest the responsible department.

### Database
- SQLite – Store complaints and user information.
- SQLAlchemy – Database management.

### Image and File Processing
- Pillow – Image processing.
- Python – File validation and processing.

### Location Services
- Browser Geolocation API – Capture complaint location with user permission.
- OpenStreetMap – Map data.
- Leaflet.js – Display complaint locations.

### Development Tools
- VS Code – Code editor.
- Git and GitHub – Version control.
- Postman – API testing.
- Vercel – Frontend deployment.
- Render – Backend deployment.

## 7. Main Features

### 1. Citizen Complaint Registration
- Register civic problems.
- Upload images or videos.
- Add complaint descriptions.
- Capture location.
- Select complaint category.

### 2. AI-Based Complaint Analysis
- Analyse uploaded images.
- Identify the type of civic issue.
- Generate a short complaint summary.
- Estimate complaint severity.
- Suggest the responsible department.

### 3. Automatic Complaint Prioritization
Classify complaints into:
- Critical
- High
- Medium
- Low

Prioritization should consider the issue type, visible damage and potential public impact.

### 4. Complaint Tracking
- Generate a unique complaint ID.
- Display complaint status.
- Show submission date.
- Track department assignment.
- Display resolution updates.

### 5. Public Dashboard
- Display total complaints.
- Show pending complaints.
- Show resolved complaints.
- Display complaint categories.
- Show severity distribution.

### 6. Interactive Complaint Map
- Display complaints on a map.
- Show the location of reported problems.
- Filter complaints by category and status.
- Allow citizens to view nearby reported issues.

### 7. Admin Dashboard
- View all submitted complaints.
- Review AI classifications.
- Assign complaints to departments.
- Update complaint status.
- Add resolution notes.

### 8. Multilingual Support
- Support English and Kannada.
- Allow citizens to submit complaints in their preferred language.
- Display AI-generated summaries in the selected language.

## 8. Application Pages

1. Home Page – Project introduction.
2. Citizen Dashboard – Submit and track complaints.
3. Report Issue – Upload images and complaint details.
4. Complaint Map – View reported civic issues.
5. Public Dashboard – View complaint statistics.
6. Admin Dashboard – Manage complaints.
7. Complaint Details – View complete complaint information.

## 9. Complaint Workflow

1. Citizen opens CivicTrack AI.
2. Citizen uploads an image or describes a civic issue.
3. System captures the location with permission.
4. Gemini AI analyses the submitted information.
5. System identifies the issue category.
6. AI estimates its severity.
7. Complaint receives a unique ID.
8. Complaint is assigned or suggested for the appropriate department.
9. Admin reviews and updates the complaint.
10. Citizen tracks the complaint until resolution.

## 10. System Architecture

Citizen
↓
React.js Frontend
↓
Python Flask Backend
↓
Gemini AI Image and Text Analysis
↓
Complaint Classification and Severity Assessment
↓
SQLite Database
↓
Admin Dashboard and Public Dashboard
↓
Complaint Tracking and Resolution

## 11. UI/UX Requirements
- Modern and professional interface.
- Responsive desktop and mobile design.
- Simple complaint submission form.
- Interactive map.
- Dashboard with statistics and charts.
- Clear complaint status indicators.
- English and Kannada language options.

## 12. Security and Reliability
- Validate uploaded files.
- Protect API keys using environment variables.
- Request location permission before capturing location.
- Prevent unauthorized admin access.
- Protect citizens' personal information.
- Allow admin verification of AI classifications.
- Do not claim a complaint has been officially submitted to a government authority unless an actual integration exists.

## 13. Expected Outcome
A functional AI-powered civic complaint management platform that helps citizens report infrastructure problems, automatically analyses complaints, prioritizes important issues and provides transparent complaint tracking through public dashboards.

## 14. Development Priority
1. Build the React frontend.
2. Develop Flask backend APIs.
3. Create SQLite database.
4. Implement complaint registration.
5. Integrate Gemini AI image and text analysis.
6. Implement severity classification.
7. Develop interactive complaint map.
8. Create citizen and admin dashboards.
9. Implement complaint tracking.
10. Test and deploy the application.