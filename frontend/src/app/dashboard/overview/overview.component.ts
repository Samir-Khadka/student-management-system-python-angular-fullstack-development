import { Component, inject, OnInit, ChangeDetectorRef, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Component({
    selector: 'app-dashboard-overview',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './overview.component.html',
    styleUrls: ['./overview.component.css']
})
export class OverviewComponent implements OnInit, AfterViewInit {
    private apiService = inject(ApiService);
    private authService = inject(AuthService);
    private cdr = inject(ChangeDetectorRef);

    isLoading = true;
    userRole = '';

    dashboardData = {
        totalStudents: 0,
        totalTeachers: 0,
        atRiskStudents: 0,
        averageGrade: 0
    };

    recentStudents: any[] = [];
    topPerformers: any[] = [];
    studentsNeedingAttention: any[] = [];
    gradeDistribution: number[] = [0, 0, 0, 0, 0, 0]; // 0-39, 40-49, 50-59, 60-69, 70-79, 80-100
    errors: any = {};

    ngOnInit() {
        const user = this.authService.getUser();
        this.userRole = user ? user.role : '';
        this.loadDashboardData();
    }

    ngAfterViewInit() {
        // Force change detection after view initialization
        setTimeout(() => {
            this.cdr.detectChanges();
        }, 0);
    }

    loadDashboardData() {
        this.isLoading = true;
        this.errors = {};

        const user = this.authService.getUser();

        // For teachers, fetch their courses and enrolled students
        if (this.userRole === 'teacher') {
            this.loadTeacherDashboard();
            return;
        }

        forkJoin({
            students: this.apiService.getStudents(1000, 0).pipe( // Fetch all for calc
                catchError(err => {
                    console.error('Failed to load students', err);
                    this.errors.students = true;
                    return of({ total: 0, students: [] });
                })
            ),
            teachers: this.apiService.getTeachers().pipe(
                catchError(err => {
                    console.error('Failed to load teachers', err);
                    this.errors.teachers = true;
                    return of({ count: 0 });
                })
            ),
            avgGrade: this.apiService.getAverageGrade().pipe(
                catchError(err => {
                    console.error('Failed to load average grade', err);
                    return of({ average_grade: 0 });
                })
            ),
            atRisk: this.apiService.getAtRiskStudents().pipe(
                catchError(err => {
                    console.error('Failed to load at-risk', err);
                    return of({ total_at_risk: 0 });
                })
            )
        }).subscribe({
            next: (results: any) => {
                const students = results.students.students || [];

                this.dashboardData = {
                    totalStudents: results.students.total || 0,
                    totalTeachers: results.teachers.count || 0,
                    atRiskStudents: results.atRisk.total_at_risk || 0,
                    averageGrade: results.avgGrade.average_grade || 0
                };

                this.processStudentData(students);

                this.recentStudents = students.slice(0, 5).map((s: any) => ({
                    name: s.name,
                    score: s.final_grade
                }));

                this.isLoading = false;
                this.cdr.detectChanges();
            },
            error: (err) => {
                console.error('Critical error loading dashboard', err);
                this.isLoading = false;
                this.cdr.detectChanges();
            }
        });
    }

    loadTeacherDashboard() {
        this.apiService.getCourses().subscribe({
            next: (res: any) => {
                const courses = res.courses || [];

                // Get all course IDs teacher teaches
                const courseIds = courses.map((c: any) => c.course_id);

                if (courseIds.length === 0) {
                    this.isLoading = false;
                    this.cdr.detectChanges();
                    return;
                }

                // For each course, get the students
                const studentRequests = courseIds.map((courseId: string) =>
                    this.apiService.getCourseStudents(courseId).pipe(
                        catchError(() => of({ students: [] }))
                    )
                );

                if (studentRequests.length === 0) {
                    this.isLoading = false;
                    this.cdr.detectChanges();
                    return;
                }

                (forkJoin(studentRequests) as any).subscribe({
                    next: (allResults: any[]) => {
                        // Flatten all students and remove duplicates
                        const allStudents: any[] = [];
                        const uniqueStudentIds = new Set<string>();

                        allResults.forEach(result => {
                            const students = result.students || [];
                            students.forEach((s: any) => {
                                if (!uniqueStudentIds.has(s.student_id)) {
                                    uniqueStudentIds.add(s.student_id);
                                    allStudents.push(s);
                                }
                            });
                        });

                        // Calculate average grade from all enrolled students
                        const totalGrade = allStudents.reduce((sum, s) => sum + (s.marks || 0), 0);
                        const avgGrade = allStudents.length > 0 ? totalGrade / allStudents.length : 0;

                        // Count students needing attention (marks < 40)
                        const needsAttention = allStudents.filter(s => (s.marks || 0) < 40).length;

                        this.dashboardData = {
                            totalStudents: allStudents.length,
                            totalTeachers: 0, // Not relevant for teachers
                            atRiskStudents: needsAttention,
                            averageGrade: avgGrade
                        };

                        this.processStudentData(allStudents);

                        this.topPerformers = [...allStudents]
                            .sort((a, b) => (b.marks || 0) - (a.marks || 0))
                            .slice(0, 5);

                        this.studentsNeedingAttention = allStudents
                            .filter((s: any) => (s.marks || 0) < 40)
                            .slice(0, 5);

                        this.isLoading = false;
                        this.cdr.detectChanges();
                    },
                    error: (err: any) => {
                        console.error('Error loading teacher dashboard', err);
                        this.isLoading = false;
                        this.cdr.detectChanges();
                    }
                });
            },
            error: (err) => {
                console.error('Error loading courses', err);
                this.isLoading = false;
                this.cdr.detectChanges();
            }
        });
    }

    processStudentData(students: any[]) {
        // Top Performers
        this.topPerformers = [...students]
            .sort((a, b) => b.final_grade - a.final_grade)
            .slice(0, 5);

        // Needs Attention
        this.studentsNeedingAttention = students
            .filter((s: any) => s.final_grade < 40)
            .slice(0, 5);

        // Grade Distribution
        const dist = [0, 0, 0, 0, 0, 0];
        students.forEach((s: any) => {
            const grade = s.final_grade;
            if (grade < 40) dist[0]++;
            else if (grade < 50) dist[1]++;
            else if (grade < 60) dist[2]++;
            else if (grade < 70) dist[3]++;
            else if (grade < 80) dist[4]++;
            else dist[5]++; // 80+
        });

        // Normalize for chart height (max 100%)
        // We will pass raw values to template and calculate height percentage there or here
        // For simplicity, let's keep raw counts
        this.gradeDistribution = dist;
    }

    getMaxDistribution() {
        return Math.max(...this.gradeDistribution, 1);
    }
}
