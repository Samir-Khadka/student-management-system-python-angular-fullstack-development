import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class ApiService {
    private http = inject(HttpClient);
    private apiUrl = environment.apiUrl;

    getProfilePictureUrl(path: string | undefined | null): string | null {
        if (!path) return null;
        if (path.startsWith('http') || path.startsWith('data:')) return path;
        // e.g. /static/uploads/file.png -> http://localhost:5001/static/uploads/file.png
        const baseUrl = this.apiUrl.replace('/api', '');
        return `${baseUrl}${path}`;
    }

    // Student Endpoints
    getStudents(limit: number = 100, skip: number = 0): Observable<any> {
        return this.http.get(`${this.apiUrl}/students/?limit=${limit}&skip=${skip}`);
    }

    createStudent(data: any): Observable<any> {
        return this.http.post(`${this.apiUrl}/students/`, data);
    }

    deleteStudent(studentId: string): Observable<any> {
        return this.http.delete(`${this.apiUrl}/students/${studentId}`);
    }

    // Teacher Endpoints
    getTeachers(): Observable<any> {
        return this.http.get(`${this.apiUrl}/teachers/`);
    }

    createTeacher(data: any): Observable<any> {
        return this.http.post(`${this.apiUrl}/teachers/`, data);
    }

    deleteTeacher(teacherId: string): Observable<any> {
        return this.http.delete(`${this.apiUrl}/teachers/${teacherId}`);
    }

    getTeacherCourses(teacherId: string): Observable<any> {
        return this.http.get(`${this.apiUrl}/courses/teacher/${teacherId}`);
    }

    // User Endpoints
    updateProfile(data: any): Observable<any> {
        return this.http.put(`${this.apiUrl}/auth/profile`, data);
    }

    uploadCV(file: File): Observable<any> {
        const formData = new FormData();
        formData.append('file', file);
        return this.http.post(`${this.apiUrl}/auth/upload-cv`, formData);
    }

    uploadProfilePicture(file: File): Observable<any> {
        const formData = new FormData();
        formData.append('file', file);
        return this.http.post(`${this.apiUrl}/auth/upload-picture`, formData);
    }

    removeProfilePicture(): Observable<any> {
        return this.http.post(`${this.apiUrl}/auth/remove-picture`, {});
    }

    // Admin Endpoints
    getPendingTeachers(): Observable<any> {
        return this.http.get(`${this.apiUrl}/auth/pending-teachers`);
    }

    approveTeacher(userId: string): Observable<any> {
        return this.http.post(`${this.apiUrl}/auth/approve-teacher/${userId}`, {});
    }

    // Course Endpoints
    getCourses(): Observable<any> {
        return this.http.get(`${this.apiUrl}/courses/`);
    }

    createCourse(data: any): Observable<any> {
        return this.http.post(`${this.apiUrl}/courses/`, data);
    }

    deleteCourse(courseId: string): Observable<any> {
        return this.http.delete(`${this.apiUrl}/courses/${courseId}`);
    }

    // Analytics Endpoints
    getAverageGrade(gender?: string, support?: string): Observable<any> {
        let params: any = {};
        if (gender) params.gender = gender;
        if (support) params.parental_support = support;
        return this.http.get(`${this.apiUrl}/analytics/average_grade`, { params });
    }

    getAtRiskStudents(): Observable<any> {
        return this.http.get(`${this.apiUrl}/analytics/at_risk_students`);
    }

    getGenderDistribution(): Observable<any> {
        return this.http.get(`${this.apiUrl}/analytics/gender_distribution`);
    }

    getPerformanceBySupport(): Observable<any> {
        return this.http.get(`${this.apiUrl}/analytics/performance_by_support`);
    }

    getInternetAccessImpact(): Observable<any> {
        return this.http.get(`${this.apiUrl}/analytics/internet_access_impact`);
    }

    // Update Methods
    updateStudent(id: string, data: any): Observable<any> {
        return this.http.put(`${this.apiUrl}/students/${id}`, data);
    }

    updateTeacher(id: string, data: any): Observable<any> {
        return this.http.put(`${this.apiUrl}/teachers/${id}`, data);
    }

    updateCourse(id: string, data: any): Observable<any> {
        return this.http.put(`${this.apiUrl}/courses/${id}`, data);
    }

    // New methods for Student Features
    getPublicCourses(): Observable<any> {
        return this.http.get(`${this.apiUrl}/courses/public`);
    }

    getStudent(id: string): Observable<any> {
        return this.http.get(`${this.apiUrl}/students/${id}`);
    }

    enrollStudent(data: any): Observable<any> {
        return this.http.post(`${this.apiUrl}/courses/enroll`, data);
    }

    getStudentGrades(studentId: string): Observable<any> {
        return this.http.get(`${this.apiUrl}/students/${studentId}/grades`);
    }

    // Grading Endpoints
    getCourseStudents(courseId: string): Observable<any> {
        return this.http.get(`${this.apiUrl}/courses/${courseId}/students`);
    }

    gradeStudent(data: any): Observable<any> {
        return this.http.post(`${this.apiUrl}/courses/grade`, data);
    }
}
