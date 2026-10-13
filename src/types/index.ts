// src/types/index.ts
// Shape of the pipeline's gap_report.json (schema v3, country-nested) and skill_class.json.

export interface SkillStat {
  name: string;
  count: number;
  percentage: number;
}

export interface Company {
  name: string;
  count: number;
  kind?: "company" | "placeholder" | string;
}

export interface ObservedSalary {
  raw: string;
  value: number;
  currency: string;
  likely_annual: boolean;
  category: string;
  title: string;
}

export interface SalaryRange {
  avg_min: number;
  avg_max: number;
}

export interface MyrRange {
  min: number;
  median: number;
  max: number;
}

export interface SalaryEstimate {
  min: number;
  median: number;
  max: number;
  currency: string;
  period: string;
  period_raw: string;
  source: string;
  confidence: string;
  sample_size: number;
  fetched_at: string;
  nominal_myr: MyrRange;
  ppp_myr: MyrRange;
  broad_estimate?: boolean;
}

export interface LevelBucket {
  job_count: number;
  low_sample: boolean;
  salary: SalaryRange;
  salary_estimate?: SalaryEstimate;
  top_hard_skills: SkillStat[];
  top_soft_skills: SkillStat[];
  top_technical_context: SkillStat[];
  distinct_skills: number;
}

export interface RoleCategory {
  All: LevelBucket;
  Junior?: LevelBucket;
  Mid?: LevelBucket;
  Senior?: LevelBucket;
  unknown_level?: number;
}

export interface CountryReport {
  name: string;
  total_jobs_analyzed: number;
  job_distribution: Record<string, number>;
  states: Record<string, number>;
  top_companies: Company[];
  placeholder_companies: Company;
  observed_salaries: ObservedSalary[];
  categories: Record<string, RoleCategory>;
}

export interface SkillGap {
  skill: string;
  my_pct: number;
  peer_pct: number;
  delta: number;
}

export interface SalaryDelta {
  role: string;
  level: string;
  my: number;
  peer: number;
  delta: number;
}

export interface Comparison {
  skill_gaps: SkillGap[];
  salary_delta_nominal: SalaryDelta[];
  salary_delta_ppp: SalaryDelta[];
}

export interface GapReport {
  schema_version: number;
  generated_at: string;
  countries: Record<string, CountryReport>;
  comparisons: Record<string, Comparison>;
}

export interface SkillClassCountry {
  categories: Record<string, Record<string, string[]>>;
}

export interface SkillClassFile {
  generated_at: string;
  countries: Record<string, SkillClassCountry>;
}
