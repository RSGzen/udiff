"use client"

import { useState } from "react"
import { MetricCard } from "@/components/dashboard/MetricCard"
import { SkillChart } from "@/components/dashboard/SkillChart"
import { ContextTreemap } from "@/components/dashboard/ContextTreemap"
import { Sidebar } from "@/components/Sidebar"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  DEFAULT_COUNTRY,
  getCountries,
  getCountryName,
  getRoles,
  getLevelBucket,
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

  const totalCategoryJobs = allStats?.job_count ?? 1
  const marketShare = ((jobCount / totalCategoryJobs) * 100).toFixed(1)

  const hasData = jobCount > 0

  return (
    <main className="min-h-screen bg-background text-foreground">

      <Sidebar
        categories={categoryNames}
        selectedCategory={selectedCategory}
        onSelectCategory={setSelectedCategory}
        selectedLevel={selectedLevel}
        onSelectLevel={setSelectedLevel}
      />

      <div className="pl-64 transition-all duration-300">

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

          {/* Level + country controls */}
          <div className="flex items-center gap-3 shrink-0">
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
              subtext="Estimated monthly (MYR)"
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
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
              <SkillChart data={stats?.top_hard_skills ?? []} />
              <ContextTreemap data={stats?.top_technical_context ?? []} />
            </div>
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
      </div>
    </main>
  )
}
