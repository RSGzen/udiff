import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface JobsByStateProps {
  data: Record<string, number>
}

export function JobsByState({ data }: JobsByStateProps) {
  const entries = Object.entries(data)
    .filter(([name]) => name !== "Other")
    .sort((a, b) => b[1] - a[1])
    .slice(0, 12)
  const max = Math.max(...entries.map(([, count]) => count), 1)

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Jobs by Location</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {entries.length > 0 ? (
          entries.map(([name, count]) => (
            <div key={name} className="flex items-center gap-4">
              <span className="w-40 shrink-0 truncate text-sm text-muted-foreground" title={name}>
                {name}
              </span>
              <div className="h-2 flex-1 overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full rounded-full bg-chart-1"
                  style={{ width: `${(count / max) * 100}%` }}
                />
              </div>
              <span className="w-10 shrink-0 text-right text-sm tabular-nums text-muted-foreground">
                {count}
              </span>
            </div>
          ))
        ) : (
          <p className="text-sm text-muted-foreground">No location data for this country.</p>
        )}
      </CardContent>
    </Card>
  )
}
