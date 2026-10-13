import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { ObservedSalary } from "@/types"

const SHOW = 8

export function ObservedSalaries({ data }: { data: ObservedSalary[] }) {
  const entries = data.slice(0, SHOW)

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Observed Salary Mentions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {data.length > 0 ? (
          <>
            {entries.map((s, i) => (
              <div key={i} className="flex items-start gap-3">
                <div className="min-w-0 flex-1">
                  <div className="truncate text-sm text-foreground" title={s.title}>
                    {s.title}
                  </div>
                  <div className="truncate text-xs text-muted-foreground" title={`${s.category} · ${s.raw}`}>
                    {s.category} · {s.raw}
                  </div>
                </div>
                <div className="flex shrink-0 items-center gap-2 pt-0.5">
                  <span className="tabular-nums text-sm text-foreground">
                    {s.value.toLocaleString()} {s.currency}
                  </span>
                  {s.likely_annual && (
                    <Badge
                      variant="outline"
                      className="border-border px-1.5 text-[10px] font-medium text-muted-foreground"
                    >
                      annual
                    </Badge>
                  )}
                </div>
              </div>
            ))}
            <p className="pt-1 text-xs text-muted-foreground/70">
              {data.length} mention{data.length === 1 ? "" : "s"} text-mined from ad listings — best-effort,
              not authoritative.
            </p>
          </>
        ) : (
          <p className="text-sm text-muted-foreground">No observed salary mentions for this country.</p>
        )}
      </CardContent>
    </Card>
  )
}
