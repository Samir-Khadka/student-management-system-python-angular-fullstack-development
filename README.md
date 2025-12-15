# 🎓 Student Management System

A modern, full-stack web application for educational institutions to manage students, teachers, courses, and academic performance. Built with **Angular 18** and **Flask**, featuring role-based access control, AI-powered performance prediction, and a stunning glassmorphism UI.

[![Angular](https://img.shields.io/badge/Angular-18.2-red?logo=angular)](https://angular.io/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000?logo=flask)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0-green?logo=mongodb)](https://www.mongodb.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue?logo=typescript)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)

---

## ✨ Features

### 🤖 AI Performance Prediction
- Predicts student grades based on study habits, attendance, and support systems
- Identifies at-risk students requiring intervention
- Confidence scoring for predictions

### 🔐 Role-Based Access Control
- **Admin**: Full system access, manage students, teachers, and courses
- **Teacher**: View assigned courses, grade students, access analytics
- **Student**: View grades, enroll in courses, check performance predictions

### 📊 Real-Time Analytics
- Interactive dashboard with live statistics
- Grade distribution charts
- Performance trends and insights
- Top performers and students needing attention

### 📚 Comprehensive Course Management
- Create and manage courses
- Assign teachers to courses
- Student enrollment system (max 5 courses per student)
- Grading and gradebook functionality

### 🎨 Modern UI/UX
- Glassmorphism design aesthetic
- Fully responsive (mobile, tablet, desktop)
- Smooth animations and transitions
- Intuitive navigation

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: Angular 18.2.0
- **Language**: TypeScript 5.5+
- **Styling**: CSS3 (Glassmorphism)
- **HTTP Client**: Angular HttpClient
- **Routing**: Angular Router
- **State Management**: RxJS Observables

### Backend
- **Framework**: Flask 3.0.0
- **Language**: Python 3.11+
- **Database**: MongoDB 6.0+
- **Authentication**: JWT (Flask-JWT-Extended)
- **API**: RESTful
- **Validation**: Marshmallow

### Development Tools
- **Package Managers**: npm, pip
- **Version Control**: Git
- **API Testing**: Postman
- **Code Editor**: VS Code

---

## 🚀 Quick Start

### Prerequisites

Ensure you have the following installed:
- **Node.js** 20.x or higher ([Download](https://nodejs.org/))
- **Python** 3.11 or higher ([Download](https://www.python.org/))
- **MongoDB** 6.0 or higher ([Download](https://www.mongodb.com/try/download/community))
- **Git** ([Download](https://git-scm.com/))

---

### Installation

#### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Samir-Khadka/Student-Management-System.git
cd Student-Management-System
```

#### 2️⃣ Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env  # Windows
# OR
cp .env.example .env    # Linux/Mac

# Edit .env file with your configuration
notepad .env  # Windows
# OR
nano .env     # Linux/Mac
```

**Required `.env` Configuration**:
```env
MONGO_URI=mongodb://localhost:27017/student_db
JWT_SECRET_KEY=your_super_secret_key_here
JWT_ACCESS_TOKEN_EXPIRES=900
JWT_REFRESH_TOKEN_EXPIRES=2592000
FLASK_ENV=development
PORT=5001
CORS_ORIGINS=http://localhost:4200,http://localhost:8000
```

#### 3️⃣ Start MongoDB

```bash
# Windows
mongod --dbpath C:\data\db

# Linux
sudo systemctl start mongod

# Mac
brew services start mongodb-community
```

#### 4️⃣ Run Backend Server

```bash
# Make sure you're in backend/ directory with venv activated
python run.py
```

Backend should now be running on: `http://localhost:5001`

#### 5️⃣ Frontend Setup

Open a **new terminal**:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
# OR
ng serve
```

Frontend should now be running on: `http://localhost:4200`

#### 6️⃣ Access the Application

Open your browser and navigate to:
```
http://localhost:4200
```

---

## 📖 Usage Guide

### First-Time Setup

1. **Access the Application**: Navigate to `http://localhost:4200`
2. **Register an Account**: Click "Get Started" → "Register"
3. **Choose Role**: Select Admin, Teacher, or Student
4. **Login**: Use your credentials to access the dashboard

### Default Test Accounts

After running seed scripts (optional):

| Role | Username | Password |
|------|----------|----------|
| Admin | admin1 | password123 |
| Teacher | teacher1 | password123 |
| Student | student1 | password123 |

---

## 📁 Project Structure

```
Student-Management-System/
├── backend/                    # Flask backend
│   ├── app/
│   │   ├── routes/            # API endpoints
│   │   │   ├── auth.py       # Authentication routes
│   │   │   ├── students.py   # Student CRUD
│   │   │   ├── teachers.py   # Teacher CRUD
│   │   │   ├── courses.py    # Course management
│   │   │   └── analytics.py  # Analytics endpoints
│   │   ├── models/           # Data models (if using)
│   │   ├── utils/            # Helper functions
│   │   └── __init__.py       # App factory
│   ├── config/               # Configuration files
│   ├── tests/                # Backend tests
│   ├── scripts/              # Utility scripts
│   ├── .env.example          # Environment template
│   ├── requirements.txt      # Python dependencies
│   └── run.py               # Entry point
│
├── frontend/                  # Angular frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── auth/         # Authentication module
│   │   │   ├── dashboard/    # Dashboard module
│   │   │   ├── students/     # Student management
│   │   │   ├── teachers/     # Teacher management
│   │   │   ├── courses/      # Course management
│   │   │   ├── analytics/    # Analytics views
│   │   │   ├── services/     # Shared services
│   │   │   └── interceptors/ # HTTP interceptors
│   │   ├── styles.css        # Global styles
│   │   └── index.html        # Main HTML
│   ├── angular.json          # Angular configuration
│   ├── package.json          # npm dependencies
│   └── tsconfig.json         # TypeScript config
│
└── README.md                 # This file
```

---

## 🔌 API Documentation

The backend exposes 33 RESTful API endpoints organized into modules:

### Modules
- **Authentication** (4 endpoints): Register, Login, Token Refresh, Get User
- **Students** (7 endpoints): CRUD operations, Filtering, Prediction
- **Teachers** (4 endpoints): CRUD operations
- **Courses** (10 endpoints): CRUD, Enrollment, Grading, Student Management
- **Analytics** (6 endpoints): Statistics, At-risk students, Performance insights
- **Student Profile** (3 endpoints): View/Update profile, Predictions

**Full API Documentation**: See `backend/postman_collection.json` or import into Postman

**Base URL**: `http://localhost:5001/api`

**Authentication**: JWT Bearer Token (include in headers)
```
Authorization: Bearer <your_access_token>
```

---

## 👥 User Roles & Permissions

### 🔴 Admin
- ✅ Full access to all features
- ✅ Manage students (CRUD)
- ✅ Manage teachers (CRUD)
- ✅ Manage courses (CRUD)
- ✅ Enroll students in courses
- ✅ View all analytics and reports

### 🟡 Teacher
- ✅ View assigned courses
- ✅ View students enrolled in their courses
- ✅ Grade students
- ✅ Access class analytics
- ❌ Cannot manage students/teachers/courses

### 🟢 Student
- ✅ View personal profile
- ✅ Enroll in courses (max 5)
- ✅ View grades
- ✅ View performance predictions
- ❌ Cannot access admin features

---

## 🧪 Testing

### Backend Testing

```bash
cd backend
pytest tests/
```

### Frontend Testing

```bash
cd frontend
ng test
```

### API Testing

Import `backend/postman_collection.json` into Postman for comprehensive API testing.

---

## 🚢 Deployment

### Production Build

**Frontend**:
```bash
cd frontend
ng build --configuration production
```
Output: `frontend/dist/` - Ready for deployment to Netlify, Vercel, etc.

**Backend**:
```bash
# Use Gunicorn for production
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 run:app
```

### Environment Variables (Production)

Update `.env` for production:
```env
FLASK_ENV=production
FLASK_DEBUG=False
JWT_SECRET_KEY=<strong_random_key>
MONGO_URI=<production_mongodb_uri>
CORS_ORIGINS=<production_frontend_url>
```

### Recommended Hosting

- **Frontend**: Vercel, Netlify, Firebase Hosting
- **Backend**: Heroku, Railway, DigitalOcean
- **Database**: MongoDB Atlas (cloud)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Samir Khadka**

- GitHub: [@Samir-Khadka](https://github.com/Samir-Khadka)
- Repository: [Student-Management-System](https://github.com/Samir-Khadka/Student-Management-System)

---

## 🙏 Acknowledgments

- Angular Team for the amazing framework
- Flask community for excellent documentation
- MongoDB for flexible data storage
- All contributors and testers

---

## 📞 Support

If you have any questions or run into issues:

1. Check the [Issues](https://github.com/Samir-Khadka/Student-Management-System/issues) page
2. Review the API documentation in `postman_collection.json`
3. Consult the inline code comments

---

## 🔮 Future Enhancements

- [ ] Real-time notifications with WebSockets
- [ ] Email notifications for grade updates
- [ ] Advanced analytics with machine learning
- [ ] File upload for assignments
- [ ] Mobile application (React Native)
- [ ] Automated testing suite
- [ ] Performance optimization and caching

---

<div align="center">

**⭐ If you find this project helpful, please consider giving it a star!**

Made with ❤️ by [Samir Khadka](https://github.com/Samir-Khadka)

</div>
