import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { Observable } from "rxjs";
import { environment } from "../../../environments/environment";

export interface User {
  _id: string;
  created_at: string;
  created_by?: string;
  updated_at?: string;
  updated_by?: string;
  email: string;
  username: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
}

export interface UserResponse {
  success: boolean;
  data: User[];
  detail?: string;
  total: number;
  skip: number;
  limit: number;
}

@Injectable({
  providedIn: "root",
})
export class UserService {
  constructor(private http: HttpClient) {}

  // Get all users (admin only)
  getAllUsers(
    skip: number = 0,
    limit: number = 10,
    filters?: {
      username?: string;
      is_active?: boolean;
      is_superuser?: boolean;
    }
  ): Observable<UserResponse> {
    let url = `${environment.apiUrl}/users/?skip=${skip}&limit=${limit}`;
    
    if (filters) {
      if (filters.username) {
        url += `&username=${filters.username}`;
      }
      if (filters.is_active !== undefined) {
        url += `&is_active=${filters.is_active}`;
      }
      if (filters.is_superuser !== undefined) {
        url += `&is_superuser=${filters.is_superuser}`;
      }
    }
    
    return this.http.get<UserResponse>(url);
  }

  // Update user (admin only)
  updateUser(
    username: string,
    data: {
      is_active: boolean;
      is_superuser: boolean;
    }
  ): Observable<any> {
    return this.http.put<any>(
      `${environment.apiUrl}/users/manage/${username}`,
      data
    );
  }
} 