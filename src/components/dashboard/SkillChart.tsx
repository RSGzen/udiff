"use client"

import { useState } from "react"
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip, Cell, LabelList } from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartTooltip } from "@/components/dashboard/ChartTooltip"

interface Skill {
  name: string
  percentage: number
}

interface SkillChartProps {
  data: Skill[]
}

interface BarTooltipProps {
  active?: boolean
  label?: string
  payload?: { value: number; payload: Skill }[]
  activeIndex: number | null
  chartData: Skill[]
}

function ChartBarTooltip({ active, label, payload, activeIndex, chartData }: BarTooltipProps) {
  if (!active || !payload || !payload.length || activeIndex === null) return null
  if (payload[0].payload.name !== chartData[activeIndex]?.name) return null
  return <ChartTooltip label={label} value={`${payload[0].value}%`} />
}

export function SkillChart({ data }: SkillChartProps) {
  const chartData = [...data].sort((a, b) => b.percentage - a.percentage).slice(0, 10)

  // The hovered bar index drives the dim/highlight; reset when the pointer leaves the chart.
  const [activeIndex, setActiveIndex] = useState<number | null>(null)

  return (
    <Card className="col-span-4 bg-card border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Top Required Technologies</CardTitle>
      </CardHeader>
      <CardContent className="pl-2">
        <div
          className="h-[350px] w-full"
          role="img"
          aria-label={`Top required technologies: ${chartData.slice(0, 3).map((s) => `${s.name} ${s.percentage}%`).join(", ")}`}
          onMouseLeave={() => setActiveIndex(null)}
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{ left: 0, right: 44 }}
            >
              <YAxis
                dataKey="name"
                type="category"
                width={150}
                tick={{ fill: 'var(--muted-foreground)', fontSize: 12 }}
                tickFormatter={(value: string) => value.length > 20 ? `${value.slice(0, 19)}…` : value}
                axisLine={false}
                tickLine={false}
              />
              <XAxis type="number" hide />

              <Tooltip
                content={<ChartBarTooltip activeIndex={activeIndex} chartData={chartData} />}
                cursor={{ fill: 'transparent' }}
              />

              <Bar
                dataKey="percentage"
                radius={[0, 4, 4, 0]}
                onMouseEnter={(_, index) => setActiveIndex(index)}
              >
                <LabelList
                  dataKey="percentage"
                  position="right"
                  fill="var(--muted-foreground)"
                  fontSize={11}
                  formatter={(value) => `${value}%`}
                />
                {chartData.map((entry, index) => {
                  const isHovered = activeIndex === index
                  const isAnythingHovered = activeIndex !== null

                  const finalColor = 'var(--chart-1)'
                  let finalOpacity = index < 3 ? 1 : 0.35

                  if (isHovered) {
                    finalOpacity = 1
                  } else if (isAnythingHovered) {
                    finalOpacity = 0.2
                  }

                  return (
                    <Cell
                      key={`cell-${index}`}
                      fill={finalColor}
                      fillOpacity={finalOpacity}
                      stroke="none"
                    />
                  )
                })}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
