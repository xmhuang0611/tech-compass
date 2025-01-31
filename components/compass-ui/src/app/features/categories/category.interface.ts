export interface Category {
  _id: string;
  created_at: string;
  created_by: string;
  updated_at: string;
  updated_by: string;
  name: string;
  description: string;
  usage_count: number;
}

export interface CategoryResponse {
  success: boolean;
  data: Category[];
  detail: string;
  total: number;
  skip: number;
  limit: number;
} 