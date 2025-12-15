import { Component, EventEmitter, Input, Output, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../services/api.service';

@Component({
    selector: 'app-gradebook-modal',
    standalone: true,
    imports: [CommonModule, FormsModule],
    template: `
    <div class="modal-overlay" (click)="close.emit()">
        <div class="modal-content" (click)="$event.stopPropagation()">
            <div class="modal-header">
                <h2>Gradebook: {{courseName}}</h2>
                <button class="close-btn" (click)="close.emit()">&times;</button>
            </div>
            
            <div class="modal-body">
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>STUDENT</th>
                                <th>ID</th>
                                <th>AGE</th>
                                <th>ABSENCES</th>
                                <th>MARKS (0-100)</th>
                                <th>ACTION</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr *ngFor="let student of enrolledStudents">
                                <td class="student-name">{{student.student_name}}</td>
                                <td class="student-id">{{student.student_id}}</td>
                                <td>{{student.age}}</td>
                                <td>{{student.absences}}</td>
                                <td>
                                    <input 
                                        type="number" 
                                        min="0" 
                                        max="100" 
                                        [(ngModel)]="student.tempMarks" 
                                        class="mark-input"
                                        [class.has-grade]="student.marks !== null"
                                        placeholder="--"
                                    >
                                </td>
                                <td>
                                    <button 
                                        class="btn-save" 
                                        (click)="saveGrade(student)"
                                        [disabled]="student.saving || isInvalid(student.tempMarks)">
                                        <i class="fas" [ngClass]="student.saving ? 'fa-spinner fa-spin' : 'fa-save'"></i>
                                        {{ student.marks !== null ? 'Update' : 'Assign' }}
                                    </button>
                                </td>
                            </tr>
                            <tr *ngIf="enrolledStudents.length === 0">
                                <td colspan="6" class="empty-state">No students enrolled in this course.</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    `,
    styles: [`
        .modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); backdrop-filter: blur(5px); z-index: 1000; display: flex; align-items: center; justify-content: center; animation: fadeIn 0.2s ease-out; }
        .modal-content { background: #1e293b; width: 90%; max-width: 800px; max-height: 85vh; border-radius: 1rem; border: 1px solid rgba(255,255,255,0.1); display: flex; flex-direction: column; animation: slideIn 0.3s ease-out; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04); }
        .modal-header { padding: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; align-items: center; }
        .modal-header h2 { color: white; font-size: 1.5rem; font-weight: 600; margin: 0; }
        .close-btn { background: none; border: none; color: #94a3b8; font-size: 2rem; cursor: pointer; line-height: 1; transition: color 0.2s; }
        .close-btn:hover { color: white; }
        
        .modal-body { padding: 1.5rem; overflow-y: auto; }
        
        .table-container { overflow-x: auto; }
        .data-table { width: 100%; border-collapse: separate; border-spacing: 0; color: #cbd5e1; }
        .data-table th { text-align: left; padding: 1rem; background: rgba(255,255,255,0.03); color: #94a3b8; font-weight: 600; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .data-table td { padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.05); vertical-align: middle; }
        .data-table tr:hover { background: rgba(255,255,255,0.02); }
        
        .student-name { color: white; font-weight: 500; }
        .student-id { font-family: monospace; color: #94a3b8; }
        
        .mark-input { background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1); color: white; padding: 0.5rem; border-radius: 0.5rem; width: 80px; text-align: center; font-weight: 600; transition: all 0.2s; }
        .mark-input:focus { border-color: #8b5cf6; outline: none; box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2); }
        .mark-input.has-grade { border-color: rgba(16, 185, 129, 0.3); color: #10b981; }
        
        .btn-save { background: #8b5cf6; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.5rem; cursor: pointer; font-size: 0.875rem; font-weight: 500; display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s; }
        .btn-save:hover:not(:disabled) { background: #7c3aed; transform: translateY(-1px); }
        .btn-save:disabled { opacity: 0.5; cursor: not-allowed; filter: grayscale(1); }
        
        .empty-state { text-align: center; padding: 3rem; color: #94a3b8; }

        /* Remove spin buttons from number input */
        input[type=number]::-webkit-inner-spin-button, 
        input[type=number]::-webkit-outer-spin-button { 
            -webkit-appearance: none; 
            margin: 0; 
        }

        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slideIn { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
    `]
})
export class GradebookModalComponent implements OnInit {
    @Input() courseId: string = '';
    @Input() courseName: string = '';
    @Output() close = new EventEmitter<void>();

    private apiService = inject(ApiService);

    enrolledStudents: any[] = [];
    loading = true;

    ngOnInit() {
        this.loadStudents();
    }

    loadStudents() {
        this.loading = true;
        this.apiService.getCourseStudents(this.courseId).subscribe({
            next: (res: any) => {
                this.enrolledStudents = res.students.map((s: any) => ({
                    ...s,
                    tempMarks: s.marks, // Initialize tempMarks with existing marks
                    saving: false
                }));
                this.loading = false;
            },
            error: (err) => {
                console.error(err);
                this.loading = false;
            }
        });
    }

    saveGrade(student: any) {
        if (this.isInvalid(student.tempMarks)) return;

        student.saving = true;
        const payload = {
            course_id: this.courseId,
            student_id: student.student_id,
            marks: student.tempMarks
        };

        this.apiService.gradeStudent(payload).subscribe({
            next: () => {
                student.marks = student.tempMarks; // Update confirmed marks
                student.saving = false;
                // Optional: Show success toast
            },
            error: (err) => {
                console.error(err);
                alert('Failed to save grade');
                student.saving = false;
            }
        });
    }

    isInvalid(marks: any): boolean {
        return marks === null || marks === '' || marks < 0 || marks > 100;
    }
}
