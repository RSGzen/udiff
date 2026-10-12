// src/lib/data.ts
// Single access point for the pipeline's JSON. Components must read data through
// these functions so the schema is handled in one place.

import gapReportJson from "@/data/gap_report.json";
import skillClassJson from "@/data/skill_class.json";
import type {
  GapReport,
  SkillClassFile,
  CountryReport,
  RoleCategory,
  LevelBucket,
  Comparison,
} from "@/types";

const report = gapReportJson as unknown as GapReport;
const curriculum = skillClassJson as unknown as SkillClassFile;

export const DEFAULT_COUNTRY = "my";
export const generatedAt: string = report.generated_at;

export function getCountries(): string[] {
  return Object.keys(report.countries);
}

export function getCountryName(code: string): string {
  return report.countries[code]?.name ?? code.toUpperCase();
}

export function getCountry(code: string = DEFAULT_COUNTRY): CountryReport {
  return report.countries[code] ?? report.countries[DEFAULT_COUNTRY];
}

export function getRoles(code: string = DEFAULT_COUNTRY): string[] {
  return Object.keys(getCountry(code).categories)
    .filter((role) => role !== "Other")
    .sort();
}

export function getRole(
  code: string,
  role: string
): RoleCategory | undefined {
  return getCountry(code).categories[role];
}

export function getLevelBucket(
  code: string,
  role: string,
  level: string = "All"
): LevelBucket | undefined {
  const category = getRole(code, role);
  if (!category) return undefined;
  const buckets = category as unknown as Record<string, LevelBucket | undefined>;
  return buckets[level] ?? category.All;
}

export function getComparison(
  peer: string,
  base: string = DEFAULT_COUNTRY
): Comparison | undefined {
  return report.comparisons[`${base}-vs-${peer}`];
}

export function getSkillClassRoles(code: string = DEFAULT_COUNTRY): string[] {
  return Object.keys(curriculum.countries[code]?.categories ?? {}).sort();
}

export function getSkillClass(
  code: string,
  role: string
): Record<string, string[]> {
  return curriculum.countries[code]?.categories[role] ?? {};
}
