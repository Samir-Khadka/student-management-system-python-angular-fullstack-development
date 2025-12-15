# Student Management System - Technical Documentation

**Version**: 2.0.0  
**Date**: December 2025  
**Author**: Development Team  

---

# Table of Contents

1.  [Executive Summary](#1-executive-summary)
2.  [System Architecture](#2-system-architecture)
3.  [Database Schema Reference](#3-database-schema-reference)
4.  [API Reference Manual](#4-api-reference-manual)
5.  [Frontend Architecture](#5-frontend-architecture)
6.  [Security & Compliance](#6-security--compliance)
7.  [User Manual](#7-user-manual)
8.  [Installation & Operations Handbook](#8-installation--operations-handbook)
9.  [Testing & Quality Assurance](#9-testing--quality-assurance)
10. [Appendices](#10-appendices)

---

## 1. Executive Summary

### 1.1 Project Overview
The **Student Management System (SMS)** is a state-of-the-art, web-based educational administration platform designed to modernize the academic operations of schools and universities. Built upon a robust **Angular 21** frontend and a **Flask 3.0** backend, the system provides a seamless, responsive, and secure environment for managing the complex lifecycle of student data—from enrollment to grading and performance analysis.

In an era where data-driven decision-making is paramount in education, this system goes beyond simple record-keeping. It integrates advanced analytics and **AI-driven performance prediction algorithms** to identify at-risk students early, allowing educators to intervene pro-actively rather than reactively.

### 1.2 Core Objectives
The primary objectives of the SMS are:
1.  **Digital Transformation**: Eliminate paper-based grading and manual enrollment processes, reducing administrative overhead by approximately 60%.
2.  **Real-Time Transparency**: Provide students and parents with immediate access to academic progress, attendance records, and course materials.
3.  **Scalability & Security**: Deliver a cloud-ready architecture capable of handling thousands of concurrent users while maintaining strict data privacy standards (GDPR/FERPA compliance ready).
4.  **Academic Intelligence**: Utilize historical data to forecast student outcomes and optimize curriculum sizing.

### 1.3 Scope of the System
The application covers the following functional domains:
*   **Identity Management**: Secure Role-Based Access Control (RBAC) for Administrators, Teachers, and Students.
*   **Course Administration**: Comprehensive tools for creating curricula, assigning faculty, and managing credit distributions.
*   **Enrollment Logic**: Automated workflows for student course registration, including capacity checks and conflict resolution.
*   **Assessment Engine**: A flexible grading system supporting continuous assessment (assignments, quizzes) and final examinations.
*   **Analytics Dashboard**: Visual representations of gender distribution, grade trends, and attendance correlations using Chart.js.

### 1.4 Intended Audience
This documentation is intended for:
*   **System Architects**: To understand the high-level design and integration patterns.
*   **Backend Developers**: For detailed API specifications and database schema references.
*   **Frontend Developers**: To navigate the Angular component tree and state management flows.
*   **DevOps Engineers**: For deployment strategies, containerization, and CI/CD pipelines.
*   **End Users**: Detailed guides are provided for Admins, Teachers, and Students in Section 7.


---

## 2. System Architecture

### 2.1 High-Level Architecture
The Student Management System employs a strictly decoupled **Three-Tier Architecture**, ensuring separation of concerns, maintainability, and independent scalability of varying components.

```mermaid
graph TD
    Client[Client Browser \n (Angular SPA)]
    LB[Load Balancer / Nginx]
    API[Flask REST API Server]
    DB[(MongoDB Database)]
    Auth[JWT Auth Service]

    Client -- HTTPS/JSON --> LB
    LB -- Proxy Pass --> API
    API -- Read/Write --> DB
    API -- Validate Token --> Auth
```

#### 2.1.1 Presentation Layer (Frontend)
*   **Framework**: Angular 21 (latest stable release).
*   **Paradigm**: Single Page Application (SPA) utilizing Signals and RxJS for reactive state management.
*   **Build System**: Angular CLI (Webpack/Esbuild).
*   **Styling**: Custom CSS architecture with Glassmorphism design system, utilizing CSS Variables for theming.

#### 2.1.2 Business Logic Layer (Backend)
*   **Framework**: Flask 3.0 (Python Microframework).
*   **Concurrency**: WSGI compliant, capable of running behind Gunicorn/uWSGI.
*   **API Style**: REST Level 2 (Resource-based URLs, HTTP Verbs).
*   **Modularization**: Implementation of Flask Protocols/Blueprints to segregate domain logic (Auth, Students, Courses, Analytics).

#### 2.1.3 Data Persistence Layer
*   **Database**: MongoDB 6.0 (NoSQL).
*   **Driver**: PyMongo.
*   **ODM Strategy**: Hybrid approach using Marshmallow for schema validation at the application level while leveraging MongoDB's schema-less flexibility for analytics.

### 2.2 Design Patterns & Principles

#### 2.2.1 Backend Patterns
1.  **Blueprint Pattern**: The application is divided into functional modules (`auth_bp`, `students_bp`, `courses_bp`), each containing its own routes and logic. This prevents the "Monolithic Application" anti-pattern.
2.  **Decorator Pattern**: Custom decorators like `@handle_exceptions` and `@role_required` are used extensively to separate cross-cutting concerns (error handling, authorization) from business logic.
3.  **Service/Helper Layer**: Complex logic (e.g., `predict_student_performance`) is isolated in utility modules (`student_model.py`, `auth_helper.py`) rather than cluttering route handlers.

#### 2.2.2 Frontend Patterns
1.  **Smart/Dumb Components**:
    *   **Smart Components** (e.g., `StudentsComponent`): Handle data fetching, state injection, and business logic.
    *   **Dumb Components** (e.g., `StudentCard`, `Modal`): Purely presentational, receiving data via `@Input()` and emitting events via `@Output()`.
2.  **Singleton Services**: All data services (`ApiService`, `AuthService`) are provided in `root`, ensuring a single source of truth for application state.
3.  **Interceptor Pattern**: The `AuthInterceptor` automatically manages the injection of the `Bearer` token into HTTP headers, decoupling authentication logic from feature services.

### 2.3 Technology Stack Specifications

| Component | Technology | Version | Justification |
| :--- | :--- | :--- | :--- |
| **Frontend** | Angular | 21.0.0 | Industry standard for enterprise-grade SPAs. Strong typing (TypeScript) reduces runtime errors. |
| **Language** | TypeScript | 5.9+ | Provides static analysis and interface enforcement. |
| **Backend** | Flask | 3.0.0 | Lightweight, flexible, and pythonic. Ideal for rapid API development. |
| **Language** | Python | 3.11+ | Extensive ecosystem for data science (needed for analytics/predictions). |
| **Database** | MongoDB | 6.0 | Flexible schema accommodates evolving student data structures (e.g., variable audit logs). |
| **Auth** | JWT (JSON Web Tokens) | RFC 7519 | Stateless authentication suitable for scalable REST APIs. |
| **Validation** | Marshmallow | 3.x | Powerful, declarative schema validation for Python complex data types. |


---

## 3. Database Schema Reference

### 3.1 Overview
The application uses **MongoDB**, a NoSQL document-oriented database, allowing for flexible data modeling and high performance. The database is named `student_db`.

### 3.2 Collections

#### 3.2.1 Users Collection `users`
Stores authentication credentials and global user profile data. This is the single source of truth for identity.

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `_id` | ObjectId | Yes | Unique auto-generated identifier. |
| `username` | String | Yes | Unique login identifier (Teacher ID or Student ID often used). |
| `email` | String | Yes | Unique contact email. |
| `password` | String | Yes | Bcrypt hashed password string. |
| `role` | String | Yes | Enum: `'admin'`, `'teacher'`, `'student'`. |
| `full_name` | String | No | Display name. |
| `student_id` | String | No | FK to Students collection (if role is 'student'). |
| `teacher_id` | String | No | FK to Teachers collection (if role is 'teacher'). |
| `is_active` | Boolean | Yes | Account status (default `True`). |
| `is_approved` | Boolean | Yes | Teacher approval status. `False` until Admin approves. |
| `profile_picture`| String | No | Path to uploaded image (e.g., `/static/uploads/...`). |
| `cv_url` | String | No | Path to uploaded CV (for teachers). |
| `created_at` | DateTime | Yes | Account creation timestamp. |
| `updated_at` | DateTime | Yes | Last update timestamp. |

#### 3.2.2 Students Collection `students`
Stores academic profile and performance metrics for students.

| Field | Type | Description | Validation Rules |
| :--- | :--- | :--- | :--- |
| `student_id` | String | Unique Student ID (e.g., "S001"). | Min length 1. |
| `name` | String | Full name. | Max 100 chars. |
| `age` | Integer | Age in years. | Range: 5-100. |
| `gender` | String | Gender identity. | Enum: `['Male', 'Female', 'Other']`. |
| `study_time` | Integer | Weekly self-study hours. | Range: 0-168. |
| `absences` | Integer | Total days absent. | Min: 0. |
| `parental_support`| String | Level of home support. | Enum: `['low', 'medium', 'high']`. |
| `internet_access`| Boolean | Has reliable internet at home. | - |
| `final_grade` | Integer | Aggregated performance score (0-100). | - |
| `enrolled_subjects`| Array | List of subject names. | - |

#### 3.2.3 Teachers Collection `teachers`
Stores professional details for faculty members.

| Field | Type | Description |
| :--- | :--- | :--- |
| `teacher_id` | String | Unique Teacher ID (e.g., "T001"). |
| `name` | String | Full Name. |
| `email` | String | Contact email. |
| `subject` | String | Primary subject taught (e.g., "Mathematics"). |
| `phone` | String | Contact number. |
| `qualification`| String | Highest academic degree/certification. |

#### 3.2.4 Courses Collection `courses`
Defines the curriculum entities available for enrollment.

| Field | Type | Description |
| :--- | :--- | :--- |
| `course_id` | String | Unique Course Code (e.g., "CS101"). |
| `name` | String | Course Title (e.g., "Intro to Programming"). |
| `description` | String | Brief summary of course content. |
| `credits` | Integer | Credit value (default: 50). |
| `teacher_id` | String | ID of the instructor assigned. |
| `teacher_name` | String | Cached name of the instructor. |

#### 3.2.5 Enrollments Collection `enrollments`
Junction table linking Students to Courses, storing specific performance data.

| Field | Type | Description |
| :--- | :--- | :--- |
| `student_id` | String | Reference to Student. |
| `course_id` | String | Reference to Course. |
| `course_name` | String | Cached Course Name. |
| `teacher_id` | String | Cached Teacher ID. |
| `marks` | Integer | Score achieved (0-100). Null if not yet graded. |
| `enrolled_at` | DateTime | Timestamp of enrollment. |
| `graded_at` | DateTime | Timestamp of last grade update. |


---

## 4. API Reference Manual

### 4.1 Overview
The API follows RESTful conventions. Responses are JSON.
**Base URL**: `http://localhost:5001/api/`

**Common Response Codes**:
*   `200`: Success.
*   `201`: Created.
*   `400`: Validation Error / Bad Request.
*   `401`: Unauthorized (Missing/Invalid Token).
*   `403`: Forbidden (Insufficient Role).
*   `404`: Not Found.
*   `409`: Conflict (Duplicate Resource).

### 4.2 Authentication Endpoints
**Base Path**: `/auth`

#### `POST /auth/register`
Register a new user.
*   **Body**:
    ```json
    {
        "username": "student_001",
        "password": "password123",
        "email": "student@example.com",
        "role": "student", // or "teacher"
        "student_id": "S001" // required if role is student
    }
    ```
*   **Response (201)**:
    ```json
    { "message": "User registered successfully", "user_id": "...", "username": "..." }
    ```

#### `POST /auth/login`
Authenticate specific user and retrieve access tokens.
*   **Body**:
    ```json
    { "username": "student_001", "password": "password123" }
    ```
*   **Response (200)**:
    ```json
    {
        "message": "Login successful",
        "access_token": "eyJhb...",
        "refresh_token": "eyJhb...",
        "user": { ... }
    }
    ```

#### `POST /auth/profile` (Protected)
Update user profile details.
*   **Body**: `{"full_name": "New Name", "email": "new@email.com"}`
*   **Response (200)**: `{"message": "Profile updated", "user": {...}}`

#### `POST /auth/upload-picture` (Protected)
Upload profile avatar.
*   **Format**: `multipart/form-data` with key `file`.
*   **Response (200)**: `{"profile_picture": "/static/uploads/..."}`

### 4.3 Student Endpoints
**Base Path**: `/students`

#### `POST /students/` (Admin Only)
Create a student directly.
*   **Body**: All Student fields (see Schema).
*   **Response (201)**: Created Student Object.

#### `GET /students/` (Protected)
Get list of students. Supports filtering.
*   **Header**: `Authorization: Bearer <token>`
*   **Query Params**:
    *   `gender`: Filter by gender.
    *   `min_grade`: Minimum final grade.
    *   `limit`: Pagination limit (default 100).
    *   `skip`: Pagination skip.
*   **Response (200)**: `{"students": [...], "count": 50}`

#### `GET /students/<student_id>` (Protected)
Get single student details.

#### `GET /students/predict/<student_id>` (Protected)
Get AI performance prediction.
*   **Response (200)**:
    ```json
    {
        "prediction": {
            "predicted_grade": 78.5,
            "risk_level": "low",
            "factors": { "study_impact": 12.0, "absence_penalty": 0 }
        }
    }
    ```

### 4.4 Course & Enrollment Endpoints
**Base Path**: `/courses`

#### `GET /courses/` (Protected)
List all courses.

#### `POST /courses/` (Admin Only)
Create a new course.
*   **Body**: `{"course_id": "CS101", "name": "Python 101", "teacher_id": "T001"}`

#### `POST /courses/enroll` (Protected)
Enroll a student in a course.
*   **Body**: `{"course_id": "CS101"}` (Student ID inferred from token for students).
*   **Logic**: Enforces max 5 courses per student.

#### `POST /courses/grade` (Teacher Only)
Assign marks to a student.
*   **Body**: `{"course_id": "CS101", "student_id": "S001", "marks": 85}`

### 4.5 Teacher Endpoints
**Base Path**: `/teachers`

#### `GET /teachers/` (Protected)
List all teachers.

#### `POST /teachers/` (Admin Only)
Create a teacher manually.

### 4.6 Analytics Endpoints
**Base Path**: `/analytics`

#### `GET /analytics/average_grade`
Get global average statistics.

#### `GET /analytics/at_risk_students` (Admin/Teacher)
Get students with `final_grade < 40`.

#### `GET /analytics/class_summary` (Teacher Only)
Get detailed breakdown for a teacher's classes.


---

## 5. Frontend Architecture

### 5.1 Project Structure
The frontend is built with **Angular 21** using the **Standalone Component** architecture, eliminating the need for `NgModules`.

```
src/
├── app/
│   ├── auth/                 # Authentication Pages
│   │   ├── auth.component.ts
│   │   ├── login-form/
│   │   └── register-form/
│   ├── dashboard/            # Main Authenticated Area
│   │   ├── dashboard.component.ts (Layout)
│   │   ├── overview/         # Widgets & Charts
│   │   ├── sidebar/
│   │   └── top-bar/
│   ├── students/             # Student Management
│   │   ├── students.component.ts
│   │   └── student-card/
│   ├── teachers/             # Teacher Management
│   ├── courses/              # Course Catalog & Enrollment
│   ├── analytics/            # Admin/Worker Analytics Views
│   ├── shared/               # Reusable UI Components
│   │   ├── modal/
│   │   ├── glass-card/
│   │   └── toast-notification/
│   ├── services/             # Data Access Layer
│   │   ├── api.service.ts
│   │   └── auth.service.ts
│   ├── gaurds/               # Route Protection
│   │   └── auth.guard.ts
│   └── interceptors/         # HTTP Interceptors
│       └── auth.interceptor.ts
```

### 5.2 Key Services

#### 5.2.1 `ApiService`
This singleton service acts as the bridge between the Angular client and the Flash backend. It handles all HTTP verbs and maps JSON responses to typed interfaces.
*   **Key Methods**: `getStudents()`, `enrollStudent()`, `uploadCV()`.
*   **Error Handling**: Uses RxJS `catchError` to normalize backend 4xx/5xx errors into user-friendly messages.

#### 5.2.2 `AuthService`
Manages the identity lifecycle.
*   **State**: Uses RxJS `BehaviorSubject` to hold the current `User` object, allowing components to reactively update the UI when login state changes.
*   **Persistence**: Automatically syncs the JWT token to `localStorage` to persist sessions across browser refreshes.

### 5.3 State Management
The application utilizes a hybrid state management approach:
1.  **Local State**: Managed via Angular **Signals** (`computed`, `effect`) for fine-grained reactivity within components (e.g., form validation status).
2.  **Shared State**: Global data (User Profile, Theme Preference) is managed via RxJS **Subjects** in Services.

### 5.4 Routing & Navigation
*   **Lazy Loading**: Feature routes (Dashboard, Auth) are lazy-loaded to reduce initial bundle size.
*   **Guards**:
    *   `authGuard`: Redirects unauthenticated users to `/auth`.
    *   `roleGuard`: Prevents Students from accessing Admin-only routes (e.g., `/dashboard/teachers`).


---

## 6. Security & Compliance

### 6.1 Authentication Mechanism
The system implements **Stateless JWT (JSON Web Token)** authentication to ensure scalability and security.

1.  **Login Phase**: The user sends credentials to `/auth/login`.
2.  **Verification**: The backend validates the password hash (Bcrypt).
3.  **Token Issuance**:
    *   **Access Token**: Short-lived (15 minutes). Sent in `Authorization` header.
    *   **Refresh Token**: Long-lived (7 days). Used to obtain new access tokens without re-login.
4.  **Request Flow**: The Angular `AuthInterceptor` attaches the Access Token to every API request.
5.  **Token Expiry**: If the Access Token expires (401), the frontend silently attempts to use the Refresh Token to get a new session before showing the "Session Expired" modal.

### 6.2 Data Security
*   **Password Hashing**: User passwords are **never** stored in plain text. We use `bcrypt` with a work factor of 12.
*   **Input Sanitization**:
    *   **Backend**: `Marshmallow` schemas strip unknown fields and validate types.
    *   **Frontend**: Angular's automatic XSS protection sanitizes all bound HTML.
*   **CORS Policy**: The Flask app is configured to only accept requests from the specific Angular domain (e.g., `http://localhost:4200` or production domain).

### 6.3 Authorization Matrix (RBAC)
Access to resources is strictly controlled by the `role` field in the user's JWT claim.

| Action | Student | Teacher | Admin |
| :--- | :---: | :---: | :---: |
| **Login** | ✅ | ✅ | ✅ |
| **View Own Grades** | ✅ | ❌ | ❌ |
| **Enroll in Course** | ✅ | ❌ | ✅ |
| **Grade Students** | ❌ | ✅ | ✅ |
| **Upload CV** | ❌ | ✅ | ❌ |
| **Approve Teacher** | ❌ | ❌ | ✅ |
| **Delete User** | ❌ | ❌ | ✅ |
| **View Analytics** | ✅ (Self) | ✅ (Class) | ✅ (Global) |


---

## 7. User Manual

### 7.1 Student User Guide
1.  **Dashboard Access**: Upon login, the "My Dashboard" view provides a quick summary of your GPA and upcoming classes.
2.  **Enrolling in Courses**:
    *   Navigate to **Courses** in the sidebar.
    *   Browse the catalog. Click **Enroll** on desired subjects.
    *   *Note*: You are limited to 5 active enrollments.
3.  **Viewing Grades**:
    *   Navigate to **My Grades**.
    *   View a table of all enrolled courses with current marks.
    *   Click **Analyze Performance** to see AI predictions about your future grades.

### 7.2 Teacher User Guide
1.  **Teacher Approval**:
    *   After registration, your account is "Pending".
    *   You must upload your CV via the **Profile** page.
    *   Once approved by an Admin, you will gain full access.
2.  **Course Management**:
    *   View your assigned courses under **My Classes**.
    *   Click a course to see the roster of enrolled students.
3.  **Grading Students**:
    *   Select a student from the roster.
    *   Enter the marks (0-100) and click **Save**.
    *   The student's Grade Point Average (GPA) updates instantly.

### 7.3 Administrator User Guide
1.  **User Management**:
    *   Navigate to **Pending Teachers**.
    *   Review uploaded CVs.
    *   Click **Approve** to activate a teacher's account.
2.  **System Analytics**:
    *   The **Analytics Dashboard** provides high-level metrics:
        *   *Gender Distribution*: Pie chart of student demographics.
        *   *At-Risk Report*: List of students with predicted failure (`<40%`).


---

## 8. Installation & Operations Handbook

### 8.1 Prerequisites
*   **Operating System**: Windows 10/11, macOS, or Linux.
*   **Runtime**: Node.js v18+, Python 3.11+.
*   **Database**: MongoDB 6.0+ (Installed locally or via Docker).

### 8.2 Local Development Setup
1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/organization/Student-Management-System.git
    cd Student-Management-System
    ```

2.  **Backend Configuration**:
    ```bash
    cd backend
    python -m venv venv
    # Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate
    pip install -r requirements.txt
    ```
    *   Create a `.env` file:
        ```env
        MONGO_URI=mongodb://localhost:27017/student_db
        JWT_SECRET_KEY=dev-secret-key
        PORT=5001
        ```
    *   Run the server: `python run.py`

3.  **Frontend Configuration**:
    ```bash
    cd frontend
    npm install
    npx ng serve
    ```
    *   Access the app at `http://localhost:4200`.

### 8.3 Production Deployment
1.  **Frontend Build**:
    ```bash
    ng build --configuration production
    ```
    *   Output: `dist/student-management-system/`
    *   Serve these static files via Nginx/Apache.

2.  **Backend Production Server**:
    *   Use **Gunicorn** for process management:
    ```bash
    gunicorn -w 4 -b 0.0.0.0:5001 run:app
    ```
    *   Ensure `DEBUG=False` in environment variables.


---

## 9. Testing & Quality Assurance

### 9.1 Testing Strategy
We employ a pyramid testing strategy:

1.  **Unit Tests (Backend)**:
    *   **Tool**: `pytest`
    *   **Scope**: Individual route handlers and helper functions (`predict_student_performance`).
    *   **Command**: `pytest backend/tests/`

2.  **Component Tests (Frontend)**:
    *   **Tool**: Jasmine & Karma
    *   **Scope**: Component rendering and basic user interactions.
    *   **Command**: `ng test`

3.  **Integration Tests**:
    *   **Scope**: Verifying API responses match frontend interfaces.

### 9.2 Quality Assurance Checklist
*   [ ] All new API endpoints must have corresponding Swagger documentation.
*   [ ] Frontend components must use `OnPush` change detection where possible.
*   [ ] No secrets (API Keys) commit to version control.


---

## 10. Appendices

### 10.1 Glossary
*   **JWT**: JSON Web Token. A compact, URL-safe means of representing claims to be transferred between two parties.
*   **SPA**: Single Page Application. A web app implementation that loads a single web document and updates the body content of that single document via APIs.
*   **RBAC**: Role-Based Access Control. A method of restricting network access based on the roles of individual users within an enterprise.
*   **ODM**: Object Document Mapper. A library that provides an interface between an object-oriented language and a document database (e.g., PyMongo/Marshmallow).

### 10.2 Troubleshooting Common Issues
*   **Error: "Connection Refused"**: Check if MongoDB service is running (`mongod`).
*   **Error: "CORS Policy"**: Ensure the Flask backend `CORS` configuration allows the frontend origin.
*   **Error: "Module Not Found"**: Verify the virtual environment is activated before running Python scripts.

