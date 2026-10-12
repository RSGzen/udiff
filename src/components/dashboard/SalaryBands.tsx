"use client"

import { useState } from "react"
import { Card, CardAction, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import type { SalaryEstimate } from "@/types"

const fmt = (n: number) => `RM ${Math.round(n).toLocaleString()}`

export function SalaryBands({ estimate }: { estimate?: SalaryEstimate }) {
  const [mode, setMode] = useState<"nominal" | "ppp">("nominal")

  if (!estimate) {
    return (
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-foreground">Salary Estimate</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">No salary estimate for this selection.</p>
        </CardContent>
      </Card>
    )
  }

  const range = mode === "ppp" ? estimate.ppp_myr : estimate.nominal_myr
  const span = Math.max(range.max - range.min, 1)
  const medianPct = Math.min(100, Math.max(0, ((range.median - range.min) / span) * 100))

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Salary Estimate</CardTitle>
        <CardAction>
          <Tabs value={mode} onValueChange={(v) => setMode(v as "nominal" | "ppp")}>
            <TabsList className="bg-card border border-border">
              <TabsTrigger value="nominal" className="text-xs">Nominal</TabsTrigger>
              <TabsTrigger value="ppp" className="text-xs">PPP</TabsTrigger>
            </TabsList>
          </Tabs>
        </CardAction>
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold tabular-nums text-foreground">{fmt(range.median)}</span>
          <span className="text-sm text-muted-foreground">median / month</span>
        </div>

        <div className="relative mt-4 h-3 rounded-full bg-chart-1/20">
          <div className="absolute inset-y-0 left-0 right-0 rounded-full bg-chart-1/60" />
          <div
            className="absolute top-1/2 h-5 w-1 -translate-x-1/2 -translate-y-1/2 rounded-full bg-foreground"
            style={{ left: `${medianPct}%` }}
          />
        </div>
        <div className="mt-2 flex justify-between text-xs tabular-nums text-muted-foreground">
          <span>{fmt(range.min)}</span>
          <span>{fmt(range.max)}</span>
        </div>

        <p className="mt-4 text-xs text-muted-foreground">
          {mode === "ppp" ? "PPP-adjusted to MYR" : "Converted to MYR at market FX"} ·{" "}
          {estimate.source} · {estimate.confidence} confidence · n={estimate.sample_size}
          {estimate.broad_estimate ? " · broad estimate" : ""}
        </p>
        <p className="mt-1 text-[11px] text-muted-foreground/70">
          Estimated market figure, not observed pay.
        </p>
      </CardContent>
    </Card>
  )
}
