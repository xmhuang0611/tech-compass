export interface Solution {
  _id: string;
  name: string;
  description: string;
  category: string;
  department: string;
  team: string;
  maintainer_name: string;
  maintainer_email: string;
  tags: string[];
  recommend_status: 'BUY' | 'HOLD' | 'SELL';
  radar_status: 'ADOPT' | 'TRIAL' | 'ASSESS' | 'HOLD';
  stage: 'DEVELOPING' | 'UAT' | 'PRODUCTION' | 'DEPRECATED' | 'RETIRED';
  created_at: string;
  updated_at: string;
  slug: string;
}

export interface SolutionResponse {
  success: boolean;
  data: Solution[];
  detail: string | null;
  total: number;
  skip: number;
  limit: number;
} 