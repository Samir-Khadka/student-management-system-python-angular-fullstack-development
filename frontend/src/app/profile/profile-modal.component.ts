import { Component, EventEmitter, Input, Output, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../services/api.service';

@Component({
    selector: 'app-profile-modal',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './profile-modal.component.html',
    styleUrls: ['./profile-modal.component.css']
})
export class ProfileModalComponent implements OnInit {
    @Input() user: any;
    @Output() close = new EventEmitter<void>();
    @Output() userUpdated = new EventEmitter<any>();

    private apiService = inject(ApiService);

    isEditing = false;
    editData: any = {};
    isLoading = false;

    // For file upload
    selectedFile: File | null = null;
    previewUrl: string | null = null;
    removePicture = false;

    ngOnInit() {
        this.resetForm();
    }

    resetForm() {
        this.editData = {
            full_name: this.user?.full_name || this.user?.username,
            email: this.user?.email,
            role: this.user?.role
        };
        // Reset preview to current user state
        this.previewUrl = this.user?.profile_picture || null;
        this.isEditing = false;
        this.removePicture = false;
    }

    onClose() {
        this.close.emit();
    }

    toggleEdit() {
        this.isEditing = !this.isEditing;
        if (!this.isEditing) {
            // Cancel -> reset
            this.resetForm();
        }
    }

    triggerFileInput() {
        document.getElementById('profileFileInput')?.click();
    }

    onFileSelected(event: any) {
        const file = event.target.files[0];
        if (file) {
            // Client-side Validation
            const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
            if (!allowedTypes.includes(file.type)) {
                alert('Invalid file type. Please upload an image (PNG, JPG, GIF, WebP).');
                event.target.value = ''; // Reset input
                return;
            }
            if (file.size > 5 * 1024 * 1024) { // 5MB
                alert('File is too large. Maximum size is 5MB.');
                event.target.value = ''; // Reset input
                return;
            }

            this.selectedFile = file;
            this.removePicture = false;

            // Create preview
            const reader = new FileReader();
            reader.onload = (e: any) => {
                this.previewUrl = e.target.result as string;
            };
            reader.readAsDataURL(file);

            // Immediate Upload
            this.uploadFile(file);

            // Reset input to allow re-upload of same file
            event.target.value = '';
        }
    }

    uploadFile(file: File) {
        this.apiService.uploadProfilePicture(file).subscribe({
            next: (res: any) => {
                this.previewUrl = res.profile_picture;
                // Update parent/local user object immediately
                this.user.profile_picture = res.profile_picture;
                this.userUpdated.emit(this.user);
            },
            error: (err) => {
                console.error('Upload failed', err);
                alert('Failed to upload: ' + (err.error?.error || 'Unknown error'));
            }
        });
    }

    onRemovePicture() {
        if (confirm('Are you sure you want to remove your profile picture?')) {
            this.apiService.removeProfilePicture().subscribe({
                next: () => {
                    this.previewUrl = null;
                    this.user.profile_picture = null;
                    this.userUpdated.emit(this.user);
                    alert('Profile picture removed');
                },
                error: (err) => {
                    console.error('Remove failed', err);
                    alert('Failed to remove profile picture');
                }
            });
        }
    }

    saveProfile() {
        this.isLoading = true;

        // Only update text data here
        const updatePayload: any = { ...this.editData };

        this.apiService.updateProfile(updatePayload).subscribe({
            next: (response: any) => {
                this.isLoading = false;
                this.isEditing = false;

                // Construct final user object - ensure we keep the current profile picture
                const finalUser = {
                    ...response.user,
                    profile_picture: this.user.profile_picture
                };

                this.userUpdated.emit(finalUser);
            },
            error: (err) => {
                console.error('Profile update failed', err);
                this.isLoading = false;
                alert('Failed to update profile info');
            }
        });
    }

    getInitials(name: string): string {
        if (!name) return 'U';
        return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
    }

    getProfileUrl(path: string | null): string | null {
        return this.apiService.getProfilePictureUrl(path);
    }
}
