"use client"

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartTooltip } from "@/components/dashboard/ChartTooltip"

export interface ExperienceSlice {
  label: string
  count: number
  varName: string
}

interface SliceTooltipProps {
  active?: boolean
  payload?: { payload: ExperienceSlice }[]
}

function SliceTooltip({ active, payload }: SliceTooltipProps) {
  if (!active || !payload || !payload.length) return null
  const p = payload[0].payload
  return <ChartTooltip label={p.label} value={p.count} />
}

export function ExperienceSplit({ slices }: { slices: ExperienceSlice[] }) {
  const data = slices.filter((s) => s.count > 0)
  const total = data.reduce((sum, s) => sum + s.count, 0)

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Experience Split</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col items-center justify-center gap-6">
        {total > 0 ? (
          <>
            <div className="relative aspect-square w-full max-w-[200px]" aria-hidden="true">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={data}
                    dataKey="count"
                    nameKey="label"
                    innerRadius="60%"
                    outerRadius="92%"
                    paddingAngle={2}
                    stroke="none"
                  >
                    {data.map((s) => (
                      <Cell key={s.label} fill={`var(${s.varName})`} />
                    ))}
                  </Pie>
                  <Tooltip content={<SliceTooltip />} cursor={false} />
                </PieChart>
              </ResponsiveContainer>
              <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-3xl font-bold tabular-nums text-foreground">{total}</span>
                <span className="text-xs text-muted-foreground">jobs</span>
              </div>
            </div>

            <div className="w-full max-w-xs space-y-2">
              {data.map((s) => (
                <div key={s.label} className="flex items-center gap-3 text-sm">
                  <span
                    className="h-2.5 w-2.5 shrink-0 rounded-full"
                    style={{ background: `var(${s.varName})` }}
                  />
                  <span className="text-muted-foreground">{s.label}</span>
                  <span className="ml-auto tabular-nums text-foreground">
                    {s.count}{" "}
                    <span className="text-muted-foreground">
                      ({Math.round((s.count / total) * 100)}%)
                    </span>
                  </span>
                </div>
              ))}
            </div>
          </>
        ) : (
          <p className="text-sm text-muted-foreground">No experience data for this selection.</p>
        )}
      </CardContent>
    </Card>
  )
}
