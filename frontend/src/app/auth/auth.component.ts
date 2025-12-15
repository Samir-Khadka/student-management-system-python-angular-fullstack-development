import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { ApiService } from '../services/api.service';

@Component({
    selector: 'app-auth',
    standalone: true,
    imports: [CommonModule, FormsModule, RouterModule],
    templateUrl: './auth.component.html',
    styleUrls: ['./auth.component.css']
})
export class AuthComponent implements OnInit {
    private authService = inject(AuthService);
    private apiService = inject(ApiService);
    private router = inject(Router);

    isLoginMode = true;
    isLoading = false;
    availableCourses: any[] = [];

    loginData = { username: '', password: '' };
    registerData = {
        username: '',
        email: '',
        password: '',
        full_name: '',
        role: '',
        student_id: '',
        teacher_id: '', // Added Teacher ID
        subject: '', // Added Subject
        courses: [] as string[]
    };

    ngOnInit() {
        this.loadCourses();
    }

    loadCourses() {
        this.apiService.getPublicCourses().subscribe({
            next: (res: any) => {
                this.availableCourses = res.courses || [];
            }
        });
    }

    toggleMode() {
        this.isLoginMode = !this.isLoginMode;
    }

    toggleCourse(courseId: string) {
        const index = this.registerData.courses.indexOf(courseId);
        if (index > -1) {
            this.registerData.courses.splice(index, 1);
        } else {
            if (this.registerData.courses.length >= 5) {
                alert('You can only select up to 5 courses.');
                return;
            }
            this.registerData.courses.push(courseId);
        }
    }

    onLogin() {
        this.isLoading = true;
        this.authService.login(this.loginData).subscribe({
            next: () => {
                this.isLoading = false;
                this.router.navigate(['/dashboard']);
            },
            error: (err) => {
                this.isLoading = false;
                alert('Login failed: ' + (err.error?.message || err.message));
            }
        });
    }

    onRegister() {
        this.isLoading = true;
        this.authService.register(this.registerData).subscribe({
            next: () => {
                this.isLoading = false;
                if (this.registerData.role === 'teacher') {
                    alert('Registration successful! Your account is pending approval. Please login to upload your CV.');
                } else {
                    alert('Registration successful! Please login.');
                }
                this.isLoginMode = true;
            },
            error: (err) => {
                this.isLoading = false;
                alert('Registration failed: ' + (err.error?.message || err.message));
            }
        });
    }
}
