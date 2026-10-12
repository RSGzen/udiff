"use client"

import { useState } from "react"
import { Card, CardAction, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import type { Company } from "@/types"

interface TopCompaniesProps {
  companies: Company[]
  placeholder: Company
}

export function TopCompanies({ companies, placeholder }: TopCompaniesProps) {
  const [showRecruiters, setShowRecruiters] = useState(false)

  const list = [
    ...companies.map((c) => ({ ...c, recruiter: false })),
    ...(showRecruiters ? [{ ...placeholder, recruiter: true }] : []),
  ]
    .sort((a, b) => b.count - a.count)
    .slice(0, 10)

  const max = Math.max(...list.map((c) => c.count), 1)

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Top Hiring Companies</CardTitle>
        <CardAction>
          <label className="flex cursor-pointer items-center gap-2 text-xs text-muted-foreground">
            <Checkbox
              checked={showRecruiters}
              onCheckedChange={(v) => setShowRecruiters(Boolean(v))}
            />
            Recruiters
          </label>
        </CardAction>
      </CardHeader>
      <CardContent className="space-y-3">
        {list.map((c, i) => (
          <div key={c.name} className="flex items-center gap-3">
            <span className="w-5 shrink-0 text-right text-xs tabular-nums text-muted-foreground">
              {i + 1}
            </span>
            <span
              className={`w-40 shrink-0 truncate text-sm ${
                c.recruiter ? "text-muted-foreground" : "text-foreground"
              }`}
              title={c.name}
            >
              {c.name}
            </span>
            <div className="h-2 flex-1 overflow-hidden rounded-full bg-muted">
              <div
                className={`h-full rounded-full ${c.recruiter ? "bg-chart-3" : "bg-chart-1"}`}
                style={{ width: `${(c.count / max) * 100}%` }}
              />
            </div>
            <span className="w-10 shrink-0 text-right text-sm tabular-nums text-muted-foreground">
              {c.count}
            </span>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
