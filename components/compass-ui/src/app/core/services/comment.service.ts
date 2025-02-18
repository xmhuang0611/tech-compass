import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { environment } from "../../../environments/environment";

export interface Comment {
  _id: string;
  content: string;
  username: string;
  full_name: string;
  created_at: string;
  solution_slug: string;
  type: "OFFICIAL" | "USER";
  is_adopted_user?: boolean;
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

  // Get all comments (admin only)
  getAllComments(
    skip: number = 0,
    limit: number = 10,
    filters?: {
      solution_slug?: string;
      type?: "OFFICIAL" | "USER";
    }
  ): Observable<CommentResponse> {
    let url = `${environment.apiUrl}/comments/?skip=${skip}&limit=${limit}`;
    
    if (filters) {
      if (filters.solution_slug) {
        url += `&solution_slug=${filters.solution_slug}`;
      }
      if (filters.type) {
        url += `&type=${filters.type}`;
      }
    }
    
    return this.http.get<CommentResponse>(url);
  }

  // Get comments for a specific solution
  getSolutionComments(
    slug: string,
    skip: number = 0,
    limit: number = 10,
    type?: "OFFICIAL" | "USER"
  ): Observable<CommentResponse> {
    let url = `${environment.apiUrl}/comments/solution/${slug}?skip=${skip}&limit=${limit}`;
    if (type) {
      url += `&type=${type}`;
    }
    return this.http.get<CommentResponse>(url);
  }

  // Get my comments
  getMyComments(
    skip: number = 0,
    limit: number = 10
  ): Observable<CommentResponse> {
    return this.http.get<CommentResponse>(
      `${environment.apiUrl}/comments/my/?skip=${skip}&limit=${limit}`
    );
  }

  // Add a comment to a solution
  addComment(
    slug: string, 
    data: { content: string; is_adopted_user: boolean }
  ): Observable<any> {
    return this.http.post<any>(
      `${environment.apiUrl}/comments/solution/${slug}`,
      data
    );
  }

  // Update a comment
  updateComment(
    commentId: string, 
    content: string, 
    type: "OFFICIAL" | "USER",
    is_adopted_user?: boolean
  ): Observable<any> {
    return this.http.put<any>(`${environment.apiUrl}/comments/${commentId}`, {
      content,
      type,
      is_adopted_user
    });
  }

  // Delete a comment
  deleteComment(commentId: string): Observable<any> {
    return this.http.delete<any>(`${environment.apiUrl}/comments/${commentId}`);
  }
}
