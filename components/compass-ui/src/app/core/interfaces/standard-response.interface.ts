export interface StandardResponse<T> {
  success: boolean;
  data: T;
  detail: string | null;
  total: number;
  skip: number;
  limit: number;
} 