import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { StandardResponse } from '../interfaces/standard-response.interface';

export interface Tag {
  _id: string;
  name: string;
  description: string;
  usage_count: number;
  created_at: string;
  updated_at: string;
  created_by: string;
  updated_by: string;
}

@Injectable({
  providedIn: 'root'
})
export class TagService {
  private apiUrl = `${environment.apiUrl}/tags/`;

  constructor(private http: HttpClient) {}

  getTags(): Observable<StandardResponse<Tag[]>> {
    return this.http.get<StandardResponse<Tag[]>>(this.apiUrl);
  }
} 