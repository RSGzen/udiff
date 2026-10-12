import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { SkillStat } from "@/types"

interface SoftSkillsProps {
  data: SkillStat[]
}

const ARROW =
  "polygon(0 0, calc(100% - 10px) 0, 100% 50%, calc(100% - 10px) 100%, 0 100%)"

export function SoftSkills({ data }: SoftSkillsProps) {
  const skills = [...data].sort((a, b) => b.count - a.count).slice(0, 8)

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Top Soft Skills</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {skills.length > 0 ? (
          skills.map((s) => {
            const pct = Math.min(s.percentage, 100)
            return (
              <div key={s.name} className="flex items-center gap-3">
                <span className="w-44 shrink-0 truncate text-sm text-foreground" title={s.name}>
                  {s.name}
                </span>
                <div className="relative h-8 flex-1">
                  <div className="absolute inset-0 rounded-md bg-muted" />
                  <div
                    className="absolute inset-y-0 left-0 flex items-center justify-end bg-chart-1 text-primary-foreground"
                    style={{ width: `${pct}%`, minWidth: "3.5rem", clipPath: ARROW }}
                  >
                    <span className="pr-4 text-xs font-semibold tabular-nums">{pct}%</span>
                  </div>
                </div>
                <span className="w-12 shrink-0 text-right text-sm tabular-nums text-muted-foreground">
                  {s.count}
                </span>
              </div>
            )
          })
        ) : (
          <p className="text-sm text-muted-foreground">No soft-skill data for this selection.</p>
        )}
      </CardContent>
    </Card>
  )
}
