import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface JobDistributionProps {
  data: Record<string, number>
  selectedRole: string
}

export function JobDistribution({ data, selectedRole }: JobDistributionProps) {
  const entries = Object.entries(data)
    .filter(([name]) => name !== "Other")
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
  const max = Math.max(...entries.map(([, count]) => count), 1)

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Openings by Role</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {entries.map(([name, count]) => {
          const isSelected = name === selectedRole
          return (
            <div key={name} className="flex items-center gap-4">
              <span
                className={`w-44 shrink-0 truncate text-sm ${
                  isSelected ? "font-medium text-foreground" : "text-muted-foreground"
                }`}
                title={name}
              >
                {name}
              </span>
              <div className="h-2 flex-1 overflow-hidden rounded-full bg-muted">
                <div
                  className={`h-full rounded-full ${isSelected ? "bg-chart-1" : "bg-chart-1/50"}`}
                  style={{ width: `${(count / max) * 100}%` }}
                />
              </div>
              <span className="w-10 shrink-0 text-right text-sm tabular-nums text-muted-foreground">
                {count}
              </span>
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}
