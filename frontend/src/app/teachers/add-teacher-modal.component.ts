import { Component, EventEmitter, Output, Input, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../services/api.service';

@Component({
    selector: 'app-add-teacher-modal',
    standalone: true,
    imports: [CommonModule, FormsModule],
    template: `
    <div class="modal-overlay" (click)="close.emit()">
        <div class="modal-content" (click)="$event.stopPropagation()">
            <div class="modal-header">
                <h2>{{ isEditMode ? 'Edit Teacher' : 'Add New Teacher' }}</h2>
                <button class="close-btn" (click)="close.emit()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            
            <div class="modal-body">
                <form (ngSubmit)="save()">
                    <div class="form-group">
                        <label>Teacher ID</label>
                        <input type="text" [(ngModel)]="data.teacher_id" name="teacher_id" required placeholder="T001" [disabled]="isEditMode">
                    </div>
                    
                    <div class="form-group">
                        <label>Full Name</label>
                        <input type="text" [(ngModel)]="data.name" name="name" required placeholder="Jane Smith">
                    </div>
                    
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" [(ngModel)]="data.email" name="email" required placeholder="jane@school.com">
                    </div>

                     <div class="form-group">
                        <label>Subject</label>
                        <input type="text" [(ngModel)]="data.subject" name="subject" required placeholder="Mathematics">
                    </div>

                    <div class="modal-actions">
                        <button type="button" class="btn-cancel" (click)="close.emit()">Cancel</button>
                        <button type="submit" class="btn-save" [disabled]="isLoading">
                            {{ isLoading ? 'Saving...' : (isEditMode ? 'Update Teacher' : 'Save Teacher') }}
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
        .form-group input, .form-group select { width: 100%; padding: 0.75rem; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 0.5rem; color: white; font-family: inherit; }
        .form-group input:focus, .form-group select:focus { outline: none; border-color: #8b5cf6; }
        .form-group input:disabled { opacity: 0.5; cursor: not-allowed; }
        .modal-actions { display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1.5rem; }
        .btn-cancel { background: transparent; border: 1px solid rgba(255,255,255,0.1); color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; cursor: pointer; }
        .btn-save { background: #8b5cf6; border: none; color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; cursor: pointer; }
        .btn-save:disabled { opacity: 0.5; cursor: not-allowed; }
    `]
})
export class AddTeacherModalComponent implements OnInit {
    @Input() teacher: any = null;
    @Output() close = new EventEmitter<void>();
    @Output() saved = new EventEmitter<void>();

    private apiService = inject(ApiService);

    isLoading = false;
    isEditMode = false;
    data: any = {};

    ngOnInit() {
        if (this.teacher) {
            this.isEditMode = true;
            this.data = { ...this.teacher };
        }
    }

    save() {
        if (!this.data.teacher_id || !this.data.name || !this.data.email) {
            alert('Please fill in required fields');
            return;
        }

        this.isLoading = true;
        const request$ = this.isEditMode
            ? this.apiService.updateTeacher(this.data.teacher_id, this.data)
            : this.apiService.createTeacher(this.data);

        request$.subscribe({
            next: () => {
                this.isLoading = false;
                this.saved.emit();
                this.close.emit();
            },
            error: (err: any) => {
                console.error(err);
                this.isLoading = false;
                alert(err.error?.message || 'Failed to save teacher');
            }
        });
    }
}
