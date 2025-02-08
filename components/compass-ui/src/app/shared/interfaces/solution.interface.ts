export interface Category {
  id: string;
  name: string;
  slug: string;
}

export interface Department {
  id: string;
  name: string;
}

export interface Team {
  id: string;
  name: string;
}

export interface User {
  id: string;
  full_name: string;
  email: string;
}

export interface Solution {
  _id: string;
  name: string;
  brief: string;
  description: string;
  category: string;
  department: string;
  team: string;
  team_email: string;
  maintainer_id: string;
  maintainer_name: string;
  maintainer_email: string;
  official_website?: string;
  documentation_url?: string;
  demo_url?: string;
  logo?: string;
  version?: string;
  tags: string[];
  pros?: string[];
  cons?: string[];
  recommend_status: "ADOPT" | "TRIAL" | "ASSESS" | "HOLD";
  stage: "DEVELOPING" | "UAT" | "PRODUCTION" | "DEPRECATED" | "RETIRED";
  adoption_level: "PILOT" | "TEAM" | "DEPARTMENT" | "ENTERPRISE" | "INDUSTRY";
  adoption_user_count: number;
  created_at: string;
  updated_at: string;
  slug: string;
  rating: number;
  rating_count: number;
}

export interface SolutionResponse {
  success: boolean;
  data: Solution[];
  detail: string | null;
  total: number;
  skip: number;
  limit: number;
}

export interface PaginatedSolutions {
  items: Solution[];
  total: number;
}
