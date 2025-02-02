import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { StandardResponse } from '../interfaces/standard-response.interface';
import { Solution } from '../../shared/interfaces/solution.interface';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SolutionService {
  private apiUrl = `${environment.apiUrl}/solutions/`;

  constructor(private http: HttpClient) {}

  getSolutions(params: {
    skip?: number;
    limit?: number;
    category?: string;
    department?: string;
    team?: string;
    recommend_status?: 'BUY' | 'HOLD' | 'SELL';
    radar_status?: 'ADOPT' | 'TRIAL' | 'ASSESS' | 'HOLD';
    stage?: 'DEVELOPING' | 'UAT' | 'PRODUCTION' | 'DEPRECATED' | 'RETIRED';
    sort?: string;
  }): Observable<StandardResponse<Solution[]>> {
    let httpParams = new HttpParams()
      .set('skip', params.skip?.toString() || '0')
      .set('limit', params.limit?.toString() || '10')
      .set('review_status', 'APPROVED');

    if (params.category) httpParams = httpParams.set('category', params.category);
    if (params.department) httpParams = httpParams.set('department', params.department);
    if (params.team) httpParams = httpParams.set('team', params.team);
    if (params.recommend_status) httpParams = httpParams.set('recommend_status', params.recommend_status);
    if (params.radar_status) httpParams = httpParams.set('radar_status', params.radar_status);
    if (params.stage) httpParams = httpParams.set('stage', params.stage);
    if (params.sort) httpParams = httpParams.set('sort', params.sort);

    return this.http.get<StandardResponse<Solution[]>>(this.apiUrl, { params: httpParams });
  }

  getRecommendedSolutions(skip = 0, limit = 10): Observable<StandardResponse<Solution[]>> {
    return this.http.get<StandardResponse<Solution[]>>(
      `${this.apiUrl}`,
      {
        params: {
          skip: skip.toString(),
          limit: limit.toString(),
          recommend_status: 'BUY',
          sort: 'name',
          review_status: 'APPROVED'
        }
      }
    );
  }

  createSolution(solution: Partial<Solution>): Observable<StandardResponse<Solution>> {
    return this.http.post<StandardResponse<Solution>>(this.apiUrl, solution);
  }

  getNewSolutions(skip = 0, limit = 10): Observable<StandardResponse<Solution[]>> {
    return this.http.get<StandardResponse<Solution[]>>(
      `${this.apiUrl}`,
      {
        params: {
          skip: skip.toString(),
          limit: limit.toString(),
          sort: '-created_at',
          review_status: 'APPROVED'
        }
      }
    );
  }
} 