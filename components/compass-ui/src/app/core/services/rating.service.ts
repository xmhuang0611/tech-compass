import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
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
  addRating(slug: string, score: number, comment?: string): Observable<any> {
    return this.http.post<any>(
      `${environment.apiUrl}/ratings/solution/${slug}`,
      { score, comment }
    );
  }

  // Update a rating
  updateRating(
    ratingId: string,
    score: number,
    comment?: string
  ): Observable<any> {
    return this.http.put<any>(`${environment.apiUrl}/ratings/${ratingId}`, {
      score,
      comment,
    });
  }

  // Delete a rating
  deleteRating(ratingId: string): Observable<any> {
    return this.http.delete<any>(`${environment.apiUrl}/ratings/${ratingId}`);
  }
}
