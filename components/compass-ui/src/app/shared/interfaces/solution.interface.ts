export interface Solution {
  _id: string;
  name: string;
  description: string;
  category: string;
  radar_status: 'HOLD' | 'ASSESS' | 'TRIAL' | 'ADOPT';
  department: string;
  team: string;
  maintainer_name: string;
  version: string;
  tags: string[];
  pros: string[];
  cons: string[];
  stage: 'DEPRECATED' | 'PRODUCTION' | 'BETA' | 'ALPHA';
  recommend_status: 'BUY' | 'HOLD' | 'SELL';
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