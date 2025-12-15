
## File: frontend/src/app/courses/add-course-modal.component.ts
```typescript
import { Component, EventEmitter, Output, Input, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../services/api.service';

@Component({
    selector: 'app-add-course-modal',
    standalone: true,
    imports: [CommonModule, FormsModule],
    template: `
    <div class="modal-overlay" (click)="close.emit()">
        <div class="modal-content" (click)="$event.stopPropagation()">
            <div class="modal-header">
                <h2>{{ isEditMode ? 'Edit Course' : 'Add New Course' }}</h2>
                <button class="close-btn" (click)="close.emit()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            
            <div class="modal-body">
                <form (ngSubmit)="save()">
                    <div class="form-group">
                        <label>Course ID</label>
                        <input type="text" [(ngModel)]="data.course_id" name="course_id" required placeholder="CS101" [disabled]="isEditMode">
                    </div>
                    
                    <div class="form-group">
                        <label>Course Name</label>
                        <input type="text" [(ngModel)]="data.name" name="name" required placeholder="Introduction to Computer Science">
                    </div>
                    
                    <div class="form-group">
                        <label>Description</label>
                        <textarea [(ngModel)]="data.description" name="description" rows="3" placeholder="Course overview..."></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label>Credits</label>
                        <input type="number" [(ngModel)]="data.credits" name="credits" required placeholder="3" min="1" max="6">
                    </div>
                    
                    <div class="form-group">
                        <label>Department</label>
                        <input type="text" [(ngModel)]="data.department" name="department" placeholder="Computer Science">
                    </div>
                    
                    <div class="modal-actions">
                        <button type="button" class="btn-cancel" (click)="close.emit()">Cancel</button>
                        <button type="submit" class="btn-save" [disabled]="isLoading">
                            {{ isLoading ? 'Saving...' : (isEditMode ? 'Update Course' : 'Save Course') }}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    `,
    styles: [`
        .modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); display: flex; justify-content: center; align-items: center; z-index: 1000; backdrop-filter: blur(5px); }
        .modal-content { background: #1e293b; border: 1px solid rgba(255,255,255,0.1); border-radius: 1rem; width: 90%; max-width: 500px; padding: 0; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); }
        .modal-header { padding: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; align-items: center; }
        .modal-header h2 { color: white; margin: 0; font-size: 1.25rem; }
        .close-btn { background: none; border: none; color: #94a3b8; font-size: 1.25rem; cursor: pointer; }
        .modal-body { padding: 1.5rem; }
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; color: #cbd5e1; margin-bottom: 0.5rem; font-size: 0.875rem; }
        .form-group input, .form-group textarea { width: 100%; padding: 0.75rem; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 0.5rem; color: white; font-family: inherit; }
        .form-group input:focus, .form-group textarea:focus { outline: none; border-color: #8b5cf6; }
        .form-group input:disabled { opacity: 0.5; cursor: not-allowed; }
        .modal-actions { display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1.5rem; }
        .btn-cancel { background: transparent; border: 1px solid rgba(255,255,255,0.1); color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; cursor: pointer; }
        .btn-save { background: #8b5cf6; border: none; color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; cursor: pointer; }
        .btn-save:disabled { opacity: 0.5; cursor: not-allowed; }
    `]
})
export class AddCourseModalComponent implements OnInit {
    @Input() course: any = null;
    @Output() close = new EventEmitter<void>();
    @Output() saved = new EventEmitter<void>();

    private apiService = inject(ApiService);

    isLoading = false;
    isEditMode = false;
    data: any = {};

    ngOnInit() {
        if (this.course) {
            this.isEditMode = true;
            this.data = { ...this.course };
        }
    }

    save() {
        if (!this.data.course_id || !this.data.name) {
            alert('Please fill in required fields');
            return;
        }

        this.isLoading = true;
        const request$ = this.isEditMode
            ? this.apiService.updateCourse(this.data.course_id, this.data)
            : this.apiService.createCourse(this.data);

        request$.subscribe({
            next: () => {
                this.isLoading = false;
                this.saved.emit();
                this.close.emit();
            },
            error: (err: any) => {
                console.error(err);
                this.isLoading = false;
                alert(err.error?.message || 'Failed to save course');
            }
        });
    }
}
```

## File: frontend/src/app/courses/courses.component.ts
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
    template: `
    <div class="content-padding">
        <div class="page-header">
            <div class="page-title">
                <h1>{{ getPageTitle() }}</h1>
                <span class="page-subtitle">{{ getPageSubtitle() }}</span>
            </div>
            <button *ngIf="isAdmin" class="btn-primary" (click)="openAddModal()">
                <i class="fas fa-plus"></i> Add Course
            </button>
        </div>

        <div class="content-card">
            <div class="card-header">
                <h3>{{ isStudent ? 'My Enrolled Courses' : 'Course List' }} ({{filteredCourses.length}})</h3>
                <div class="filters" *ngIf="!isStudent">
                    <div class="search-box">
                        <i class="fas fa-search"></i>
                        <input type="text" placeholder="Search courses..." [(ngModel)]="searchQuery">
                    </div>
                </div>
            </div>

            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Course ID</th>
                            <th>Course Name</th>
                            <th>Department</th>
                            <th>Credits</th>
                            <th *ngIf="isStudent">Teacher</th>
                            <th *ngIf="isStudent">My Grade</th>
                            <th *ngIf="!isStudent">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr *ngFor="let course of filteredCourses">
                            <td>{{course.course_id}}</td>
                            <td class="font-medium">{{course.name}}</td>
                            <td>{{course.department || 'N/A'}}</td>
                            <td>{{course.credits}}</td>
                            <td *ngIf="isStudent">{{course.teacher_name || 'TBA'}}</td>
                            <td *ngIf="isStudent">
                                <span [class]="getGradeColor(course.student_marks)">
                                    {{course.student_marks ?? 'N/A'}}
                                </span>
                            </td>
                            <td *ngIf="isAdmin">
                                <button class="btn-icon" (click)="openEditModal(course)"><i class="fas fa-edit"></i></button>
                                <button class="btn-icon" (click)="deleteCourse(course.course_id)">
                                    <i class="fas fa-trash"></i>
                                </button>
                                <button class="btn-primary small" (click)="openEnrollModal(course)">
                                    Enroll Students
                                </button>
                            </td>
                            <td *ngIf="isTeacher">
                                <button class="btn-primary small" (click)="openGradebook(course)">
                                    Gradebook
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <app-add-course-modal 
        *ngIf="showModal" 
        [course]="selectedCourse"
        (close)="closeModal()" 
        (saved)="loadCourses()">
    </app-add-course-modal>

    <app-gradebook-modal
        *ngIf="showGradebookModal"
        [course]="selectedCourse"
        (close)="closeGradebookModal()">
    </app-gradebook-modal>

    <!-- Simple Enroll Modal -->
    <div *ngIf="showEnrollModal" class="modal-overlay" (click)="closeEnrollModal()">
        <div class="modal-content small" (click)="$event.stopPropagation()">
            <div class="modal-header">
                <h2>Enroll Students in {{selectedCourse?.name}}</h2>
                <button class="close-btn" (click)="closeEnrollModal()"><i class="fas fa-times"></i></button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label>Student ID</label>
                    <input type="text" [(ngModel)]="enrollStudentId" placeholder="S001">
                </div>
                <div class="modal-actions">
                    <button class="btn-cancel" (click)="closeEnrollModal()">Cancel</button>
                    <button class="btn-save" (click)="enrollStudent()">Enroll</button>
                </div>
            </div>
        </div>
    </div>
    `,
    styles: [`
        .content-padding { padding: var(--spacing-xl); }
        .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--spacing-xl); }
        .page-title h1 { font-size: 2rem; font-weight: 600; color: white; margin-bottom: 0.5rem; }
        .page-subtitle { color: #94a3b8; }
        .content-card { background: #1e293b; border: 1px solid rgba(255,255,255,0.05); border-radius: 1rem; padding: 1.5rem; }
        .card-header h3 { color: white; margin-bottom: 1rem; }
        .table-container { overflow-x: auto; }
        .data-table { width: 100%; border-collapse: collapse; color: #cbd5e1; }
        .data-table th { text-align: left; padding: 1rem; background: rgba(255,255,255,0.05); color: white; font-weight: 600; }
        .data-table td { padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .data-table tr:hover { background: rgba(255,255,255,0.02); }
        .btn-primary { background-color: #8b5cf6; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.375rem; cursor: pointer; display: flex; align-items: center; gap: 0.5rem; }
        .btn-primary.small { padding: 0.25rem 0.75rem; font-size: 0.875rem; }
        .btn-icon { background: none; border: none; color: #94a3b8; cursor: pointer; padding: 0.5rem; }
        .btn-icon:hover { color: white; }
        .font-medium { font-weight: 500; color: white; }
        
        .card-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }
        .filters { display: flex; gap: 1rem; align-items: center; }
        .search-box { position: relative; }
        .search-box i { position: absolute; left: 0.75rem; top: 50%; transform: translateY(-50%); color: #94a3b8; }
        .search-box input { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white; padding: 0.5rem 1rem 0.5rem 2.25rem; border-radius: 0.5rem; outline: none; width: 200px; }
        .search-box input:focus { border-color: #8b5cf6; }

        .modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); display: flex; justify-content: center; align-items: center; z-index: 1000; backdrop-filter: blur(5px); }
        .modal-content.small { max-width: 400px; background: #1e293b; border: 1px solid rgba(255,255,255,0.1); border-radius: 1rem; width: 90%; padding: 0; }
        .modal-header { padding: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; align-items: center; }
        .modal-header h2 { color: white; margin: 0; font-size: 1.25rem; }
        .close-btn { background: none; border: none; color: #94a3b8; font-size: 1.25rem; cursor: pointer; }
        .modal-body { padding: 1.5rem; }
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; color: #cbd5e1; margin-bottom: 0.5rem; font-size: 0.875rem; }
        .form-group input { width: 100%; padding: 0.75rem; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 0.5rem; color: white; }
        .modal-actions { display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1.5rem; }
        .btn-cancel { background: transparent; border: 1px solid rgba(255,255,255,0.1); color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; cursor: pointer; }
        .btn-save { background: #8b5cf6; border: none; color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; cursor: pointer; }
    `]
})
export class CoursesComponent implements OnInit {
    private apiService = inject(ApiService);
    private authService = inject(AuthService);
    private cdr = inject(ChangeDetectorRef);

    courses: any[] = [];
    showModal = false;
    selectedCourse: any = null;
    searchQuery: string = '';

    showGradebookModal = false;
    showEnrollModal = false;
    enrollStudentId = '';

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

    get filteredCourses() {
        return this.courses.filter(c => {
            const matchesSearch = !this.searchQuery ||
                c.name?.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                c.course_id?.toLowerCase().includes(this.searchQuery.toLowerCase());
            return matchesSearch;
        });
    }

    getPageTitle(): string {
        if (this.isStudent) return 'My Courses';
        if (this.isTeacher) return 'My Teaching Courses';
        return 'Courses';
    }

    getPageSubtitle(): string {
        if (this.isStudent) return 'View your enrolled courses and grades';
        if (this.isTeacher) return 'Manage your teaching assignments';
        return 'Manage all courses';
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
                },
                error: (err: any) => console.error(err)
            });
        }
    }

    openAddModal() {
        this.selectedCourse = null;
        this.showModal = true;
    }

    openEditModal(course: any) {
        this.selectedCourse = course;
        this.showModal = true;
    }

    closeModal() {
        this.showModal = false;
        this.selectedCourse = null;
    }

    deleteCourse(courseId: string) {
        if (confirm('Are you sure you want to delete this course?')) {
            this.apiService.deleteCourse(courseId).subscribe({
                next: () => {
                    this.loadCourses();
                },
                error: (err: any) => console.error(err)
            });
        }
    }

    openEnrollModal(course: any) {
        this.selectedCourse = course;
        this.showEnrollModal = true;
    }

    closeEnrollModal() {
        this.showEnrollModal = false;
        this.enrollStudentId = '';
    }

    enrollStudent() {
        if (!this.enrollStudentId) return;
        this.apiService.enrollStudent(this.selectedCourse.course_id, this.enrollStudentId).subscribe({
            next: () => {
                alert('Student enrolled successfully');
                this.closeEnrollModal();
            },
            error: (err: any) => alert(err.error?.message || 'Enrollment failed')
        });
    }

    openGradebook(course: any) {
        this.selectedCourse = course;
        this.showGradebookModal = true;
    }

    closeGradebookModal() {
        this.showGradebookModal = false;
        this.selectedCourse = null;
    }

    getGradeColor(grade: number): string {
        if (grade >= 90) return 'text-green-500';
        if (grade >= 70) return 'text-blue-500';
        if (grade >= 50) return 'text-yellow-500';
        return 'text-red-500';
    }
}
```

## File: frontend/src/app/courses/gradebook-modal.component.ts
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
    styles: [`
        .modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); display: flex; justify-content: center; align-items: center; z-index: 1000; backdrop-filter: blur(5px); }
        .modal-content.large { background: #1e293b; border: 1px solid rgba(255,255,255,0.1); border-radius: 1rem; width: 90%; max-width: 700px; padding: 0; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); max-height: 80vh; overflow-y: auto; }
        .modal-header { padding: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; background: #1e293b; z-index: 10; }
        .modal-header h2 { color: white; margin: 0; font-size: 1.25rem; }
        .close-btn { background: none; border: none; color: #94a3b8; font-size: 1.25rem; cursor: pointer; transition: color 0.2s; }
        .close-btn:hover { color: white; }
        .modal-body { padding: 1.5rem; }
        .subtitle { color: #94a3b8; margin-bottom: 1.5rem; font-size: 0.9rem; }
        
        .students-list { display: flex; flex-direction: column; gap: 1rem; }
        .student-row { display: flex; justify-content: space-between; align-items: center; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 0.5rem; border: 1px solid rgba(255,255,255,0.1); }
        .student-info { display: flex; flex-direction: column; gap: 0.25rem; }
        .student-name { color: white; font-weight: 500; }
        .student-id { color: #94a3b8; font-size: 0.85rem; }
        .grade-input { display: flex; gap: 0.5rem; align-items: center; }
        .grade-input input { width: 80px; padding: 0.5rem; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.2); border-radius: 0.375rem; color: white; text-align: center; }
        .grade-input input:focus { outline: none; border-color: #8b5cf6; }
        .btn-save-grade { background: #8b5cf6; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.375rem; cursor: pointer; font-size: 0.875rem; display: flex; align-items: center; gap: 0.5rem; transition: background 0.2s; }
        .btn-save-grade:hover { background: #7c3aed; }

        .empty-state { text-align: center; padding: 3rem 1rem; color: #64748b; }
        .empty-state i { font-size: 3rem; margin-bottom: 1rem; opacity: 0.5; }
        .empty-state p { margin: 0; font-size: 0.95rem; }
    `]
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
