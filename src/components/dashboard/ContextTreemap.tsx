"use client"

import { useState } from "react"
import { ResponsiveContainer, Treemap, Tooltip } from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface ContextItem {
  name: string
  count: number
  percentage: number
}

interface ContextTreemapProps {
  data: ContextItem[]
}

// 1. Custom Content Renderer
// We pass activeIndex and setActiveIndex down to each block
const CustomContent = (props: any) => {
  const { 
    x, y, width, height, name, percentage, index, depth, // Recharts injected props
    activeIndex, setActiveIndex // Our custom props
  } = props

  // Recharts renders the root node (depth 0) through this content too. It has no
  // name/percentage and covers the whole area — skip it (avoids a stray "%" and a
  // full-area tint behind every tile).
  if (depth === 0) return null
  
  // A. Interaction Logic (Focus & Dim)
  const isHovered = index === activeIndex
  const isAnythingHovered = activeIndex !== null
  const isDimmed = isAnythingHovered && !isHovered

  // B. Color Logic
  const isTop = index < 2
  const bgColor = 'var(--chart-1)'
  let borderColor = 'var(--border)'
  let opacity = isTop ? 0.9 : 0.35

  if (isHovered) {
    borderColor = 'var(--primary-foreground)'
    opacity = 1
  } else if (isDimmed) {
    opacity = 0.2
  }

  // C. Text Collision Logic
  // Estimate text width: ~8px per character. 
  // If the box width is smaller than text width + 10px padding, hide it.
  const estimatedTextWidth = name.length * 8
  const shouldShowText = width > (estimatedTextWidth + 10) && height > 35

  return (
    <g
      onMouseEnter={() => setActiveIndex(index)}
      onMouseLeave={() => setActiveIndex(null)}
      style={{ cursor: 'pointer' }}
    >
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        style={{
          fill: bgColor,
          stroke: borderColor,
          strokeWidth: isHovered ? 3 : 2, // Thicker border on hover
          opacity: opacity,
          transition: 'fill 150ms ease-out, opacity 150ms ease-out, stroke 150ms ease-out'
        }}
        rx={6}
      />
      
      {/* Only render text if it fits safely */}
      {shouldShowText && (
        <>
          <text
            x={x + width / 2}
            y={y + height / 2}
            textAnchor="middle"
            fill="var(--primary-foreground)"
            stroke="none"
            fontSize={14}
            fontWeight="bold"
            dy={-6}
            style={{ pointerEvents: 'none' }} // Let mouse pass through to the rect
          >
            {name}
          </text>
          <text
            x={x + width / 2}
            y={y + height / 2}
            textAnchor="middle"
            fill="var(--muted-foreground)"
            stroke="none"
            fontSize={11}
            dy={12}
            style={{ pointerEvents: 'none' }}
          >
            {percentage}%
          </text>
        </>
      )}
    </g>
  )
}

export function ContextTreemap({ data }: ContextTreemapProps) {
  // Sort and slice top 8
  const treeData = data.map(d => ({
    name: d.name,
    size: d.count,
    percentage: d.percentage
  })).sort((a, b) => b.size - a.size).slice(0, 8) 

  // State for interaction
  const [activeIndex, setActiveIndex] = useState<number | null>(null)

  return (
    <Card className="col-span-3 bg-card border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Technical Context</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[350px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <Treemap
              data={treeData}
              dataKey="size"
              aspectRatio={4 / 3}
              stroke="var(--border)" 
              fill="var(--muted)"
              // Pass our Custom Component WITH the state props
              content={
                <CustomContent 
                  activeIndex={activeIndex} 
                  setActiveIndex={setActiveIndex} 
                />
              }
            >
              <Tooltip 
                cursor={{ stroke: 'none' }} // Hide default cursor since we have custom dimming
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const d = payload[0].payload
                    return (
                      <div className="bg-popover border border-border rounded-lg px-3 py-2 shadow-xl z-50">
                        <div className="flex items-center justify-between gap-4 text-xs">
                          <span className="text-muted-foreground">{d.name}</span>
                          <span className="font-medium text-foreground tabular-nums">{d.percentage}%</span>
                        </div>
                      </div>
                    )
                  }
                  return null
                }}
              />
            </Treemap>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}