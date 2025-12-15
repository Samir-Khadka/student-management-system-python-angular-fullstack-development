# Student Management System - Frontend Code Documentation
## Important Code Listing (Angular 21 Application)

**Project:** Student Management System  
**Frontend Framework:** Angular 21 (Standalone Components)  
**Purpose:** Role-based educational data management and analytics platform  
**Code Coverage:** Core components, services, and configuration files

---

## Table of Contents

1. [Application Configuration & Entry Point](#1-application-configuration--entry-point)
2. [Core Services](#2-core-services)
3. [Authentication Module](#3-authentication-module)
4. [Dashboard & Overview](#4-dashboard--overview)
5. [Student Management](#5-student-management)
6. [Course Management](#6-course-management)
7. [Analytics Dashboard](#7-analytics-dashboard)
8. [Supporting Modules](#8-supporting-modules)

---

## 1. Application Configuration & Entry Point

### 1.1 Main Entry Point (`main.ts`)

```typescript
import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { App } from './app/app';

bootstrapApplication(App, appConfig)
  .catch((err) => console.error(err));
```

**Purpose:** Bootstraps the Angular application with the root `App` component and application configuration.

---

### 1.2 Application Configuration (`app.config.ts`)

```typescript
import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';

import { routes } from './app.routes';
import { authInterceptor } from './interceptors/auth.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor]))
  ]
};
```

**Key Features:**
- Configures routing system
- Registers HTTP client with authentication interceptor
- Enables global error handling

---

### 1.3 Route Configuration (`app.routes.ts`)

```typescript
import { Routes } from '@angular/router';
import { AuthComponent } from './auth/auth.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { LandingComponent } from './landing/landing.component';
import { OverviewComponent } from './dashboard/overview/overview.component';
import { StudentsComponent } from './students/students.component';
import { TeachersComponent } from './teachers/teachers.component';
import { CoursesComponent } from './courses/courses.component';
import { StudentGradesComponent } from './students/student-grades.component';
import { AnalyticsComponent } from './analytics/analytics.component';

export const routes: Routes = [
    { path: '', component: LandingComponent },
    { path: 'auth', component: AuthComponent },
    {
        path: 'dashboard',
        component: DashboardComponent,
        children: [
            { path: '', component: OverviewComponent },
            { path: 'students', component: StudentsComponent },
            { path: 'grades', component: StudentGradesComponent },
            { path: 'teachers', component: TeachersComponent },
            { path: 'courses', component: CoursesComponent },
            { path: 'analytics', component: AnalyticsComponent }
        ]
    }
];
```

**Route Structure:**
- `/` - Landing page (public)
- `/auth` - Login/Registration (public)
- `/dashboard` - Protected area with nested routes
  - `/dashboard` - Overview (default)
  - `/dashboard/students` - Student management
  - `/dashboard/courses` - Course management
  - `/dashboard/analytics` - Analytics dashboard

---

## 2. Core Services

### 2.1 Authentication Service (`services/auth.service.ts`)

```typescript
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  private apiUrl = environment.apiUrl;

  login(credentials: { username: string; password: string }) {
    return this.http.post(`${this.apiUrl}/auth/login`, credentials).pipe(
      tap((response: any) => {
        if (response.access_token) {
          localStorage.setItem('token', response.access_token);
          localStorage.setItem('user', JSON.stringify(response.user));
        }
      })
    );
  }

  register(userData: any) {
    return this.http.post(`${this.apiUrl}/auth/register`, userData);
  }

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    this.router.navigate(['/auth']);
  }

  getToken(): string | null {
    return localStorage.getItem('token');
  }

  getUser(): any {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  isAdmin(): boolean {
    const user = this.getUser();
    return user?.role === 'Admin';
  }

  isTeacher(): boolean {
    const user = this.getUser();
    return user?.role === 'Teacher';
  }

  isStudent(): boolean {
    const user = this.getUser();
    return user?.role === 'Student';
  }
}
```

**Key Responsibilities:**
- Manages user authentication (login/register/logout)
- Stores JWT tokens in localStorage
- Provides role-checking methods
- Integrates with backend authentication API

---

### 2.2 API Service (`services/api.service.ts`)

```typescript
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  // ==================== STUDENT ENDPOINTS ====================
  
  getStudents(limit: number = 100, offset: number = 0): Observable<any> {
    return this.http.get(`${this.apiUrl}/students?limit=${limit}&offset=${offset}`);
  }

  getStudent(studentId: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/students/${studentId}`);
  }

  createStudent(studentData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/students`, studentData);
  }

  updateStudent(studentId: string, studentData: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/students/${studentId}`, studentData);
  }

  deleteStudent(studentId: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/students/${studentId}`);
  }

  getStudentCourses(studentId: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/students/${studentId}/courses`);
  }

  // ==================== TEACHER ENDPOINTS ====================
  
  getTeachers(): Observable<any> {
    return this.http.get(`${this.apiUrl}/teachers`);
  }

  createTeacher(teacherData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/teachers`, teacherData);
  }

  updateTeacher(teacherId: string, teacherData: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/teachers/${teacherId}`, teacherData);
  }

  deleteTeacher(teacherId: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/teachers/${teacherId}`);
  }

  getPendingTeachers(): Observable<any> {
    return this.http.get(`${this.apiUrl}/teachers/pending`);
  }

  approveTeacher(userId: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/teachers/${userId}/approve`, {});
  }

  getTeacherCourses(username: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/teachers/${username}/courses`);
  }

  // ==================== COURSE ENDPOINTS ====================
  
  getCourses(): Observable<any> {
    return this.http.get(`${this.apiUrl}/courses`);
  }

  createCourse(courseData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/courses`, courseData);
  }

  updateCourse(courseId: string, courseData: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/courses/${courseId}`, courseData);
  }

  deleteCourse(courseId: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/courses/${courseId}`);
  }

  getCourseStudents(courseId: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/courses/${courseId}/students`);
  }

  enrollStudent(courseId: string, studentId: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/courses/${courseId}/enroll`, { student_id: studentId });
  }

  assignGrade(studentId: string, courseId: string, marks: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/courses/assign-grade`, {
      student_id: studentId,
      course_id: courseId,
      marks: marks
    });
  }

  // ==================== ANALYTICS ENDPOINTS ====================
  
  getGenderDistribution(): Observable<any> {
    return this.http.get(`${this.apiUrl}/analytics/gender-distribution`);
  }

  getPerformanceBySupport(): Observable<any> {
    return this.http.get(`${this.apiUrl}/analytics/performance-by-support`);
  }

  getInternetAccessImpact(): Observable<any> {
    return this.http.get(`${this.apiUrl}/analytics/internet-access-impact`);
  }

  getAtRiskStudents(): Observable<any> {
    return this.http.get(`${this.apiUrl}/analytics/at-risk-students`);
  }

  // ==================== FILE UPLOAD ====================
  
  uploadProfilePicture(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.apiUrl}/upload/profile-picture`, formData);
  }

  uploadCV(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.apiUrl}/upload/cv`, formData);
  }

  getProfilePictureUrl(filename: string): string {
    return `${this.apiUrl}/uploads/profile-pictures/${filename}`;
  }
}
```

