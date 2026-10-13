"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { AppShell } from "@/components/AppShell"
import { CheckCircle2, AlertCircle, ArrowRight } from "lucide-react"

// 1. Read the skill→course dictionary through the schema layer
import { DEFAULT_COUNTRY, getSkillClassRoles, getSkillClass } from "@/lib/data"
import { SKILL_ALIASES } from "@/lib/skill-aliases"

const ROLES = getSkillClassRoles(DEFAULT_COUNTRY)

// Normalize for matching: fold tech punctuation into safe tokens (C++ → cpp, C# → csharp,
// .NET → dotnet), then keep only alphanumerics. Returns space-separated tokens.
const normalize = (text: string) =>
  text
    .toLowerCase()
    .replace(/c\+\+/g, " cpp ")
    .replace(/c#/g, " csharp ")
    .replace(/f#/g, " fsharp ")
    .replace(/\.net/g, " dotnet ")
    .replace(/node\.?js/g, " nodejs ")
    .replace(/[^a-z0-9]+/g, " ")
    .trim()

const escapeRegExp = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")

// Whole-word / phrase match. Prevents "C#" (→"c") from matching "Computer", and skips
// empty terms (junk synonyms like "," that would otherwise match everything).
const containsTerm = (haystack: string, term: string) => {
  const t = normalize(term)
  if (!t) return false
  const pattern = t.split(" ").map(escapeRegExp).join("\\s+")
  return new RegExp(`(?:^| )${pattern}(?: |$)`).test(haystack)
}

export default function CurriculumCheckPage() {
  // --- STATE ---
  // Default to first role in the dictionary
  const [selectedRole, setSelectedRole] = useState(ROLES[0] ?? "")
  const [inputText, setInputText] = useState("")
  const [isAnalyzed, setIsAnalyzed] = useState(false)

  // Analysis Results
  const [foundSkills, setFoundSkills] = useState<string[]>([])
  const [missingSkills, setMissingSkills] = useState<string[]>([])
  const [score, setScore] = useState(0)

  // --- THE NEW LOGIC ---
  const handleAnalyze = () => {
    if (!inputText.trim()) return

    // 1. Get the Dictionary for the selected Role
    const roleData = getSkillClass(DEFAULT_COUNTRY, selectedRole)

    if (!roleData) {
      console.error("No data found for role:", selectedRole)
      return
    }

    // The Keys are our "Target Skills" (e.g., "Python", "NLP")
    const targetSkills = Object.keys(roleData)

    const userTextClean = normalize(inputText)
    const found: string[] = []
    const missing: string[] = []

    // 2. Iterate through each Target Skill
    targetSkills.forEach((skillName) => {
      // Check A: the skill itself (whole-word / phrase).
      let isMatch = containsTerm(userTextClean, skillName)

      // Check B: any of the generated course-name synonyms.
      if (!isMatch) {
        const synonyms = roleData[skillName] || []
        isMatch = synonyms.some((syn) => containsTerm(userTextClean, syn))
      }

      // Check C: the curated cross-walk for common phrasings.
      if (!isMatch) {
        const aliases = SKILL_ALIASES[normalize(skillName)] ?? []
        isMatch = aliases.some((alias) => containsTerm(userTextClean, alias))
      }

      if (isMatch) {
        found.push(skillName)
      } else {
        missing.push(skillName)
      }
    })

    // 4. Update UI
    setFoundSkills(found)
    setMissingSkills(missing)
    setScore(Math.round((found.length / targetSkills.length) * 100))
    setIsAnalyzed(true)
  }

  const handleReset = () => {
    setIsAnalyzed(false)
    setInputText("")
    setFoundSkills([])
    setMissingSkills([])
  }

  return (
    <AppShell>
      <main className="p-8">

      {/* HEADER */}
      <div className="max-w-4xl mx-auto mb-8">
        <h2 className="text-3xl font-bold text-foreground">
          Curriculum Gap Analyzer
        </h2>
        <p className="text-muted-foreground mt-2">
          Paste your university syllabus, course list, or resume below.
          We will check if it matches the market demands for
          <span className="text-primary font-bold"> {selectedRole}</span>.
        </p>
      </div>

      <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">

        {/* LEFT COLUMN: INPUT */}
        <div className="md:col-span-2 space-y-6">

          <div className="bg-muted/30 border border-border rounded-lg p-3 flex gap-3 items-start mb-4">
            <AlertCircle className="h-5 w-5 text-primary shrink-0 mt-0.5" />
            <div className="text-sm text-foreground/90">
              <span className="font-bold text-primary">Beta Feature:</span> This tool uses keyword matching.
              It might miss course titles that use unique naming conventions.
              <br/>
              <span className="text-xs text-muted-foreground mt-1 block">
                (Tip: For best results, paste your detailed course syllabus, not just the titles.)
              </span>
            </div>
          </div>

          {/* Controls */}
          <div className="bg-card border border-border p-4 rounded-xl flex flex-col sm:flex-row items-center gap-4">
            <div className="flex-1 w-full">
              <label className="text-xs text-muted-foreground font-bold uppercase tracking-wider mb-1 block">Target Role</label>
              <Select value={selectedRole} onValueChange={(val) => { setSelectedRole(val); setIsAnalyzed(false); }}>
                <SelectTrigger className="bg-background border-border text-foreground w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-popover border-border text-popover-foreground max-h-[300px]">
                   {/* Dynamically load roles from the dictionary */}
                   {ROLES.map(cat => (
                     <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                   ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-end w-full sm:w-auto">
              {!isAnalyzed ? (
                <Button onClick={handleAnalyze} className="bg-primary hover:bg-primary/90 text-primary-foreground w-full sm:w-auto">
                  Run Analysis <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              ) : (
                <Button onClick={handleReset} variant="outline" className="border-border text-foreground hover:bg-muted w-full sm:w-auto">
                  Reset
                </Button>
              )}
            </div>
          </div>

          {/* Text Area */}
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-lg text-foreground">Your Curriculum</CardTitle>
            </CardHeader>
            <CardContent>
              <Textarea
                placeholder="Paste course descriptions here... (e.g. 'CS101: Introduction to Object Oriented Programming using Java...')"
                className="min-h-[400px] bg-background border-border text-foreground font-mono text-sm"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                disabled={isAnalyzed}
              />
            </CardContent>
          </Card>
        </div>

        {/* RIGHT COLUMN: RESULTS */}
        <div className="md:col-span-1">
          {isAnalyzed ? (
            <div className="space-y-6 animate-in fade-in slide-in-from-right duration-200 ease-out">

              {/* Score Card */}
              <Card className="bg-card border-border text-center py-6">
                <div className="text-muted-foreground text-sm font-medium uppercase tracking-wider mb-2">Readiness Score</div>
                <div className={`text-5xl font-bold tabular-nums ${score > 70 ? 'text-success' : score > 40 ? 'text-warning' : 'text-destructive'}`}>
                  {score}%
                </div>
                <div className="text-xs text-muted-foreground mt-2 px-4">
                  Based on matches against top market skills for this role.
                </div>
              </Card>

              {/* Missing Skills (The Gap) */}
              <Card className="bg-card border-border">
                <CardHeader className="pb-2">
                  <CardTitle className="text-destructive flex items-center gap-2 text-lg">
                    <AlertCircle className="h-5 w-5" /> Missing Skills
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {missingSkills.length > 0 ? missingSkills.map(skill => (
                      <Badge key={skill} variant="outline" className="border-destructive/30 bg-destructive/10 text-destructive hover:bg-destructive/20">
                        {skill}
                      </Badge>
                    )) : (
                      <span className="text-muted-foreground text-sm">None! You are fully covered.</span>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Found Skills */}
              <Card className="bg-card border-border">
                <CardHeader className="pb-2">
                  <CardTitle className="text-success flex items-center gap-2 text-lg">
                    <CheckCircle2 className="h-5 w-5" /> Covered
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {foundSkills.length > 0 ? foundSkills.map(skill => (
                      <Badge key={skill} variant="outline" className="border-success/30 bg-success/10 text-success">
                        {skill}
                      </Badge>
                    )) : (
                      <span className="text-muted-foreground text-sm">No matches found. Try pasting more detailed descriptions.</span>
                    )}
                  </div>
                </CardContent>
              </Card>

            </div>
          ) : (
            // Empty State
            <div className="h-full flex items-center justify-center border-2 border-dashed border-border rounded-xl p-6 text-center text-muted-foreground">
              <div>
                <AlertCircle className="h-10 w-10 mx-auto mb-4 opacity-50" />
                <p className="text-sm">
                  Waiting for input... <br/>
                  Select a role and run the analysis to see your results here.
                </p>
              </div>
            </div>
          )}
        </div>

      </div>
      </main>
    </AppShell>
  )
}
