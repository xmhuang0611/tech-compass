import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { SolutionResponse } from '../../shared/interfaces/solution.interface';

@Injectable({
  providedIn: 'root'
})
export class SolutionService {
  private apiUrl = 'http://127.0.0.1:8000/api';

  constructor(private http: HttpClient) {}

  getRecommendedSolutions(skip = 0, limit = 10): Observable<SolutionResponse> {
    return this.http.get<SolutionResponse>(
      `${this.apiUrl}/solutions/`,
      {
        params: {
          skip: skip.toString(),
          limit: limit.toString(),
          recommend_status: 'BUY',
          sort: 'name'
        }
      }
    );
  }

  getNewSolutions(skip = 0, limit = 10): Observable<SolutionResponse> {
    return this.http.get<SolutionResponse>(
      `${this.apiUrl}/solutions/`,
      {
        params: {
          skip: skip.toString(),
          limit: limit.toString(),
          sort: '-created_at'
        }
      }
    );
  }
} 