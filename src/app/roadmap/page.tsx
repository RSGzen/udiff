"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { AppShell } from "@/components/AppShell"

// Import the MASTER data
import allRoadmaps from "@/data/roadmaps.json"

export default function RoadmapPage() {
  // 1. State for selected Role (Default to Backend)
  const [selectedRoleKey, setSelectedRoleKey] = useState("Backend")

  // 2. State for collected skills (We use a simple object: { "Backend": ["Git", "Java"], "AI": ["Python"] })
  const [userProgress, setUserProgress] = useState<Record<string, string[]>>({})
  const [loaded, setLoaded] = useState(false)

  // Load persisted progress once on mount (avoids an SSR/hydration mismatch).
  useEffect(() => {
    try {
      const saved = localStorage.getItem("udiff-roadmap-progress")
      if (saved) setUserProgress(JSON.parse(saved))
    } catch {
      /* ignore malformed storage */
    }
    setLoaded(true)
  }, [])

  // Persist on change, but only after the initial load so we never clobber saved data.
  useEffect(() => {
    if (!loaded) return
    try {
      localStorage.setItem("udiff-roadmap-progress", JSON.stringify(userProgress))
    } catch {
      /* ignore quota errors */
    }
  }, [userProgress, loaded])

  // Load the data for the current view
  // @ts-ignore
  const currentRoadmap = allRoadmaps[selectedRoleKey] || allRoadmaps["Backend"]
  const currentCollected = new Set(userProgress[selectedRoleKey] || [])

  const toggleSkill = (skillName: string) => {
    const newSet = new Set(currentCollected)
    if (newSet.has(skillName)) {
      newSet.delete(skillName)
    } else {
      newSet.add(skillName)
    }

    // Save back to main state
    setUserProgress({
      ...userProgress,
      [selectedRoleKey]: Array.from(newSet)
    })
  }

  // Calculate Metrics
  const totalSkills = currentRoadmap.phases.reduce((acc: any, phase: any) => acc + phase.skills.length, 0)
  const totalCollected = currentCollected.size
  const totalPercentage = Math.round((totalCollected / totalSkills) * 100)

  return (
    <AppShell>
      <main className="p-8">

      {/* NAVIGATION HEADER */}
      <div className="max-w-3xl mx-auto mb-8 flex flex-col md:flex-row md:items-center justify-end gap-4">
        {/* ROLE SELECTOR */}
        <div className="flex items-center gap-3">
            <span className="text-muted-foreground text-sm font-medium">Career Path:</span>
            <Select value={selectedRoleKey} onValueChange={setSelectedRoleKey}>
                <SelectTrigger className="w-[200px] bg-card border-border text-foreground">
                    <SelectValue placeholder="Select Role" />
                </SelectTrigger>
                <SelectContent className="bg-popover border-border text-popover-foreground">
                    {Object.keys(allRoadmaps).map((key) => (
                        <SelectItem key={key} value={key}>{key}</SelectItem>
                    ))}
                </SelectContent>
            </Select>
        </div>
      </div>

      {/* ROADMAP HEADER */}
      <div className="max-w-3xl mx-auto mb-12">
        <h2 className="text-4xl font-bold text-foreground mb-4">
          {currentRoadmap.role} Roadmap
        </h2>
        <div className="flex items-center gap-4 mb-2">
          <Progress value={totalPercentage} className="h-4 bg-muted" />
          <span className="font-bold text-primary min-w-[4rem] tabular-nums">{totalPercentage}%</span>
        </div>
        <p className="text-muted-foreground">
          {totalCollected} / {totalSkills} skills acquired. Keep pushing!
        </p>
      </div>

      {/* PHASED TIMELINE */}
      <div className="max-w-3xl mx-auto space-y-8 relative pb-20">
        <div className="absolute left-6 top-4 bottom-4 w-0.5 bg-border -z-10"></div>

        {currentRoadmap.phases.map((phase: any, index: number) => {
          const phaseCollectedCount = phase.skills.filter((s: string) => currentCollected.has(s)).length
          const isPhaseComplete = phaseCollectedCount === phase.skills.length

          // Unlock Logic: Previous phase must be > 50% done
          const previousPhase = index > 0 ? currentRoadmap.phases[index - 1] : null
          const prevCollected = previousPhase
            ? previousPhase.skills.filter((s: string) => currentCollected.has(s)).length
            : 0
          const isLocked = index > 0 && (prevCollected / previousPhase.skills.length) < 0.5

          return (
            <Card key={phase.id} className={`bg-card/80 border-border relative transition-[opacity,filter] duration-300 ease-out ${isLocked ? 'opacity-50 grayscale' : ''}`}>

              <div className={`absolute -left-9 top-6 h-6 w-6 rounded-full border-4 border-background flex items-center justify-center transition-colors duration-300 ${
                isPhaseComplete ? 'bg-primary' : isLocked ? 'bg-muted' : 'bg-foreground'
              }`}>
                 {isPhaseComplete && <span className="text-primary-foreground text-xs font-bold">✓</span>}
              </div>

              <CardHeader>
                <div className="flex justify-between items-center">
                    <div>
                        <CardTitle className={`text-xl ${isLocked ? 'text-muted-foreground' : 'text-foreground'}`}>
                        {phase.title}
                        </CardTitle>
                        <CardDescription className="text-muted-foreground mt-1">
                        {phase.description}
                        </CardDescription>
                    </div>
                    {isLocked && <Badge variant="outline" className="text-muted-foreground border-border">Locked</Badge>}
                     {isPhaseComplete && <Badge className="bg-primary hover:bg-primary/90 text-primary-foreground border-0">Completed</Badge>}
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {phase.skills.map((skill: string) => (
                    <div
                      key={skill}
                      className={`flex items-center space-x-3 p-3 rounded-lg border border-border/50 transition-colors duration-200 ${
                        currentCollected.has(skill) ? 'bg-primary/10 text-primary border-primary/30' : 'bg-background/50 text-muted-foreground'
                      } ${isLocked ? 'pointer-events-none' : 'cursor-pointer hover:bg-muted'}`}
                      onClick={() => !isLocked && toggleSkill(skill)}
                    >
                      <Checkbox
                        id={skill}
                        checked={currentCollected.has(skill)}
                        className="pointer-events-none data-[state=checked]:bg-primary data-[state=checked]:border-primary"
                      />
                      <label htmlFor={skill} className="text-sm font-medium leading-none pointer-events-none select-none">
                        {skill}
                      </label>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>
      </main>
    </AppShell>
  )
}
