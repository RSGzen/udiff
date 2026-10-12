"use client"

import { useState } from "react"
import { AppShell } from "@/components/AppShell"
import { Card, CardContent, CardHeader, CardTitle, CardAction } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { DEFAULT_COUNTRY, getComparison, getCountries, getCountryName } from "@/lib/data"
import type { Comparison } from "@/types"

const PEERS = getCountries().filter((c) => c !== DEFAULT_COUNTRY)
const BASE_NAME = getCountryName(DEFAULT_COUNTRY)

const fmtPp = (n: number) => `${n > 0 ? "+" : ""}${n.toFixed(1)} pp`
const fmtRm = (n: number) => `${n < 0 ? "-" : "+"}RM ${Math.abs(Math.round(n)).toLocaleString()}`

function DivergingBar({ value, max }: { value: number; max: number }) {
  const pct = max > 0 ? (Math.abs(value) / max) * 50 : 0
  const positive = value >= 0
  return (
    <div className="relative h-4 flex-1">
      <div className="absolute inset-y-0 left-1/2 w-px -translate-x-1/2 bg-border" />
      <div
        className={`absolute inset-y-1 rounded-sm ${positive ? "bg-success" : "bg-destructive"}`}
        style={positive ? { left: "50%", width: `${pct}%` } : { right: "50%", width: `${pct}%` }}
      />
    </div>
  )
}

export default function ComparePage() {
  const [peer, setPeer] = useState(PEERS[0])
  const [salaryMode, setSalaryMode] = useState<"nominal" | "ppp">("nominal")

  const cmp: Comparison | undefined = getComparison(peer)
  const peerName = getCountryName(peer)

  const skillGaps = [...(cmp?.skill_gaps ?? [])]
    .sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta))
    .slice(0, 12)
  const maxSkill = Math.max(...skillGaps.map((s) => Math.abs(s.delta)), 1)

  const salaryDeltas = [...(cmp?.[salaryMode === "ppp" ? "salary_delta_ppp" : "salary_delta_nominal"] ?? [])]
    .sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta))
    .slice(0, 12)
  const maxSalary = Math.max(...salaryDeltas.map((s) => Math.abs(s.delta)), 1)

  return (
    <AppShell>
      <main className="p-8">
        {/* Header */}
        <div className="mb-8 flex flex-wrap items-start justify-between gap-4 border-b border-border pb-8">
          <div>
            <h2 className="text-3xl font-bold tracking-tight text-foreground">Compare Markets</h2>
            <p className="mt-2 text-muted-foreground">
              {BASE_NAME} vs {peerName} — where local demand and pay differ.
            </p>
          </div>
          <Tabs value={peer} onValueChange={setPeer}>
            <TabsList className="bg-card border border-border">
              {PEERS.map((c) => (
                <TabsTrigger key={c} value={c} className="text-xs">
                  {getCountryName(c)}
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>
        </div>

        <div className="space-y-8">
          {/* Skill gaps */}
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-foreground">Skill Gaps</CardTitle>
              <CardAction>
                <span className="text-xs text-muted-foreground">
                  {BASE_NAME} minus {peerName} (pp)
                </span>
              </CardAction>
            </CardHeader>
            <CardContent className="space-y-3">
              {skillGaps.length > 0 ? (
                skillGaps.map((s) => (
                  <div key={s.skill} className="flex items-center gap-3">
                    <span className="w-40 shrink-0 truncate text-sm text-foreground" title={s.skill}>
                      {s.skill}
                    </span>
                    <DivergingBar value={s.delta} max={maxSkill} />
                    <span
                      className={`w-20 shrink-0 text-right text-sm tabular-nums ${
                        s.delta >= 0 ? "text-success" : "text-destructive"
                      }`}
                    >
                      {fmtPp(s.delta)}
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">No comparison data.</p>
              )}
            </CardContent>
          </Card>

          {/* Salary deltas */}
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-foreground">Salary Deltas</CardTitle>
              <CardAction>
                <Tabs value={salaryMode} onValueChange={(v) => setSalaryMode(v as "nominal" | "ppp")}>
                  <TabsList className="bg-card border border-border">
                    <TabsTrigger value="nominal" className="text-xs">Nominal</TabsTrigger>
                    <TabsTrigger value="ppp" className="text-xs">PPP</TabsTrigger>
                  </TabsList>
                </Tabs>
              </CardAction>
            </CardHeader>
            <CardContent className="space-y-3">
              {salaryDeltas.length > 0 ? (
                salaryDeltas.map((s) => (
                  <div key={`${s.role}-${s.level}`} className="flex items-center gap-3">
                    <div className="w-48 shrink-0">
                      <div className="truncate text-sm text-foreground" title={s.role}>
                        {s.role}
                      </div>
                      <div className="text-xs text-muted-foreground">{s.level}</div>
                    </div>
                    <DivergingBar value={s.delta} max={maxSalary} />
                    <span
                      className={`w-24 shrink-0 text-right text-sm tabular-nums ${
                        s.delta >= 0 ? "text-success" : "text-destructive"
                      }`}
                      title={`${BASE_NAME}: RM ${Math.round(s.my).toLocaleString()} · ${peerName}: RM ${Math.round(s.peer).toLocaleString()}`}
                    >
                      {fmtRm(s.delta)}
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">No comparison data.</p>
              )}
            </CardContent>
          </Card>

          <p className="text-xs text-muted-foreground/70">
            Right = {BASE_NAME} higher, left = {BASE_NAME} lower. Salaries are monthly estimates in MYR
            (nominal or PPP-adjusted); hover a number for the underlying figures.
          </p>
        </div>
      </main>
    </AppShell>
  )
}