**Service Coverage:**
- Student CRUD operations
- Teacher management with approval workflow
- Course management and enrollment
- Grade assignment
- Analytics data retrieval
- File upload handling

---

### 2.3 HTTP Interceptor (`interceptors/auth.interceptor.ts`)

```typescript
import { HttpInterceptorFn } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem('token');
  
  if (token) {
    req = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  }
  
  return next(req);
};
```

**Purpose:** Automatically attaches JWT token to all outgoing HTTP requests for authentication.

---

## 3. Authentication Module

### 3.1 Authentication Component (`auth/auth.component.ts`)

```typescript
import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './auth.component.html',
  styleUrls: ['./auth.component.css']
})
export class AuthComponent {
  private authService = inject(AuthService);
  private router = inject(Router);

  isLogin = true;
  isLoading = false;
  errorMessage = '';

  // Form Data
  email = '';
  password = '';
  name = '';
  role = 'Student';

  toggleMode() {
    this.isLogin = !this.isLogin;
    this.errorMessage = '';
  }

  onSubmit() {
    if (!this.email || !this.password) {
      this.errorMessage = 'Please fill in all required fields.';
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    if (this.isLogin) {
      this.authService.login({
        username: this.email,
        password: this.password
      }).subscribe({
        next: (res) => {
          this.isLoading = false;
          if (res.access_token) {
            this.router.navigate(['/dashboard']);
          }
        },
        error: (err) => {
          this.isLoading = false;
          console.error(err);
          this.errorMessage = err.error?.message || 'Login failed. Please check your credentials.';
        }
      });
    } else {
      if (!this.name) {
        this.errorMessage = 'Full name is required for registration.';
        this.isLoading = false;
        return;
      }

      const registerData = {
        username: this.email,
        password: this.password,
        role: this.role,
        name: this.name,
        full_name: this.name
      };

      this.authService.register(registerData).subscribe({
        next: (res) => {
           this.isLoading = false;
           this.isLogin = true;
           alert('Registration successful! Please log in.');
        },
        error: (err) => {
          this.isLoading = false;
          console.error(err);
          this.errorMessage = err.error?.message || 'Registration failed. Please try again.';
        }
      });
    }
  }
}
```

