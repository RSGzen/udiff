"use client"

import { useState } from "react"
import { MetricCard } from "@/components/dashboard/MetricCard"
import { SkillChart } from "@/components/dashboard/SkillChart"
import { ContextTreemap } from "@/components/dashboard/ContextTreemap"
import { SoftSkills } from "@/components/dashboard/SoftSkills"
import { JobDistribution } from "@/components/dashboard/JobDistribution"
import { ExperienceSplit } from "@/components/dashboard/ExperienceSplit"
import { JobsByState } from "@/components/dashboard/JobsByState"
import { TopCompanies } from "@/components/dashboard/TopCompanies"
import { SectionHeading } from "@/components/dashboard/SectionHeading"
import { SalaryBands } from "@/components/dashboard/SalaryBands"
import { RolePanel } from "@/components/dashboard/RolePanel"
import { AppShell } from "@/components/AppShell"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  DEFAULT_COUNTRY,
  getCountries,
  getCountryName,
  getRoles,
  getLevelBucket,
  getCountry,
  getRole,
} from "@/lib/data"
import { Briefcase, DollarSign, PieChart, AlertCircle } from "lucide-react"

export default function Home() {
  // 1. STATE MANAGEMENT
  const [selectedCountry, setSelectedCountry] = useState(DEFAULT_COUNTRY)
  const categoryNames = getRoles(selectedCountry)
  const [selectedCategory, setSelectedCategory] = useState(categoryNames[0])
  const [selectedLevel, setSelectedLevel] = useState("All")

  // 2. GET DATA LOGIC (all through the schema layer)
  const stats = getLevelBucket(selectedCountry, selectedCategory, selectedLevel)
  const allStats = getLevelBucket(selectedCountry, selectedCategory, "All")

  // 3. CALCULATE METRICS
  const jobCount = stats?.job_count ?? 0

  const estimate = stats?.salary_estimate
  const salaryDisplay = estimate
    ? `RM ${Math.round(estimate.nominal_myr.min).toLocaleString()} - ${Math.round(estimate.nominal_myr.max).toLocaleString()}`
    : "N/A"
  const salarySubtext = estimate
    ? "Market estimate · monthly (MYR)"
    : "Not reported in source data"

  const totalCategoryJobs = allStats?.job_count ?? 1
  const marketShare = ((jobCount / totalCategoryJobs) * 100).toFixed(1)

  const country = getCountry(selectedCountry)
  const role = getRole(selectedCountry, selectedCategory)
  const distribution = country.job_distribution
  const expSlices = [
    { label: "Junior", count: role?.Junior?.job_count ?? 0, varName: "--chart-1" },
    { label: "Mid", count: role?.Mid?.job_count ?? 0, varName: "--chart-2" },
    { label: "Senior", count: role?.Senior?.job_count ?? 0, varName: "--chart-3" },
    {
      label: "Unknown",
      count: typeof role?.unknown_level === "number" ? role.unknown_level : 0,
      varName: "--muted-foreground",
    },
  ]

  const hasData = jobCount > 0

  return (
    <AppShell>
      <div className="flex">
        <RolePanel
          categories={categoryNames}
          selectedCategory={selectedCategory}
          onSelectCategory={setSelectedCategory}
          selectedLevel={selectedLevel}
          onSelectLevel={setSelectedLevel}
        />

        <main className="flex-1 min-w-0">
          {/* Header Bar */}
          <div className="border-b border-border p-8 flex flex-wrap justify-between items-start gap-4">
            <div className="min-w-0">
              <h2 className="text-3xl font-bold tracking-tight text-foreground">
                {selectedCategory}
              </h2>
              <p className="text-muted-foreground mt-2">
                Analysis based on {jobCount} job postings in {getCountryName(selectedCountry)}.
              </p>
            </div>

            {/* Level + country controls (desktop) */}
            <div className="hidden lg:flex items-center gap-3 shrink-0">
              <span className="text-sm bg-muted text-primary px-3 py-1 rounded-full border border-border">
                {selectedLevel}
              </span>
              <Select
                value={selectedCountry}
                onValueChange={(val) => {
                  setSelectedCountry(val)
                  setSelectedCategory(getRoles(val)[0])
                }}
              >
                <SelectTrigger className="w-[160px] bg-card border-border text-foreground">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-popover border-border text-popover-foreground">
                  {getCountries().map((code) => (
                    <SelectItem key={code} value={code}>
                      {getCountryName(code)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Filters (mobile) */}
            <div className="flex lg:hidden flex-wrap items-center gap-2 w-full">
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger className="flex-1 min-w-[140px] bg-card border-border text-foreground">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-popover border-border text-popover-foreground max-h-[300px]">
                  {categoryNames.map((cat) => (
                    <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select value={selectedLevel} onValueChange={setSelectedLevel}>
                <SelectTrigger className="w-[110px] bg-card border-border text-foreground">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-popover border-border text-popover-foreground">
                  <SelectItem value="All">All</SelectItem>
                  <SelectItem value="Junior">Junior</SelectItem>
                  <SelectItem value="Mid">Mid</SelectItem>
                  <SelectItem value="Senior">Senior</SelectItem>
                </SelectContent>
              </Select>
              <Select
                value={selectedCountry}
                onValueChange={(val) => {
                  setSelectedCountry(val)
                  setSelectedCategory(getRoles(val)[0])
                }}
              >
                <SelectTrigger className="w-[130px] bg-card border-border text-foreground">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-popover border-border text-popover-foreground">
                  {getCountries().map((code) => (
                    <SelectItem key={code} value={code}>
                      {getCountryName(code)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Dashboard Content */}
          <div className="p-8 space-y-8">

            {/* Row 1: Metrics */}
            <div className="grid gap-4 md:grid-cols-3">
              <MetricCard
                title={`${selectedLevel} Openings`}
                value={jobCount}
                subtext="Job postings analysed"
                icon={Briefcase}
              />
              <MetricCard
                title="Estimated Base Salary"
                value={salaryDisplay}
                subtext={salarySubtext}
                icon={DollarSign}
              />
              <MetricCard
                title="Share of Role"
                value={`${marketShare}%`}
                subtext={`of all ${selectedCategory} jobs`}
                icon={PieChart}
              />
            </div>

            {/* CHECK: Do we have data? */}
            {hasData ? (
              <>
                <SectionHeading title="Skills & experience" scope="role × level" />
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                  <SkillChart data={stats?.top_hard_skills ?? []} />
                  <ContextTreemap data={stats?.top_technical_context ?? []} />
                </div>
                <div className="grid gap-4 lg:grid-cols-2">
                  <SoftSkills data={stats?.top_soft_skills ?? []} />
                  <ExperienceSplit slices={expSlices} />
                </div>
                <SalaryBands estimate={stats?.salary_estimate} />

                <SectionHeading title="Market overview" scope="country only" />
                <div className="grid gap-4 lg:grid-cols-2">
                  <JobDistribution data={distribution} selectedRole={selectedCategory} />
                  <JobsByState data={country.states} />
                </div>
                <TopCompanies
                  companies={country.top_companies}
                  placeholder={country.placeholder_companies}
                />
              </>
            ) : (
              <div className="bg-card/50 border border-border rounded-xl p-12 text-center text-muted-foreground flex flex-col items-center">
                <AlertCircle className="h-12 w-12 text-muted-foreground/60 mb-4" />
                <h3 className="text-lg font-semibold text-foreground">No Data Found</h3>
                <p className="max-w-sm mt-2">
                  We couldn&apos;t find any {selectedLevel} level jobs for this category in the current dataset.
                  Try switching to &quot;All&quot; or &quot;Mid&quot;.
                </p>
              </div>
            )}

          </div>
        </main>
      </div>
    </AppShell>
  )
}
