import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { SkillStat } from "@/types"

interface SoftSkillsProps {
  data: SkillStat[]
}

export function SoftSkills({ data }: SoftSkillsProps) {
  const skills = [...data].sort((a, b) => b.count - a.count).slice(0, 8)

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Top Soft Skills</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {skills.length > 0 ? (
          skills.map((s) => (
            <div key={s.name} className="flex items-center gap-4">
              <span className="w-44 shrink-0 truncate text-sm text-foreground" title={s.name}>
                {s.name}
              </span>
              <div className="h-2 flex-1 overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full rounded-full bg-chart-1"
                  style={{ width: `${Math.min(s.percentage, 100)}%` }}
                />
              </div>
              <span className="w-24 shrink-0 text-right text-sm tabular-nums text-muted-foreground">
                {s.percentage}% · {s.count}
              </span>
            </div>
          ))
        ) : (
          <p className="text-sm text-muted-foreground">No soft-skill data for this selection.</p>
        )}
      </CardContent>
    </Card>
  )
}
