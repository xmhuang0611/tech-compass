import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface DepartmentResponse {
  success: boolean;
  data: string[];
  detail: string | null;
  total: number;
  skip: number;
  limit: number;
}

@Injectable({
  providedIn: 'root'
})
export class DepartmentService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getDepartments(): Observable<DepartmentResponse> {
    return this.http.get<DepartmentResponse>(`${this.apiUrl}/solutions/departments`);
  }
} 