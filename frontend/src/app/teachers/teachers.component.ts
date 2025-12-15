import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../services/api.service';
import { AuthService } from '../services/auth.service';
import { AddTeacherModalComponent } from './add-teacher-modal.component';

import { FormsModule } from '@angular/forms';

@Component({
    selector: 'app-teachers',
    standalone: true,
    imports: [CommonModule, AddTeacherModalComponent, FormsModule],
    template: `
    <div class="content-padding">
        <div class="page-header">
            <div class="page-title">
                <h1>Teachers</h1>
                <span class="page-subtitle">Manage faculty members</span>
            </div>
            <button *ngIf="isAdmin" class="btn-primary" (click)="openAddModal()">
                <i class="fas fa-plus"></i> Add Teacher
            </button>
        </div>

        <div class="content-card mb-4" *ngIf="isAdmin && pendingTeachers.length > 0">
            <div class="card-header highlight">
                <h3><i class="fas fa-clock"></i> Pending Approvals ({{pendingTeachers.length}})</h3>
            </div>
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Subject</th>
                            <th>Email</th>
                            <th>CV</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr *ngFor="let teacher of pendingTeachers">
                            <td class="font-medium">{{teacher.full_name || teacher.username}}</td>
                            <td><span class="badge">{{teacher.subject}}</span></td>
                            <td>{{teacher.email}}</td>
                            <td>
                                <a *ngIf="teacher.cv_url" [href]="teacher.cv_url" target="_blank" class="cv-link">
                                    <i class="fas fa-file-pdf"></i> View CV
                                </a>
                                <span *ngIf="!teacher.cv_url" class="text-muted">No CV</span>
                            </td>
                            <td>
                                <button class="btn-success small" (click)="approveTeacher(teacher.user_id)">
                                    <i class="fas fa-check"></i> Approve
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div class="content-card">
            <div class="card-header">
                <h3>Teacher List ({{filteredTeachers.length}})</h3>
                <div class="filters">
                    <div class="search-box">
                        <i class="fas fa-search"></i>
                        <input type="text" placeholder="Search teachers..." [(ngModel)]="searchQuery">
                    </div>
                    <select class="subject-select" [(ngModel)]="selectedSubject">
                        <option value="">All Subjects</option>
                        <option *ngFor="let sub of uniqueSubjects" [value]="sub">{{sub}}</option>
                    </select>
                </div>
            </div>
            
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Subject</th>
                            <th>Email</th>
                            <th *ngIf="isAdmin">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr *ngFor="let teacher of filteredTeachers">
                            <td>{{teacher.teacher_id}}</td>
                            <td class="font-medium">{{teacher.name}}</td>
                            <td>
                                <span class="badge">{{teacher.subject}}</span>
                            </td>
                            <td>{{teacher.email}}</td>
                            <td *ngIf="isAdmin">
                                <button class="btn-icon" (click)="openEditModal(teacher)"><i class="fas fa-edit"></i></button>
                                <button class="btn-icon" (click)="deleteTeacher(teacher.teacher_id)">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <app-add-teacher-modal 
        *ngIf="showModal" 
        [teacher]="selectedTeacher"
        (close)="closeModal()" 
        (saved)="loadTeachers()">
    </app-add-teacher-modal>
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
        .btn-icon { background: none; border: none; color: #94a3b8; cursor: pointer; padding: 0.5rem; }
        .btn-icon:hover { color: white; }
        .font-medium { font-weight: 500; color: white; }
        .badge { background: rgba(139, 92, 246, 0.1); color: #8b5cf6; padding: 0.25rem 0.5rem; border-radius: 9999px; font-size: 0.875rem; }
        .mb-4 { margin-bottom: 1.5rem; }
        .card-header.highlight h3 { color: #fbbf24; }
        .cv-link { color: #60a5fa; text-decoration: none; display: flex; align-items: center; gap: 0.5rem; }
        .cv-link:hover { text-decoration: underline; }
        .text-muted { color: #64748b; font-style: italic; }
        .btn-success { background-color: #10b981; color: white; border: none; padding: 0.25rem 0.75rem; border-radius: 0.375rem; cursor: pointer; display: flex; align-items: center; gap: 0.5rem; }
        .btn-success:hover { background-color: #059669; }
        .btn-success:hover { background-color: #059669; }
        
        /* Filter Styles */
        .card-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }
        .filters { display: flex; gap: 1rem; align-items: center; }
        .search-box { position: relative; }
        .search-box i { position: absolute; left: 0.75rem; top: 50%; transform: translateY(-50%); color: #94a3b8; }
        .search-box input { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white; padding: 0.5rem 1rem 0.5rem 2.25rem; border-radius: 0.5rem; outline: none; width: 200px; }
        .search-box input:focus { border-color: #8b5cf6; }
        .subject-select { background: #1e293b; color: white; border: 1px solid rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 0.5rem; outline: none; cursor: pointer; }
        .subject-select:focus { border-color: #8b5cf6; }
    `]
})
export class TeachersComponent implements OnInit {
    private apiService = inject(ApiService);
    private authService = inject(AuthService);
    private cdr = inject(ChangeDetectorRef);