**Features:**
- Toggle between login and registration modes
- Form validation
- Error handling with user-friendly messages
- Automatic navigation to dashboard on successful login
- Role selection during registration (Student/Teacher/Admin)

---

## 4. Dashboard & Overview

### 4.1 Dashboard Component (`dashboard/dashboard.component.ts`)

```typescript
import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { ApiService } from '../services/api.service';
import { ProfileModalComponent } from '../profile/profile-modal.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, ProfileModalComponent],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  private authService = inject(AuthService);
  private apiService = inject(ApiService);
  private router = inject(Router);

  user: any = null;
  isSidebarCollapsed = false;
  isDropdownOpen = false;
  showProfileModal = false;

  ngOnInit() {
    this.user = this.authService.getUser();
    if (!this.user) {
      this.router.navigate(['/auth']);
    }
  }

  get isAdmin(): boolean {
    return this.authService.isAdmin();
  }

  get isTeacher(): boolean {
    return this.authService.isTeacher();
  }

  get isStudent(): boolean {
    return this.authService.isStudent();
  }

  get userInitials(): string {
    if (!this.user?.full_name) return 'U';
    return this.user.full_name.split(' ').map((n: string) => n[0]).join('').substring(0, 2).toUpperCase();
  }

  toggleSidebar() {
    this.isSidebarCollapsed = !this.isSidebarCollapsed;
  }

  toggleDropdown() {
    this.isDropdownOpen = !this.isDropdownOpen;
  }

  openProfileModal() {
    this.showProfileModal = true;
    this.isDropdownOpen = false;
  }

  closeProfileModal() {
    this.showProfileModal = false;
    this.user = this.authService.getUser();
  }

  onProfilePictureChange(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.apiService.uploadProfilePicture(file).subscribe({
        next: (res) => {
          if (res.filename) {
            const updatedUser = { ...this.user, profile_picture_url: res.filename };
            localStorage.setItem('user', JSON.stringify(updatedUser));
            this.user = updatedUser;
          }
        },
        error: (err) => console.error('Upload failed', err)
      });
    }
  }

  uploadCV(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.apiService.uploadCV(file).subscribe({
        next: (res) => {
          alert('CV uploaded successfully! Awaiting admin approval.');
        },
        error: (err) => console.error('CV upload failed', err)
      });
    }
  }

  logout() {
    this.authService.logout();
  }
}
```

**Dashboard Features:**
- Role-based sidebar navigation
- User profile dropdown
- Profile modal integration
- CV upload for teachers
- Responsive sidebar toggle

---

### 4.2 Overview Component (`dashboard/overview/overview.component.ts`)

```typescript
import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-overview',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './overview.component.html',
  styleUrls: ['./overview.component.css']
})
export class OverviewComponent implements OnInit {
  private apiService = inject(ApiService);
  private authService = inject(AuthService);
  private cdr = inject(ChangeDetectorRef);

  totalStudents = 0;
  totalTeachers = 0;
  totalCourses = 0;
  averageGrade = 0;
  atRiskCount = 0;

  isLoading = true;

  ngOnInit() {
    if (this.authService.isTeacher()) {
      this.loadTeacherData();
    } else {
      this.loadOverviewData();
    }
  }

  loadOverviewData() {
    this.apiService.getStudents(1000, 0).subscribe({
      next: (res) => {
        this.totalStudents = res.total || res.students.length;
        
        // Calculate average grade
        const grades = res.students.map((s: any) => s.final_grade || 0);
        this.averageGrade = grades.length > 0 
          ? Math.round(grades.reduce((a: number, b: number) => a + b, 0) / grades.length)
          : 0;

        // Count at-risk students (< 40%)
        this.atRiskCount = res.students.filter((s: any) => (s.final_grade || 0) < 40).length;

        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error(err);
        this.isLoading = false;
      }
    });

    this.apiService.getTeachers().subscribe({
      next: (res) => {
        this.totalTeachers = res.total || res.teachers.length;
        this.cdr.detectChanges();
      }
    });

    this.apiService.getCourses().subscribe({
      next: (res) => {
        this.totalCourses = res.courses.length;
        this.cdr.detectChanges();
      }
    });
  }

  loadTeacherData() {
    const user = this.authService.getUser();
    this.apiService.getTeacherCourses(user.username).subscribe({
      next: (res) => {
        this.totalCourses = res.courses?.length || 0;
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error(err);
        this.isLoading = false;
      }
    });
  }
}
```

