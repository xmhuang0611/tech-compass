import { HttpClient, HttpParams } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { environment } from "../../../environments/environment";
import {
    Solution
} from "../../shared/interfaces/solution.interface";
import { StandardResponse } from "../interfaces/standard-response.interface";

export interface AdoptedUser {
  _id: string;
  created_at: string;
  created_by: string | null;
  updated_at: string;
  updated_by: string | null;
  email: string;
  username: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
}

export interface AdoptedUsersResponse {
  success: boolean;
  data: AdoptedUser[];
  detail: string | null;
  total: number;
  skip: number;
  limit: number;
}

@Injectable({
  providedIn: "root",
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
    recommend_status?: "ADOPT" | "TRIAL" | "ASSESS" | "HOLD";
    stage?: "DEVELOPING" | "UAT" | "PRODUCTION" | "DEPRECATED" | "RETIRED";
    sort?: string;
    tags?: string;
  }): Observable<StandardResponse<Solution[]>> {
    let httpParams = new HttpParams()
      .set("skip", params.skip?.toString() || "0")
      .set("limit", params.limit?.toString() || "10")
      .set("review_status", "APPROVED");

    if (params.category)
      httpParams = httpParams.set("category", params.category);
    if (params.department)
      httpParams = httpParams.set("department", params.department);
    if (params.team) httpParams = httpParams.set("team", params.team);
    if (params.recommend_status)
      httpParams = httpParams.set("recommend_status", params.recommend_status);
    if (params.stage) httpParams = httpParams.set("stage", params.stage);
    if (params.sort) httpParams = httpParams.set("sort", params.sort);
    if (params.tags) httpParams = httpParams.set("tags", params.tags);

    return this.http.get<StandardResponse<Solution[]>>(this.apiUrl, {
      params: httpParams,
    });
  }

  getRecommendedSolutions(
    skip = 0,
    limit = 10
  ): Observable<StandardResponse<Solution[]>> {
    return this.http.get<StandardResponse<Solution[]>>(`${this.apiUrl}`, {
      params: {
        skip: skip.toString(),
        limit: limit.toString(),
        recommend_status: "ADOPT",
        sort: "name",
        review_status: "APPROVED",
      },
    });
  }

  createSolution(
    solution: Partial<Solution>
  ): Observable<StandardResponse<Solution>> {
    return this.http.post<StandardResponse<Solution>>(this.apiUrl, solution);
  }

  getNewSolutions(
    skip = 0,
    limit = 10
  ): Observable<StandardResponse<Solution[]>> {
    return this.http.get<StandardResponse<Solution[]>>(`${this.apiUrl}`, {
      params: {
        skip: skip.toString(),
        limit: limit.toString(),
        sort: "-created_at",
        review_status: "APPROVED",
      },
    });
  }

  searchSolutions(keyword: string): Observable<StandardResponse<Solution[]>> {
    return this.http.get<StandardResponse<Solution[]>>(
      `${this.apiUrl}search/`,
      {
        params: { keyword },
      }
    );
  }

  getMySolutions(
    skip: number = 0,
    limit: number = 10,
    sort: string = "name"
  ): Observable<StandardResponse<Solution[]>> {
    const params = new HttpParams()
      .set("skip", skip.toString())
      .set("limit", limit.toString())
      .set("sort", sort);

    return this.http.get<StandardResponse<Solution[]>>(`${this.apiUrl}my/`, {
      params,
    });
  }

  updateSolution(
    slug: string,
    solution: Partial<Solution>
  ): Observable<StandardResponse<Solution>> {
    return this.http.put<StandardResponse<Solution>>(
      `${this.apiUrl}${slug}`,
      solution
    );
  }

  deleteSolution(slug: string): Observable<StandardResponse<void>> {
    return this.http.delete<StandardResponse<void>>(`${this.apiUrl}${slug}`);
  }

  getAllSolutions(
    skip: number = 0,
    limit: number = 10,
    sort: string = "name",
    filters?: {
      category?: string;
      recommend_status?: string;
      review_status?: string;
    }
  ): Observable<StandardResponse<Solution[]>> {
    let params = new HttpParams()
      .set("skip", skip.toString())
      .set("limit", limit.toString())
      .set("sort", sort);

    if (filters) {
      if (filters.category) {
        params = params.set("category", filters.category);
      }
      if (filters.recommend_status) {
        params = params.set("recommend_status", filters.recommend_status);
      }
      if (filters.review_status) {
        params = params.set("review_status", filters.review_status);
      }
    }

    return this.http.get<StandardResponse<Solution[]>>(`${this.apiUrl}`, {
      params,
    });
  }

  getSolution(slug: string): Observable<StandardResponse<Solution>> {
    return this.http.get<StandardResponse<Solution>>(`${this.apiUrl}${slug}`);
  }

  // Get adopted users for a solution
  getAdoptedUsers(
    slug: string,
    skip: number = 0,
    limit: number = 10
  ): Observable<AdoptedUsersResponse> {
    return this.http.get<AdoptedUsersResponse>(
      `${environment.apiUrl}/solutions/${slug}/adopted-users?skip=${skip}&limit=${limit}`
    );
  }
}
