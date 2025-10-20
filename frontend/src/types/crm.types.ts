// frontend/src/types/crm.types.ts

export interface Lead {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  company?: string;
  job_title?: string;
  source: string;
  status: string;
  score: number;
  created_at: string;
  estimated_value?: number;
  expected_close_date?: string;
}