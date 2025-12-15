import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { ApiService } from '../services/api.service';
import { AuthService } from '../services/auth.service';
import { ProfileModalComponent } from '../profile/profile-modal.component';

@Component({
    selector: 'app-dashboard',
    standalone: true,
    imports: [CommonModule, RouterModule, ProfileModalComponent],
    templateUrl: './dashboard.component.html',
    styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
    private apiService = inject(ApiService);
    private authService = inject(AuthService);
    private router = inject(Router);

    // ... existing properties
    user: any;
    isDropdownOpen = false;
    isSidebarOpen = true; // Open by default
    showProfileModal = false;
    isUploadingCV = false;

    ngOnInit() {
        this.user = this.authService.getUser();
        if (!this.user) {
            this.router.navigate(['/auth']);
            return;
        }
    }

    // ... existing methods

    onCVSelected(event: any) {
        const file = event.target.files[0];
        if (file) {
            this.uploadCV(file);
        }
    }

    uploadCV(file: File) {
        this.isUploadingCV = true;
        this.apiService.uploadCV(file).subscribe({
            next: (res: any) => {
                this.isUploadingCV = false;
                alert('CV uploaded successfully! Please wait for admin approval.');
                // Update local user state if needed to show "Pending Approval" instead of "Upload CV"
                // But keeping it simple: banner can say "Upload/Update CV"
            },
            error: (err: any) => {
                this.isUploadingCV = false;
                alert('Failed to upload CV: ' + (err.error?.message || err.message));
            }
        });
    }

    toggleDropdown() {
        this.isDropdownOpen = !this.isDropdownOpen;
    }

    openProfile() {
        this.showProfileModal = true;
        this.isDropdownOpen = false;
    }

    closeProfile() {
        this.showProfileModal = false;
    }

    onUserUpdated(updatedUser: any) {
        this.user = updatedUser;
    }

    toggleSidebar() {
        this.isSidebarOpen = !this.isSidebarOpen;
    }


    logout() {
        this.authService.logout();
        this.router.navigate(['/']); // Redirect to landing page
    }

    getInitials(name: string): string {
        if (!name) return 'U';
        return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
    }

    getProfileUrl(path: string | null): string | null {
        return this.apiService.getProfilePictureUrl(path);
    }
}
