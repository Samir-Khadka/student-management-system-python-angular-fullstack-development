import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable, tap } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private http = inject(HttpClient);
    private apiUrl = environment.apiUrl;
    private readonly TOKEN_KEY = 'auth_token';
    private readonly USER_KEY = 'user_data';

    login(credentials: any): Observable<any> {
        return this.http.post(`${this.apiUrl}/auth/login`, credentials).pipe(
            tap((response: any) => {
                if (response.access_token) {
                    this.saveToken(response.access_token);
                    this.saveUser(response.user);
                }
            })
        );
    }

    register(userData: any): Observable<any> {
        return this.http.post(`${this.apiUrl}/auth/register`, userData);
    }

    logout() {
        localStorage.removeItem(this.TOKEN_KEY);
        localStorage.removeItem(this.USER_KEY);
    }

    private saveToken(token: string) {
        localStorage.setItem(this.TOKEN_KEY, token);
    }

    private saveUser(user: any) {
        localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    }

    getUser(): any {
        const user = localStorage.getItem(this.USER_KEY);
        return user ? JSON.parse(user) : null;
    }

    isAuthenticated(): boolean {
        return !!localStorage.getItem(this.TOKEN_KEY);
    }

    getUserRole(): string {
        const user = this.getUser();
        return user ? user.role : '';
    }

    isAdmin(): boolean {
        return this.getUserRole() === 'admin';
    }

    isTeacher(): boolean {
        return this.getUserRole() === 'teacher';
    }

    isStudent(): boolean {
        return this.getUserRole() === 'student';
    }
}