**Overview Statistics:**
- Total students, teachers, and courses
- Average student grade calculation
- At-risk student count (<40% threshold)
- Role-specific data loading (teachers see only their data)

---

## 5. Student Management

### 5.1 Students Component (`students/students.component.ts`)

```typescript
import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../services/api.service';
import { AuthService } from '../services/auth.service';
import { AddStudentModalComponent } from './add-student-modal.component';
import { AssignGradeModalComponent } from './assign-grade-modal.component';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-students',
  standalone: true,
  imports: [CommonModule, FormsModule, AddStudentModalComponent, AssignGradeModalComponent],
  templateUrl: './students.component.html',
  styleUrls: ['./students.component.css']
})
export class StudentsComponent implements OnInit {
  private apiService = inject(ApiService);
  private authService = inject(AuthService);
  private cdr = inject(ChangeDetectorRef);

  students: any[] = [];
  showModal = false;
  selectedStudent: any = null;
  searchQuery: string = '';
  selectedGender: string = '';
  showGradeModal = false;
  currentStudentCourses: any[] = [];

  get filteredStudents() {
    return this.students.filter(s => {
      const query = this.searchQuery ? this.searchQuery.toLowerCase() : '';
      const matchesSearch = !query ||
        s.name?.toLowerCase().includes(query) ||
        s.student_id?.toLowerCase().includes(query);

      const matchesGender = !this.selectedGender ||
        (s.gender || 'Other').toLowerCase() === this.selectedGender.toLowerCase();

      return matchesSearch && matchesGender;
    });
  }

  ngOnInit() {
    if (this.isStudent) {
      this.loadMyProfile();
    } else if (this.isTeacher) {
      this.loadTeacherStudents();
    } else {
      this.loadStudents();
    }
  }

  get isAdmin(): boolean {
    return this.authService.isAdmin();
  }

  get isStudent(): boolean {
    return this.authService.isStudent();
  }

  get isTeacher(): boolean {
    return this.authService.isTeacher();
  }

  loadStudents() {
    this.apiService.getStudents(100, 0).subscribe({
      next: (res: any) => {
        this.students = res.students;
        this.cdr.detectChanges();
      },
      error: (err) => console.error('Error loading students', err)
    });
  }

  loadMyProfile() {
    const user = this.authService.getUser();
    if (user && user.student_id) {
      this.apiService.getStudent(user.student_id).subscribe({
        next: (res: any) => {
          this.students = [res.student];
          this.cdr.detectChanges();
        },
        error: (err) => console.error('Error loading profile', err)
      });
    }
  }

  loadTeacherStudents() {
    const user = this.authService.getUser();
    this.apiService.getTeacherCourses(user.username).subscribe({
      next: (res: any) => {
        const courses = res.courses || [];
        if (courses.length === 0) {
          this.students = [];
          return;
        }

        let completed = 0;
        const studentMap = new Map<string, any>();

        courses.forEach((course: any) => {
          this.apiService.getCourseStudents(course.course_id).subscribe({
            next: (res: any) => {
              (res.students || []).forEach((s: any) => {
                const studentEntry = studentMap.get(s.student_id) || {
                  student_id: s.student_id,
                  name: s.student_name,
                  gender: 'Unknown',
                  courses: []
                };
                studentEntry.courses.push({
                  course_id: course.course_id,
                  course_name: course.name,
                  current_marks: s.marks
                });
                studentMap.set(s.student_id, studentEntry);
              });
            },
            complete: () => {
              completed++;
              if (completed === courses.length) {
                this.students = Array.from(studentMap.values());
                this.cdr.detectChanges();
              }
            }
          });
        });
      }
    });
  }

  openAddModal() {
    this.selectedStudent = null;
    this.showModal = true;
  }

  openEditModal(student: any) {
    this.selectedStudent = student;
    this.showModal = true;
  }

  closeModal() {
    this.showModal = false;
    this.selectedStudent = null;
  }

  deleteStudent(studentId: string) {
    if (confirm('Are you sure you want to delete this student?')) {
      this.apiService.deleteStudent(studentId).subscribe({
        next: () => this.loadStudents(),
        error: (err) => console.error(err)
      });
    }
  }

  openGradeModal(student: any) {
    this.selectedStudent = student;
    this.currentStudentCourses = student.courses;
    this.showGradeModal = true;
  }

  closeGradeModal() {
    this.showGradeModal = false;
    this.selectedStudent = null;
    this.loadTeacherStudents();
  }

  getGradeColor(grade: number): string {
    if (grade >= 90) return 'text-green-500';
    if (grade >= 70) return 'text-blue-500';
    if (grade >= 50) return 'text-yellow-500';
    return 'text-red-500';
  }

  getInitials(name: string): string {
    if (!name) return 'S';
    return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
  }
}
```

