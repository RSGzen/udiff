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
    x, y, width, height, name, percentage, index, // Recharts injected props
    activeIndex, setActiveIndex // Our custom props
  } = props
  
  // A. Interaction Logic (Focus & Dim)
  const isHovered = index === activeIndex
  const isAnythingHovered = activeIndex !== null
  const isDimmed = isAnythingHovered && !isHovered

  // B. Color Logic
  const isTop = index < 2
  let bgColor = isTop ? 'var(--chart-1)' : 'var(--muted)'
  let borderColor = 'var(--border)'
  let opacity = 0.9

  if (isHovered) {
    bgColor = 'var(--chart-1)'
    borderColor = 'var(--primary-foreground)'
    opacity = 1
  } else if (isDimmed) {
    opacity = 0.3
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
          transition: 'all 0.3s ease' // Smooth animation
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
                      <div className="bg-popover border border-border p-2 rounded shadow-xl z-50">
                        <p className="text-primary font-mono text-xs font-bold tabular-nums">
                          [ {d.name}: {d.percentage}% ]
                        </p>
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