    teachers: any[] = [];
    totalTeachers = 0;
    showModal = false;
    selectedTeacher: any = null;

    // Filter Logic
    searchQuery: string = '';
    selectedSubject: string = '';

    get uniqueSubjects(): string[] {
        const subjects = new Set(this.teachers.map(t => t.subject));
        return Array.from(subjects).sort();
    }

    get filteredTeachers() {
        return this.teachers.filter(t => {
            const matchesSearch = !this.searchQuery ||
                t.name?.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                t.teacher_id?.toLowerCase().includes(this.searchQuery.toLowerCase());

            const matchesSubject = !this.selectedSubject || t.subject === this.selectedSubject;

            return matchesSearch && matchesSubject;
        });
    }

    // Pending Teachers Logic
    pendingTeachers: any[] = [];

    ngOnInit() {
        this.loadTeachers();
        if (this.isAdmin) {
            this.loadPendingTeachers();
        }
    }

    get isAdmin(): boolean {
        return this.authService.isAdmin();
    }

    loadTeachers() {
        this.apiService.getTeachers().subscribe({
            next: (res: any) => {
                this.teachers = res.teachers;
                this.totalTeachers = res.total;
                this.cdr.detectChanges();
            },
            error: (err: any) => console.error(err)
        });
    }

    loadPendingTeachers() {
        this.apiService.getPendingTeachers().subscribe({
            next: (res: any) => {
                this.pendingTeachers = res.pending_teachers || [];
                this.cdr.detectChanges();
            },
            error: (err: any) => console.error('Error loading pending teachers', err)
        });
    }

    approveTeacher(userId: string) {
        if (confirm('Approve this teacher account?')) {
            this.apiService.approveTeacher(userId).subscribe({
                next: () => {
                    alert('Teacher approved successfully');
                    this.loadPendingTeachers();
                    this.loadTeachers(); // Refresh main list
                },
                error: (err: any) => alert('Failed to approve: ' + (err.error?.message || err.message))
            });
        }
    }

    openAddModal() {
        this.selectedTeacher = null;
        this.showModal = true;
    }

    openEditModal(teacher: any) {
        this.selectedTeacher = teacher;
        this.showModal = true;
    }

    closeModal() {
        this.showModal = false;
        this.selectedTeacher = null;
    }

    deleteTeacher(teacherId: string) {
        if (confirm('Are you sure you want to delete this teacher?')) {
            this.apiService.deleteTeacher(teacherId).subscribe({
                next: () => {
                    this.loadTeachers();
                },
                error: (err: any) => console.error(err)
            });
        }
    }
}