**Student Management Features:**
- Role-based data loading (admin sees all, student sees self, teacher sees enrolled)
- Real-time search and gender filtering
- CRUD operations (admin only)
- Grade assignment modal (teacher)
- Profile view with performance prediction (student)

---

## 6. Course Management

### 6.1 Courses Component (Excerpt) (courses/courses.component.ts`)

```typescript
import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../services/api.service';
import { AuthService } from '../services/auth.service';
import { AddCourseModalComponent } from './add-course-modal.component';
import { GradebookModalComponent } from './gradebook-modal.component';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-courses',
  standalone: true,
  imports: [CommonModule, AddCourseModalComponent, GradebookModalComponent, FormsModule],
  templateUrl: './courses.component.html',
  styleUrls: ['./courses.component.css']
})
export class CoursesComponent implements OnInit {
  private apiService = inject(ApiService);
  private authService = inject(AuthService);
  private cdr = inject(ChangeDetectorRef);

  courses: any[] = [];
  showModal = false;
  selectedCourse: any = null;
  showGradebookModal = false;
  searchQuery: string = '';

  ngOnInit() {
    this.loadCourses();
  }

  get isAdmin(): boolean {
    return this.authService.isAdmin();
  }

  get isStudent(): boolean {
    return this.authService.isStudent();
  }

  get isTeacher(): boolean {
    return this.authService.isTeacher();
  }

  loadCourses() {
    if (this.isStudent) {
      const user = this.authService.getUser();
      if (user && user.student_id) {
        this.apiService.getStudentCourses(user.student_id).subscribe({
          next: (res: any) => {
            this.courses = res.courses || [];
            this.cdr.detectChanges();
          }
        });
      }
    } else if (this.isTeacher) {
      const user = this.authService.getUser();
      this.apiService.getTeacherCourses(user.username).subscribe({
        next: (res: any) => {
          this.courses = res.courses || [];
          this.cdr.detectChanges();
        }
      });
    } else {
      this.apiService.getCourses().subscribe({
        next: (res: any) => {
          this.courses = res.courses;
          this.cdr.detectChanges();
        }
      });
    }
  }

  openGradebook(course: any) {
    this.selectedCourse = course;
    this.showGradebookModal = true;
  }

  deleteCourse(courseId: string) {
    if (confirm('Are you sure you want to delete this course?')) {
      this.apiService.deleteCourse(courseId).subscribe({
        next: () => this.loadCourses(),
        error: (err) => console.error(err)
      });
    }
  }
}
```

**Course Features:**
- Role-specific course lists (student: enrolled, teacher: teaching, admin: all)
- Gradebook access for teachers
- Course CRUD operations (admin)
- Student enrollment management

---

### 6.2 Gradebook Modal Component (`courses/gradebook-modal.component.ts`)

```typescript
import { Component, EventEmitter, Output, Input, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-gradebook-modal',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="modal-overlay" (click)="close.emit()">
        <div class="modal-content large" (click)="$event.stopPropagation()">
            <div class="modal-header">
                <h2>📊 Gradebook: {{course?.name}}</h2>
                <button class="close-btn" (click)="close.emit()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            
            <div class="modal-body">
                <p class="subtitle">Manage student grades for this course</p>
                
                <div class="students-list">
                    <div *ngFor="let student of students" class="student-row">
                        <div class="student-info">
                            <span class="student-name">{{student.student_name}}</span>
                            <span class="student-id">{{student.student_id}}</span>
                        </div>
                        <div class="grade-input">
                            <input 
                                type="number" 
                                [(ngModel)]="student.marks" 
                                min="0" 
                                max="100"
                                placeholder="0-100">
                            <button class="btn-save-grade" (click)="saveGrade(student)">
                                <i class="fas fa-save"></i> Save
                            </button>
                        </div>
                    </div>
                    
                    <div *ngIf="students.length === 0" class="empty-state">
                        <i class="fas fa-users-slash"></i>
                        <p>No students enrolled in this course yet.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
  `,
  styles: [`/* Styles omitted for brevity */`]
})
export class GradebookModalComponent implements OnInit {
  @Input() course: any = null;
  @Output() close = new EventEmitter<void>();

