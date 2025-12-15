import { Component, inject, OnInit, ChangeDetectorRef, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../services/api.service';
import { AuthService } from '../services/auth.service';

@Component({
    selector: 'app-student-grades',
    standalone: true,
    imports: [CommonModule],
    template: `
    <div class="content-padding">
        <div class="page-header">
            <div class="page-title">
                <h1>My Grades</h1>
                <span class="page-subtitle">Academic performance record</span>
            </div>
            
             <div class="tab-buttons">
                <button class="tab-btn" [class.active]="activeTab === 'grades'" (click)="switchTab('grades')">My Grades</button>
                <button class="tab-btn" [class.active]="activeTab === 'courses'" (click)="switchTab('courses')">Browse Courses</button>
            </div>
        </div>

        <!-- My Grades Tab -->
        <div class="content-card" *ngIf="activeTab === 'grades'">
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>COURSE</th>
                            <th>TEACHER</th>
                            <th>MARKS</th>
                            <th>STATUS</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr *ngFor="let grade of grades">
                            <td>
                                <div class="course-info">
                                    <span class="course-name">{{grade.course_name}}</span>
                                    <span class="course-id">{{grade.course_id}}</span>
                                </div>
                            </td>
                            <td>{{grade.teacher_name || 'N/A'}}</td>
                            <td>
                                <span class="marks-display" [class.pending]="grade.marks === null">
                                    {{grade.marks === null ? '--' : grade.marks}}
                                </span>
                            </td>
                            <td>
                                <span class="status-badge" [ngClass]="getStatusColor(grade.marks)">
                                    {{getStatusText(grade.marks)}}
                                </span>
                            </td>
                        </tr>
                        <tr *ngIf="grades.length === 0">
                            <td colspan="4" class="empty-state">No grades available yet. Switch to "Browse Courses" to enroll!</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Browse Courses Tab -->
        <div *ngIf="activeTab === 'courses'">
            <!-- Enrollment Limit Warning -->
            <div class="alert-info" *ngIf="enrolledCourseIds.length >= 5">
                <i class="fas fa-info-circle"></i>
                <div>
                    <strong>Enrollment Limit Reached</strong>
                    <p>You are enrolled in {{enrolledCourseIds.length}} courses (maximum allowed). Please drop a course to enroll in a new one.</p>
                </div>
            </div>

            <div class="alert-success" *ngIf="enrolledCourseIds.length < 5 && enrolledCourseIds.length > 0">
                <i class="fas fa-check-circle"></i>
                <p>You are enrolled in {{enrolledCourseIds.length}} / 5 courses. You can enroll in {{5 - enrolledCourseIds.length}} more.</p>
            </div>

            <div class="courses-grid">
                <div class="course-card" *ngFor="let course of availableCourses">
                    <div class="course-header">
                        <h3>{{course.name}}</h3>
                        <span class="course-code">{{course.course_id}}</span>
                    </div>
                    <div class="course-details">
                        <div class="detail-item">
                            <i class="fas fa-chalkboard-teacher"></i>
                            <span>{{course.teacher_name || 'TBD'}}</span>
                        </div>
                        <div class="detail-item">
                            <i class="fas fa-graduation-cap"></i>
                            <span>{{course.credits || 3}} Credits</span>
                        </div>
                    </div>
                    <p class="course-desc">{{course.description || 'No description available'}}</p>
                    
                    <button 
                        class="enroll-btn"
                        [class.enrolled]="isEnrolled(course.course_id)"
                        [disabled]="isEnrolled(course.course_id) || (enrolledCourseIds.length >= 5 && !isEnrolled(course.course_id))"
                        (click)="enrollInCourse(course)">
                        <i class="fas" [class.fa-check]="isEnrolled(course.course_id)" [class.fa-plus]="!isEnrolled(course.course_id)"></i>
                        {{isEnrolled(course.course_id) ? 'Enrolled' : (enrolledCourseIds.length >= 5 ? 'Limit Reached' : 'Enroll Now')}}
                    </button>
                </div>

                <div class="empty-state" *ngIf="availableCourses.length === 0">
                    <i class="fas fa-book-open"></i>
                    <p>No courses available at the moment</p>
                </div>
            </div>
        </div>
    </div>
    `,
    styles: [`
        .content-padding { 
            padding: 2rem;
            min-height: 100vh;
            position: relative;
            z-index: 1;
        }
        
        .page-header { 
            margin-bottom: 2rem;
            padding: 2rem;
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(168, 139, 250, 0.05) 100%);
            border: 1px solid rgba(139, 92, 246, 0.2);
            border-radius: 1.5rem;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            box-shadow: 0 8px 32px rgba(139, 92, 246, 0.1);
        }
        
        .page-title h1 { 
            font-size: 2.25rem; 
            font-weight: 700; 
            color: white; 
            margin-bottom: 0.5rem;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, #fff 0%, #a78bfa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .page-subtitle { 
            color: #c4b5fd;
            font-size: 1rem;
            font-weight: 500;
        }
        
        .tab-buttons { display: flex; gap: 1rem; margin-top: 1.5rem; }
        .tab-btn { 
            background: rgba(255,255,255,0.05); 
            border: 1px solid rgba(139, 92, 246, 0.2); 
            color: #94a3b8; 
            padding: 0.75rem 1.5rem; 
            border-radius: 0.75rem; 
            cursor: pointer; 
            transition: all 0.3s;
            font-weight: 600;
            font-size: 0.95rem;
        }
        .tab-btn:hover { background: rgba(139, 92, 246, 0.1); color: #a78bfa; }
        .tab-btn.active { 
            background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%); 
            color: white; 
            border-color: #8b5cf6;
            box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
        }
        
        .content-card { 
            background: rgba(30, 41, 59, 0.6);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(139, 92, 246, 0.15); 
            border-radius: 1.5rem; 
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2),
                        0 0 0 1px rgba(255, 255, 255, 0.02) inset;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        .content-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #8b5cf6, #a78bfa, #8b5cf6);
            background-size: 200% 100%;
            animation: shimmer 3s linear infinite;
        }
        
        @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        
        .content-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 16px 48px rgba(139, 92, 246, 0.25),
                        0 0 0 1px rgba(139, 92, 246, 0.2) inset;
            border-color: rgba(139, 92, 246, 0.3);
        }
        
        /* Alerts */
        .alert-info, .alert-success {
            padding: 1.25rem 1.5rem;
            border-radius: 1rem;
            margin-bottom: 2rem;
            display: flex;
            align-items: flex-start;
            gap: 1rem;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
        }

        .alert-info {
            background: rgba(245, 158, 11, 0.1);
            border: 1px solid rgba(245, 158, 11, 0.3);
            color: #fbbf24;
        }

        .alert-success {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: #34d399;
        }

        .alert-info i, .alert-success i {
            font-size: 1.25rem;
            margin-top: 0.125rem;
        }

        .alert-info strong {
            display: block;
            font-size: 1rem;
            margin-bottom: 0.25rem;
        }

        .alert-info p, .alert-success p {
            margin: 0;
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        /* Courses Grid */
        .courses-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 1.5rem;
        }

        .course-card {
            background: rgba(30, 41, 59, 0.6);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(139, 92, 246, 0.15);
            border-radius: 1.25rem;
            padding: 1.75rem;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .course-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #8b5cf6, #a78bfa);
        }

        .course-card:hover {
            transform: translateY(-4px);
            border-color: rgba(139, 92, 246, 0.3);
            box-shadow: 0 12px 32px rgba(139, 92, 246, 0.2);
        }

        .course-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1rem;
        }

        .course-header h3 {
            color: white;
            font-size: 1.25rem;
            font-weight: 600;
            margin: 0;
            flex: 1;
        }

        .course-code {
            background: rgba(139, 92, 246, 0.2);
            color: #c4b5fd;
            padding: 0.35rem 0.75rem;
            border-radius: 0.5rem;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            border: 1px solid rgba(139, 92, 246, 0.3);
        }

        .course-details {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            margin-bottom: 1rem;
        }

        .detail-item {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            color: #cbd5e1;
            font-size: 0.9rem;
        }

        .detail-item i {
            color: #a78bfa;
            width: 1.25rem;
        }

        .course-desc {
            color: #94a3b8;
            font-size: 0.875rem;
            line-height: 1.6;
            margin: 1rem 0 1.5rem 0;
            min-height: 3rem;
        }

        .enroll-btn {
            width: 100%;
            padding: 0.875rem 1.5rem;
            background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%);
            color: white;
            border: none;
            border-radius: 0.75rem;
            font-weight: 600;
            font-size: 0.95rem;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
        }

        .enroll-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4);
        }

        .enroll-btn:active:not(:disabled) {
            transform: translateY(0);
        }

        .enroll-btn.enrolled {
            background: rgba(16, 185, 129, 0.2);
            border: 1px solid rgba(16, 185, 129, 0.4);
            color: #10b981;
            cursor: default;
        }

        .enroll-btn:disabled {
            background: rgba(148, 163, 184, 0.1);
            border: 1px solid rgba(148, 163, 184, 0.2);
            color: #64748b;
            cursor: not-allowed;
            box-shadow: none;
        }
        
        .table-container { overflow-x: auto; }
        .data-table { width: 100%; border-collapse: separate; border-spacing: 0; color: #cbd5e1; }
        .data-table th { text-align: left; padding: 1rem; background: rgba(255,255,255,0.03); color: #94a3b8; font-weight: 600; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .data-table td { padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.05); vertical-align: middle; }
        .data-table tr:hover { background: rgba(255,255,255,0.02); }
        
        .course-info { display: flex; flex-direction: column; }
        .course-name { color: white; font-weight: 500; }
        .course-id { font-size: 0.75rem; color: #94a3b8; }
        
        .marks-display { font-weight: 600; color: white; }
        .marks-display.pending { color: #94a3b8; font-weight: 400; }
        
        .status-badge { padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
        .status-pass { background: rgba(16, 185, 129, 0.1); color: #10b981; }
        .status-fail { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
        .status-pending { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }
        
        .empty-state { 
            text-align: center; 
            padding: 4rem 2rem; 
            color: #94a3b8;
            grid-column: 1 / -1;
        }

        .empty-state i {
            font-size: 3rem;
            color: #475569;
            margin-bottom: 1rem;
            display: block;
        }

        .empty-state p {
            font-size: 1.125rem;
            margin: 0;
        }
    `]
})
export class StudentGradesComponent implements OnInit, AfterViewInit {
    private apiService = inject(ApiService);
    private authService = inject(AuthService);
    private cdr = inject(ChangeDetectorRef);

    grades: any[] = [];
    availableCourses: any[] = [];
    enrolledCourseIds: string[] = [];
    activeTab: 'grades' | 'courses' = 'grades';

    ngOnInit() {
        this.loadGrades();
        this.loadAvailableCourses();
    }

    ngAfterViewInit() {
        setTimeout(() => {
            this.cdr.detectChanges();
        }, 0);
    }

    switchTab(tab: 'grades' | 'courses') {
        this.activeTab = tab;
        if (tab === 'courses' && this.availableCourses.length === 0) {
            this.loadAvailableCourses();
        }
    }

    loadGrades() {
        const user = this.authService.getUser();

        if (user && user.student_id) {
            this.apiService.getStudentGrades(user.student_id).subscribe({
                next: (res: any) => {
                    this.grades = res.grades || [];
                    this.enrolledCourseIds = this.grades.map(g => g.course_id);
                    this.cdr.detectChanges();
                },
                error: (err) => {
                    console.error('Error loading grades:', err);
                }
            });
        }
    }

    loadAvailableCourses() {
        this.apiService.getCourses().subscribe({
            next: (res: any) => {
                this.availableCourses = res.courses || [];
                this.cdr.detectChanges();
            },
            error: (err) => {
                console.error('Error loading courses:', err);
            }
        });
    }

    isEnrolled(courseId: string): boolean {
        return this.enrolledCourseIds.includes(courseId);
    }

    enrollInCourse(course: any) {
        // Check if already enrolled
        if (this.isEnrolled(course.course_id)) {
            alert('You are already enrolled in this course!');
            return;
        }

        // Check enrollment limit
        if (this.enrolledCourseIds.length >= 5) {
            alert('⚠️ Enrollment Limit Reached!\n\nYou can only enroll in a maximum of 5 courses per semester.\n\nPlease drop a course before enrolling in a new one.');
            return;
        }

        const user = this.authService.getUser();
        if (!user || !user.student_id) {
            alert('Error: Student ID not found. Please log in again.');
            return;
        }

        // Enroll via API - pass data object
        const enrollmentData = {
            student_id: user.student_id,
            course_id: course.course_id
        };

        this.apiService.enrollStudent(enrollmentData).subscribe({
            next: (res: any) => {
                alert(`✅ Successfully enrolled in ${course.name}!\n\nYou are now enrolled in ${this.enrolledCourseIds.length + 1} / 5 courses.`);
                this.enrolledCourseIds.push(course.course_id);
                this.loadGrades(); // Refresh grades
                this.cdr.detectChanges();
            },
            error: (err) => {
                console.error('Enrollment error:', err);
                const message = err.error?.message || 'Failed to enroll in course';
                alert(`❌ Enrollment Failed\n\n${message}`);
            }
        });
    }

    getStatusText(marks: number | null): string {
        if (marks === null) return 'Pending';
        return marks >= 40 ? 'Passed' : 'Failed';
    }

    getStatusColor(marks: number | null): string {
        if (marks === null) return 'status-pending';
        return marks >= 40 ? 'status-pass' : 'status-fail';
    }
}
