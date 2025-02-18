import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { environment } from "../../../environments/environment";

export interface Rating {
  _id: string;
  score: number;
  comment?: string;
  username: string;
  full_name: string;
  created_at: string;
  solution_slug: string;
  is_adopted_user?: boolean;
  created_by?: string;
  updated_at?: string;
  updated_by?: string;
}

export interface RatingResponse {
  success: boolean;
  data: Rating[];
  total: number;
}

@Injectable({
  providedIn: "root",
})
export class RatingService {
  constructor(private http: HttpClient) {}

  // Get ratings for a specific solution
  getSolutionRatings(
    slug: string,
    skip: number = 0,
    limit: number = 10
  ): Observable<RatingResponse> {
    return this.http.get<RatingResponse>(
      `${environment.apiUrl}/ratings/solution/${slug}?skip=${skip}&limit=${limit}`
    );
  }

  // Get all ratings (admin only)
  getAllRatings(
    skip: number = 0,
    limit: number = 10,
    filters?: {
      solution_slug?: string;
      score?: number;
    }
  ): Observable<RatingResponse> {
    let url = `${environment.apiUrl}/ratings/?skip=${skip}&limit=${limit}`;
    
    if (filters) {
      if (filters.solution_slug) {
        url += `&solution_slug=${filters.solution_slug}`;
      }
      if (filters.score) {
        url += `&score=${filters.score}`;
      }
    }
    
    return this.http.get<RatingResponse>(url);
  }

  // Get my ratings
  getMyRatings(
    skip: number = 0,
    limit: number = 10
  ): Observable<RatingResponse> {
    return this.http.get<RatingResponse>(
      `${environment.apiUrl}/ratings/my/?skip=${skip}&limit=${limit}`
    );
  }

  // Add a rating to a solution
  addRating(
    slug: string, 
    score: number, 
    comment?: string,
    is_adopted_user?: boolean
  ): Observable<any> {
    return this.http.post<any>(
      `${environment.apiUrl}/ratings/solution/${slug}`,
      { score, comment, is_adopted_user }
    );
  }

  // Update a rating
  updateRating(
    ratingId: string,
    score: number,
    comment?: string,
    is_adopted_user?: boolean
  ): Observable<any> {
    return this.http.put<any>(`${environment.apiUrl}/ratings/${ratingId}`, {
      score,
      comment,
      is_adopted_user,
    });
  }

  // Delete a rating
  deleteRating(ratingId: string): Observable<any> {
    return this.http.delete<any>(`${environment.apiUrl}/ratings/${ratingId}`);
  }
}