  private apiService = inject(ApiService);
  students: any[] = [];

  ngOnInit() {
    if (this.course) {
      this.loadStudents();
    }
  }

  loadStudents() {
    this.apiService.getCourseStudents(this.course.course_id).subscribe({
      next: (res: any) => {
        this.students = res.students || [];
      },
      error: (err: any) => console.error(err)
    });
  }

  saveGrade(student: any) {
    if (student.marks === null || student.marks === undefined) {
      alert('Please enter a grade');
      return;
    }

    this.apiService.assignGrade(student.student_id, this.course.course_id, student.marks).subscribe({
      next: () => {
        alert('Grade saved successfully');
      },
      error: (err: any) => {
        console.error(err);
        alert(err.error?.message || 'Failed to save grade');
      }
    });
  }
}
```

**Gradebook Features:**
- Lists all students enrolled in selected course
- Inline grade entry (0-100 validation)
- Individual save per student
- Empty state handling

---

## 7. Analytics Dashboard

### 7.1 Analytics Component (`analytics/analytics.component.ts`)

```typescript
import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-analytics',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './analytics.component.html',
  styleUrls: ['./analytics.component.css']
})
export class AnalyticsComponent implements OnInit {
  private apiService = inject(ApiService);
  private cdr = inject(ChangeDetectorRef);

  genderData: any[] = [];
  supportData: any[] = [];
  internetData: any[] = [];
  atRiskData: any[] = [];

  ngOnInit() {
    this.loadData();
  }

  loadData() {
    this.apiService.getGenderDistribution().subscribe({
      next: (res: any) => {
        this.genderData = res.gender_distribution;
        this.cdr.detectChanges();
      }
    });

    this.apiService.getPerformanceBySupport().subscribe({
      next: (res: any) => {
        this.supportData = res.performance_by_support;
        this.cdr.detectChanges();
      }
    });

    this.apiService.getInternetAccessImpact().subscribe({
      next: (res: any) => {
        this.internetData = res.internet_access_impact;
        this.cdr.detectChanges();
      }
    });

    this.apiService.getAtRiskStudents().subscribe({
      next: (res: any) => {
        this.atRiskData = res.at_risk_students;
        this.cdr.detectChanges();
      }
    });
  }
}
```

**Analytics Features:**
- Gender distribution visualization
- Performance correlation with parental support
- Internet access impact analysis
- At-risk student identification with risk factors

---

## 8. Supporting Modules

### 8.1 Environment Configuration (`environments/environment.ts`)

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:5001/api'
};
```

**Purpose:** Centralizes API endpoint configuration for easy environment switching.

---

## Code Statistics Summary

### Component Breakdown
- **Total Components:** 15+ standalone components
- **Services:** 2 core services (Auth, API)
- **Interceptors:** 1 HTTP interceptor
- **Routes:** 7 main routes + nested dashboard routes

### Key Technologies Used
- **Framework:** Angular 21 (standalone components)
- **State Management:** RxJS Observables
- **HTTP Communication:** HttpClient with interceptors
- **Routing:** Angular Router with nested routes
- **Forms:** Template-driven forms with FormsModule
- **Styling:** CSS with Glassmorphism dark theme

### Architecture Highlights
- **Standalone Components:** No NgModules, modern Angular architecture
- **Dependency Injection:** Using `inject()` function
- **Reactive Programming:** RxJS for async operations
- **Role-Based Access:** Dynamic UI rendering based on user role
- **Modular Design:** Clear separation of concerns

---

## Conclusion

This frontend codebase demonstrates a modern Angular application with:
- Clean architecture and separation of concerns
- Type-safe development with TypeScript
- Reactive programming patterns
- Role-based access control
- Responsive, accessible UI
- Integration with RESTful backend API

The application successfully implements comprehensive student management functionality with predictive analytics, providing an intuitive interface for students, teachers, and administrators.

---

**Document Version:** 1.0  
**Last Updated:** December 2024  
**Total Pages:** ~18 pages
