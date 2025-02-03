export interface Solution {
  _id: string;
  name: string;
  description: string;
  category: string;
  department: string;
  team: string;
  team_email: string;
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
  recommend_status: 'ADOPT' | 'TRIAL' | 'ASSESS' | 'HOLD';
  radar_status: 'ADOPT' | 'TRIAL' | 'ASSESS' | 'HOLD';
  stage: 'DEVELOPING' | 'UAT' | 'PRODUCTION' | 'DEPRECATED' | 'RETIRED';
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