"use client"

import { useState } from "react"
import { ResponsiveContainer, Treemap, Tooltip } from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartTooltip } from "@/components/dashboard/ChartTooltip"

interface ContextItem {
  name: string
  count: number
  percentage: number
}

interface ContextTreemapProps {
  data: ContextItem[]
}

interface TreemapContentProps {
  x?: number
  y?: number
  width?: number
  height?: number
  name?: string
  percentage?: number
  index?: number
  depth?: number
  activeIndex: number | null
  setActiveIndex: (index: number | null) => void
}

// 1. Custom Content Renderer
// Recharts injects the node geometry + data; we add activeIndex/setActiveIndex.
const CustomContent = (props: TreemapContentProps) => {
  const {
    x = 0, y = 0, width = 0, height = 0,
    name = "", percentage = 0, index = 0, depth,
    activeIndex, setActiveIndex,
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

  // C. Text Collision Logic — truncate the label to the tile width; hide when too small.
  const CHAR_W = 7
  const maxChars = Math.floor((width - 12) / CHAR_W)
  const label = name.length > maxChars ? `${name.slice(0, Math.max(0, maxChars - 1))}…` : name
  const shouldShowText = maxChars >= 4 && height > 32

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
          opacity: opacity
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
            {label}
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
        <div
          className="h-[350px] w-full"
          role="img"
          aria-label={`Technical context: ${treeData.slice(0, 3).map((d) => `${d.name} ${d.percentage}%`).join(", ")}`}
        >
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
                    return <ChartTooltip label={d.name} value={`${d.percentage}%`} />
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