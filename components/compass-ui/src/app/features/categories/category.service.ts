import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { CategoryResponse } from './category.interface';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class CategoryService {
  private readonly baseUrl = `${environment.apiUrl}/categories`;

  constructor(private http: HttpClient) {}

  getCategories(skip: number = 0, limit: number = 20): Observable<CategoryResponse> {
    return this.http.get<CategoryResponse>(`${this.baseUrl}/?skip=${skip}&limit=${limit}`);
  }
} 