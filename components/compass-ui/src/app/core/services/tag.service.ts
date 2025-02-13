import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface Tag {
  _id: string;
  name: string;
  description: string;
  usage_count: number;
  created_at: string;
  created_by: string;
  updated_at: string;
  updated_by: string;
}

export interface TagResponse {
  success: boolean;
  data: Tag[];
  detail: string;
  total: number;
  skip: number;
  limit: number;
}

export interface SingleTagResponse {
  success: boolean;
  data: Tag;
  detail: string;
}

@Injectable({
  providedIn: 'root'
})
export class TagService {
  private apiUrl = `${environment.apiUrl}/tags`;

  constructor(private http: HttpClient) {}

  getTags(): Observable<TagResponse> {
    return this.http.get<TagResponse>(`${this.apiUrl}/?limit=100`);
  }

  getAllTags(skip: number = 0, limit: number = 10): Observable<TagResponse> {
    return this.http.get<TagResponse>(`${this.apiUrl}/?skip=${skip}&limit=${limit}`);
  }

  getTag(id: string): Observable<SingleTagResponse> {
    return this.http.get<SingleTagResponse>(`${this.apiUrl}/${id}`);
  }

  updateTag(id: string, data: Partial<Tag>): Observable<SingleTagResponse> {
    return this.http.put<SingleTagResponse>(`${this.apiUrl}/${id}`, data);
  }

  deleteTag(id: string): Observable<SingleTagResponse> {
    return this.http.delete<SingleTagResponse>(`${this.apiUrl}/${id}`);
  }
} 