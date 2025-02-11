import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface Category {
  _id: string;
  name: string;
  description: string;
  created_at: string;
  created_by: string;
  updated_at: string;
  updated_by: string;
  usage_count: number;
  radar_quadrant?: number;
}

export interface CategoryResponse {
  success: boolean;
  data: Category[];
  detail: string | null;
  total: number;
  skip: number;
  limit: number;
}

export interface CategoryUpdatePayload {
  name: string;
  description?: string;
  radar_quadrant?: number;
}

@Injectable({
  providedIn: 'root'
})
export class CategoryService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getCategories(): Observable<CategoryResponse> {
    return this.http.get<CategoryResponse>(`${this.apiUrl}/categories/`);
  }

  getAllCategories(
    skip: number = 0, 
    limit: number = 10
  ): Observable<CategoryResponse> {
    const params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());

    return this.http.get<CategoryResponse>(`${this.apiUrl}/categories/`, { params });
  }

  updateCategory(categoryId: string, payload: CategoryUpdatePayload): Observable<CategoryResponse> {
    return this.http.put<CategoryResponse>(`${this.apiUrl}/categories/${categoryId}`, payload);
  }

  deleteCategory(categoryId: string): Observable<CategoryResponse> {
    return this.http.delete<CategoryResponse>(`${this.apiUrl}/categories/${categoryId}`);
  }
} 
