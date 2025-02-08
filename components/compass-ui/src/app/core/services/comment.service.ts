import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { Observable } from "rxjs";
import { environment } from "../../../environments/environment";

export interface Comment {
  _id: string;
  content: string;
  username: string;
  full_name: string;
  created_at: string;
  solution_slug: string;
  created_by?: string;
  updated_at?: string;
  updated_by?: string;
}

export interface CommentResponse {
  success: boolean;
  data: Comment[];
  total: number;
}

@Injectable({
  providedIn: "root",
})
export class CommentService {
  constructor(private http: HttpClient) {}

  // Get comments for a specific solution
  getSolutionComments(
    slug: string,
    page: number = 1,
    pageSize: number = 10
  ): Observable<CommentResponse> {
    return this.http.get<CommentResponse>(
      `${environment.apiUrl}/comments/solution/${slug}?page=${page}&page_size=${pageSize}`
    );
  }

  // Get my comments
  getMyComments(
    page: number = 1,
    pageSize: number = 10
  ): Observable<CommentResponse> {
    return this.http.get<CommentResponse>(
      `${environment.apiUrl}/comments/my/?page=${page}&page_size=${pageSize}`
    );
  }

  // Add a comment to a solution
  addComment(slug: string, content: string): Observable<any> {
    return this.http.post<any>(
      `${environment.apiUrl}/comments/solution/${slug}`,
      { content }
    );
  }

  // Update a comment
  updateComment(commentId: string, content: string): Observable<any> {
    return this.http.put<any>(`${environment.apiUrl}/comments/${commentId}`, {
      content,
    });
  }

  // Delete a comment
  deleteComment(commentId: string): Observable<any> {
    return this.http.delete<any>(`${environment.apiUrl}/comments/${commentId}`);
  }
}
