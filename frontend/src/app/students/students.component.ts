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
    totalStudents = 0;
    isLoading = true;
    showModal = false;
    selectedStudent: any = null;
    searchQuery: string = '';
    selectedGender: string = '';

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

    // Teacher Specific State
    showGradeModal = false;
    currentStudentCourses: any[] = [];

    loadTeacherStudents() {
        this.isLoading = true;
        const user = this.authService.getUser();
        // 1. Get Teacher's Courses
        this.apiService.getTeacherCourses(user.username).subscribe({
            next: (res: any) => {
                const courses = res.courses || [];
                if (courses.length === 0) {
                    this.students = [];
                    this.isLoading = false;
                    return;
                }

                // 2. For each course, get students
                // Naive approach: multiple calls (parallel)
                let completed = 0;
                const studentMap = new Map<string, any>();

                courses.forEach((course: any) => {
                    this.apiService.getCourseStudents(course.course_id).subscribe({
                        next: (res: any) => {
                            (res.students || []).forEach((s: any) => {
                                // Add course info to student for grading context
                                const studentEntry = studentMap.get(s.student_id) || {
                                    student_id: s.student_id,
                                    name: s.student_name,
                                    gender: 'Unknown', // Not in this endpoint, but fine
                                    courses: []
                                };
                                studentEntry.courses.push({
                                    course_id: course.course_id,
                                    course_name: course.name,
                                    current_marks: s.marks
                                });
                                // Keep 'final_grade' as average of known marks?
                                studentMap.set(s.student_id, studentEntry);
                            });
                        },
                        complete: () => {
                            completed++;
                            if (completed === courses.length) {
                                this.students = Array.from(studentMap.values());
                                this.totalStudents = this.students.length;
                                this.isLoading = false;
                                this.cdr.detectChanges();
                            }
                        }
                    });
                });
            },
            error: (err) => {
                console.error(err);
                this.isLoading = false;
            }
        });
    }

    openGradeModal(student: any) {
        this.selectedStudent = student;
        this.currentStudentCourses = student.courses;
        this.showGradeModal = true;
    }

    closeGradeModal() {
        this.showGradeModal = false;
        this.selectedStudent = null;
        this.currentStudentCourses = [];
        this.loadTeacherStudents(); // Reload to see updates
    }

    loadMyProfile() {
        const user = this.authService.getUser();
        if (user && user.student_id) {
            this.apiService.getStudent(user.student_id).subscribe({
                next: (res: any) => {
                    this.students = [res.student]; // Show only self
                    this.totalStudents = 1;
                    this.isLoading = false;
                    this.cdr.detectChanges();
                },
                error: (err) => {
                    console.error('Error loading profile', err);
                    this.isLoading = false;
                    this.cdr.detectChanges();
                }
            });
        }
    }

    loadStudents() {
        this.apiService.getStudents(100, 0).subscribe({
            next: (res: any) => {
                this.students = res.students;
                this.totalStudents = res.total;
                this.isLoading = false;
                this.cdr.detectChanges();
            },
            error: (err) => {
                console.error('Error loading students', err);
                this.isLoading = false;
                this.cdr.detectChanges();
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
                next: () => {
                    this.loadStudents();
                },
                error: (err) => console.error(err)
            });
        }
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
