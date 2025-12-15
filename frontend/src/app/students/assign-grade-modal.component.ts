import { Component, EventEmitter, Input, Output, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../services/api.service';

@Component({
    selector: 'app-assign-grade-modal',
    standalone: true,
    imports: [CommonModule, FormsModule],
    template: `
    <div class="modal-overlay" (click)="close.emit()">
        <div class="modal-content glass-card" (click)="$event.stopPropagation()">
            <div class="modal-header">
                <h2>Assign Grade</h2>
                <button class="close-btn" (click)="close.emit()">&times;</button>
            </div>
            
            <div class="modal-body">
                <div class="student-info">
                    <h3>{{ student?.name }}</h3>
                    <span class="student-id">{{ student?.student_id }}</span>
                </div>

                <div class="form-group" *ngIf="availableCourses.length > 1">
                    <label>Select Course</label>
                    <select [(ngModel)]="selectedCourseId" (change)="onCourseChange()">
                        <option *ngFor="let course of availableCourses" [value]="course.course_id">
                            {{ course.course_name }}
                        </option>
                    </select>
                </div>
                
                <div class="form-group" *ngIf="availableCourses.length === 1">
                    <label>Course</label>
                    <div class="static-value">{{ availableCourses[0].course_name }}</div>
                </div>

                <div class="form-group">
                    <label>Marks (0-100)</label>
                    <input 
                        type="number" 
                        min="0" 
                        max="100" 
                        [(ngModel)]="marks" 
                        placeholder="Enter marks">
                </div>

                <div class="actions">
                    <button class="btn-cancel" (click)="close.emit()">Cancel</button>
                    <button class="btn-save" (click)="saveGrade()" [disabled]="isValid()">
                        <i class="fas" [class.fa-spinner]="saving" [class.fa-spin]="saving" [class.fa-save]="!saving"></i>
                        {{ saving ? 'Saving...' : 'Save Grade' }}
                    </button>
                </div>
            </div>
        </div>
    </div>
    `,
    styles: [`
        .modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); backdrop-filter: blur(5px); z-index: 1000; display: flex; align-items: center; justify-content: center; }
        .modal-content { background: #1e293b; width: 90%; max-width: 400px; border-radius: 1rem; border: 1px solid rgba(255,255,255,0.1); padding: 0; overflow: hidden; animation: slideIn 0.3s ease-out; }
        .modal-header { padding: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.02); }
        .modal-header h2 { margin: 0; color: white; font-size: 1.25rem; }
        .close-btn { background: none; border: none; color: #94a3b8; font-size: 1.5rem; cursor: pointer; }
        .close-btn:hover { color: white; }
        
        .modal-body { padding: 1.5rem; }
        
        .student-info { margin-bottom: 1.5rem; text-align: center; }
        .student-info h3 { margin: 0; color: white; font-size: 1.5rem; }
        .student-id { color: #8b5cf6; font-family: monospace; }
        
        .form-group { margin-bottom: 1.25rem; }
        .form-group label { display: block; color: #94a3b8; margin-bottom: 0.5rem; font-size: 0.875rem; }
        .form-group select, .form-group input { width: 100%; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1); color: white; padding: 0.75rem; border-radius: 0.5rem; }
        .static-value { color: white; font-weight: 500; padding: 0.75rem; background: rgba(255,255,255,0.05); border-radius: 0.5rem; }
        
        .actions { display: flex; gap: 1rem; margin-top: 2rem; }
        .actions button { flex: 1; padding: 0.75rem; border-radius: 0.5rem; border: none; font-weight: 600; cursor: pointer; }
        .btn-cancel { background: transparent; border: 1px solid rgba(255,255,255,0.1) !important; color: #cbd5e1; }
        .btn-save { background: #8b5cf6; color: white; display: flex; align-items: center; justify-content: center; gap: 0.5rem; }
        .btn-save:disabled { opacity: 0.5; cursor: not-allowed; }
        
        @keyframes slideIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    `]
})
export class AssignGradeModalComponent implements OnInit {
    @Input() student: any;
    @Input() enrolledCourses: any[] = []; // List of {course_id, course_name, current_marks}
    @Output() close = new EventEmitter<void>();
    @Output() saved = new EventEmitter<void>();

    private apiService = inject(ApiService);

    selectedCourseId: string = '';
    marks: number | null = null;
    saving = false;
    availableCourses: any[] = [];

    ngOnInit() {
        if (this.enrolledCourses && this.enrolledCourses.length > 0) {
            this.availableCourses = this.enrolledCourses;
            this.selectedCourseId = this.availableCourses[0].course_id;
            this.marks = this.availableCourses[0].currrent_marks || null;
        }
    }

    onCourseChange() {
        const course = this.availableCourses.find(c => c.course_id === this.selectedCourseId);
        if (course) {
            this.marks = course.current_marks || null;
        }
    }

    saveGrade() {
        if (this.marks === null || this.marks < 0 || this.marks > 100) return;

        this.saving = true;
        this.apiService.gradeStudent({
            course_id: this.selectedCourseId,
            student_id: this.student.student_id,
            marks: this.marks
        }).subscribe({
            next: () => {
                this.saving = false;
                this.saved.emit();
                this.close.emit();
            },
            error: (err) => {
                this.saving = false;
                alert('Error saving grade');
                console.error(err);
            }
        });
    }

    isValid(): boolean {
        return this.marks === null || this.marks < 0 || this.marks > 100 || this.saving || !this.selectedCourseId;
    }
}
