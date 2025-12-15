import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../services/api.service';
import { AuthService } from '../services/auth.service';
import { AddCourseModalComponent } from './add-course-modal.component';
import { GradebookModalComponent } from './gradebook-modal.component';

@Component({
    selector: 'app-courses',
    standalone: true,
    imports: [CommonModule, AddCourseModalComponent, GradebookModalComponent],
    template: `
    <div class="content-padding">
        <div class="page-header">
            <div class="page-title">
                <h1>Courses</h1>
                <span class="page-subtitle">Manage curriculum</span>
            </div>
            <button *ngIf="isAdmin" class="btn-primary" (click)="openAddModal()">
                <i class="fas fa-plus"></i> Add Course
            </button>
        </div>

        <div class="content-card">
            <div class="card-header">
                <h3>All Courses</h3>
            </div>
            
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Course Name</th>
                            <th>Description</th>
                            <th>Credits</th>
                            <th *ngIf="isAdmin || isStudent">Actions</th>
                            <th *ngIf="isTeacher">Manage</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr *ngFor="let course of courses">
                            <td>{{course.course_id}}</td>
                            <td class="font-medium">{{course.name}}</td>
                            <td>{{course.description}}</td>
                            <td>{{course.credits}}</td>
                            
                            <!-- Admin Actions -->
                            <td *ngIf="isAdmin">
                                <button class="btn-icon" (click)="openEditModal(course)"><i class="fas fa-edit"></i></button>
                                <button class="btn-icon" (click)="deleteCourse(course.course_id)">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </td>

                            <!-- Student Actions -->
                            <td *ngIf="isStudent">
                                <button *ngIf="!enrolledCourseIds.has(course.course_id)" class="btn-primary small" (click)="enroll(course.course_id)">
                                    Enroll
                                </button>
                                <button *ngIf="enrolledCourseIds.has(course.course_id)" class="btn-secondary small" disabled>
                                    Enrolled
                                </button>
                            </td>

                            <!-- Teacher Actions -->
                            <td *ngIf="isTeacher">
                                <button class="btn-primary small outline" (click)="openGradebook(course)">
                                    <i class="fas fa-graduation-cap"></i> Grades
                                </button>
                            </td>
                        </tr>
                        <tr *ngIf="courses.length === 0">
                            <td colspan="5" style="text-align: center; color: #94a3b8;">No courses found.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <!-- Add/Edit Course Modal -->
    <app-add-course-modal 
        *ngIf="showModal" 
        [course]="selectedCourse"
        (close)="closeModal()" 
        (saved)="loadCourses()">
    </app-add-course-modal>

    <!-- Gradebook Modal -->
    <app-gradebook-modal
        *ngIf="showGradebook"
        [courseId]="selectedCourseId"
        [courseName]="selectedCourseName"
        (close)="closeGradebook()">
    </app-gradebook-modal>
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
        .btn-primary.outline { background: transparent; border: 1px solid #8b5cf6; color: #8b5cf6; }
        .btn-primary.outline:hover { background: rgba(139, 92, 246, 0.1); }
        .btn-icon { background: none; border: none; color: #94a3b8; cursor: pointer; padding: 0.5rem; }
        .btn-icon:hover { color: white; }
        .btn-icon:hover { color: white; }
        .font-medium { font-weight: 500; color: white; }
        .btn-secondary { background: rgba(255,255,255,0.1); color: #94a3b8; border: none; padding: 0.5rem 1rem; border-radius: 0.375rem; cursor: not-allowed; }
    `]
})
export class CoursesComponent implements OnInit {
    private apiService = inject(ApiService);
    private authService = inject(AuthService);
    private cdr = inject(ChangeDetectorRef);

    courses: any[] = [];
    showModal = false;
    selectedCourse: any = null;
    enrolledCourseIds: Set<string> = new Set();

    // Gradebook state
    showGradebook = false;
    selectedCourseId = '';
    selectedCourseName = '';

    ngOnInit() {
        this.loadCourses();
        if (this.isStudent) {
            this.loadEnrollments();
        }
    }

    loadEnrollments() {
        const user = this.authService.getUser();
        if (user && user.student_id) {
            this.apiService.getStudentGrades(user.student_id).subscribe({
                next: (res: any) => {
                    this.enrolledCourseIds = new Set(res.grades.map((g: any) => g.course_id));
                    this.cdr.detectChanges();
                },
                error: (err) => console.error('Failed to load enrollments', err)
            });
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

    loadCourses() {
        this.apiService.getCourses().subscribe({
            next: (res: any) => {
                this.courses = res.courses || [];
                this.cdr.detectChanges();
            },
            error: (err) => {
                console.error(err);
                this.cdr.detectChanges();
            }
        });
    }

    enroll(courseId: string) {
        if (confirm('Enroll in this course?')) {
            this.apiService.enrollStudent({ course_id: courseId }).subscribe({
                next: () => {
                    alert('Successfully enrolled!');
                    this.enrolledCourseIds.add(courseId); // Update local state
                    this.cdr.detectChanges();
                },
                error: (err) => {
                    alert('Enrollment failed: ' + (err.error?.message || err.message));
                }
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
        this.selectedCourse = null;
        this.showModal = false;
    }

    deleteCourse(id: string) {
        if (confirm('Delete this course?')) {
            this.apiService.deleteCourse(id).subscribe(() => this.loadCourses());
        }
    }

    openGradebook(course: any) {
        this.selectedCourseId = course.course_id;
        this.selectedCourseName = course.name;
        this.showGradebook = true;
    }

    closeGradebook() {
        this.showGradebook = false;
        this.selectedCourseId = '';
        this.selectedCourseName = '';
    }
}
