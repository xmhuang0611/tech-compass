import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface User {
  _id: string;
  email: string;
  username: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface StandardResponse<T> {
  success: boolean;
  data: T;
  detail: string | null;
  total: number | null;
  skip: number | null;
  limit: number | null;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl;
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  currentUser$ = this.currentUserSubject.asObservable();
  private tokenKey = 'auth_token';

  constructor(private http: HttpClient) {
    // Check if there's a stored token and fetch user info if exists
    const token = localStorage.getItem(this.tokenKey);
    if (token) {
      this.fetchCurrentUser().subscribe();
    }
  }

  login(username: string, password: string): Observable<LoginResponse> {
    const formData = new URLSearchParams();
    formData.set('username', username);
    formData.set('password', password);

    return this.http.post<LoginResponse>(`${this.apiUrl}/auth/login`, formData.toString(), {
      headers: new HttpHeaders().set('Content-Type', 'application/x-www-form-urlencoded')
    }).pipe(
      tap(response => {
        localStorage.setItem(this.tokenKey, response.access_token);
        this.fetchCurrentUser().subscribe();
      })
    );
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
    this.currentUserSubject.next(null);
  }

  fetchCurrentUser(): Observable<StandardResponse<User>> {
    return this.http.get<StandardResponse<User>>(`${this.apiUrl}/users/me`).pipe(
      tap(response => {
        if (response.success) {
          this.currentUserSubject.next(response.data);
        }
      })
    );
  }

  getAuthToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  isLoggedIn(): boolean {
    return !!this.getAuthToken();
  }
} 
