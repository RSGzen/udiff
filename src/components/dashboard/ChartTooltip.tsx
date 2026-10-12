import type { ReactNode } from "react"

export function ChartTooltip({ label, value }: { label: ReactNode; value: ReactNode }) {
  return (
    <div className="bg-popover border border-border rounded-lg px-3 py-2 shadow-xl">
      <div className="flex items-center justify-between gap-4 text-xs">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-medium tabular-nums text-foreground">{value}</span>
      </div>
    </div>
  )
}
