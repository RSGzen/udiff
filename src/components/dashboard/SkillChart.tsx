"use client"

import { useState } from "react"
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip, Cell, TooltipProps } from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface Skill {
  name: string
  percentage: number
}

interface SkillChartProps {
  data: Skill[]
}

export function SkillChart({ data }: SkillChartProps) {
  const chartData = [...data].sort((a, b) => b.percentage - a.percentage).slice(0, 10)
  
  // State is now the "Master Switch" for the Tooltip
  const [activeIndex, setActiveIndex] = useState<number | null>(null)

  // 1. MOVED INSIDE: Custom Tooltip now has access to 'activeIndex'
  const CustomTooltip = ({ active, payload, label }: any) => {
    // The Logic: 
    // active = Recharts thinks mouse is in the row (True even in white space)
    // activeIndex !== null = Mouse is actually hitting the coloured Bar (Our custom tracker)
    if (active && payload && payload.length && activeIndex !== null) {
      
      // Optional: Check if the row being hovered matches the active bar
      // (Prevents edge case flickering)
      const isMatchingRow = payload[0].payload.name === chartData[activeIndex]?.name
      if (!isMatchingRow) return null;

      return (
        <div className="bg-popover border border-border p-3 rounded-lg shadow-xl">
          <p className="text-primary font-mono text-sm font-bold tabular-nums">
            [ {label} : {payload[0].value}% ]
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <Card className="col-span-4 bg-card border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Top Required Technologies</CardTitle>
      </CardHeader>
      <CardContent className="pl-2">
        <div className="h-[350px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart 
              data={chartData} 
              layout="vertical" 
              margin={{ left: 0, right: 30 }}
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
                content={<CustomTooltip />}
                cursor={{ fill: 'transparent' }} // Invisible cursor background
              />
              
              <Bar 
                dataKey="percentage" 
                radius={[0, 4, 4, 0]}
                // These events control the "Master Switch"
                onMouseEnter={(_, index) => setActiveIndex(index)}
                onMouseLeave={() => setActiveIndex(null)}
              >
                {chartData.map((entry, index) => {
                  const isHovered = activeIndex === index
                  const isAnythingHovered = activeIndex !== null
                  
                  let finalColor = index < 3 ? 'var(--chart-1)' : 'var(--muted)'
                  let finalOpacity = 1

                  if (isHovered) {
                    finalColor = 'var(--chart-1)'
                    finalOpacity = 1
                  } else if (isAnythingHovered) {
                    finalOpacity = 0.3
                  }

                  return (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={finalColor}
                      fillOpacity={finalOpacity}
                      style={{ transition: 'all 0.3s ease' }}
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