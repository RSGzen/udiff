import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import {
  LayoutDashboard,
  ArrowLeftRight,
  Route,
  GraduationCap,
  ArrowRight,
  Github,
} from "lucide-react"
import { DEFAULT_COUNTRY, getCountries, getCountry, getCountryName, getRoles } from "@/lib/data"

const PIPELINE = [
  { step: "Fetch", desc: "Pull live postings from the JSearch API for MY, SG & ID." },
  { step: "Extract", desc: "A local LLM reads each ad for hard skills, soft skills & context." },
  { step: "Analyze", desc: "Aggregate demand per role × experience level, per country." },
  { step: "Estimate", desc: "Add attributed pay bands — nominal MYR and PPP-adjusted." },
  { step: "Compare", desc: "Diff every market against Malaysia." },
]

const FEATURES = [
  {
    href: "/dashboard",
    title: "Market Dashboard",
    desc: "In-demand skills, salary ranges, soft skills and hiring spread by role and experience.",
    icon: LayoutDashboard,
  },
  {
    href: "/compare",
    title: "Compare Markets",
    desc: "Skill gaps and salary deltas — Malaysia vs Singapore and Indonesia.",
    icon: ArrowLeftRight,
  },
  {
    href: "/roadmap",
    title: "Career Roadmaps",
    desc: "Gamified, phase-locked learning paths for 15+ roles, with saved progress.",
    icon: Route,
  },
  {
    href: "/curriculum",
    title: "Curriculum Checker",
    desc: "Paste a syllabus and see which in-demand skills it covers — and which it misses.",
    icon: GraduationCap,
  },
]

export default function LandingPage() {
  const countries = getCountries()
  const totalJobs = countries.reduce((sum, cc) => sum + getCountry(cc).total_jobs_analyzed, 0)
  const roles = getRoles(DEFAULT_COUNTRY).length

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="sticky top-0 z-40 border-b border-border bg-background/80 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-6">
          <Link href="/" className="text-xl font-bold text-primary">
            UDiff
          </Link>
          <nav className="flex items-center gap-2">
            <Button asChild variant="ghost" className="text-muted-foreground hover:text-foreground">
              <Link href="/methodology">Methodology</Link>
            </Button>
            <Button asChild className="bg-primary text-primary-foreground hover:bg-primary/90">
              <Link href="/dashboard">
                Open dashboard <ArrowRight className="ml-1 h-4 w-4" />
              </Link>
            </Button>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="mx-auto max-w-5xl px-6 pb-16 pt-20">
        <p className="text-sm font-medium uppercase tracking-wider text-primary">
          {countries.map(getCountryName).join(" · ")}
        </p>
        <h1 className="mt-4 max-w-3xl text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
          See the gap between what universities teach and what the market hires for.
        </h1>
        <p className="mt-6 max-w-2xl text-lg text-muted-foreground">
          UDiff turns thousands of live tech job postings into a comparable, honest snapshot of demand —
          the skills, salary bands and hiring spread behind each role — then checks a syllabus against it.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Button asChild size="lg" className="bg-primary text-primary-foreground hover:bg-primary/90">
            <Link href="/dashboard">Explore the dashboard</Link>
          </Button>
          <Button asChild size="lg" variant="outline">
            <Link href="/methodology">How the data works</Link>
          </Button>
        </div>
      </section>

      {/* Stats */}
      <section className="border-y border-border">
        <div className="mx-auto grid max-w-5xl grid-cols-3 gap-4 px-6 py-10">
          <div>
            <div className="text-3xl font-bold tabular-nums text-foreground">
              {totalJobs.toLocaleString()}
            </div>
            <div className="text-sm text-muted-foreground">postings analysed</div>
          </div>
          <div>
            <div className="text-3xl font-bold tabular-nums text-foreground">{countries.length}</div>
            <div className="text-sm text-muted-foreground">markets</div>
          </div>
          <div>
            <div className="text-3xl font-bold tabular-nums text-foreground">{roles}</div>
            <div className="text-sm text-muted-foreground">tech roles tracked</div>
          </div>
        </div>
      </section>

      {/* Pipeline */}
      <section className="mx-auto max-w-5xl px-6 py-16">
        <h2 className="text-2xl font-semibold text-foreground">How it works</h2>
        <p className="mt-2 text-muted-foreground">A one-way batch pipeline, from raw ads to a live report.</p>
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {PIPELINE.map((p, i) => (
            <div key={p.step} className="rounded-lg border border-border bg-card p-4">
              <div className="text-xs font-mono tabular-nums text-primary">{String(i + 1).padStart(2, "0")}</div>
              <div className="mt-2 font-semibold text-foreground">{p.step}</div>
              <div className="mt-1 text-sm text-muted-foreground">{p.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-5xl px-6 pb-20">
        <h2 className="text-2xl font-semibold text-foreground">Explore</h2>
        <div className="mt-8 grid gap-4 sm:grid-cols-2">
          {FEATURES.map(({ href, title, desc, icon: Icon }) => (
            <Link key={href} href={href} className="group">
              <Card className="h-full bg-card border-border transition-colors group-hover:border-primary/50">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3">
                    <Icon className="h-5 w-5 text-primary" />
                    <span className="font-semibold text-foreground">{title}</span>
                    <ArrowRight className="ml-auto h-4 w-4 text-muted-foreground transition-transform group-hover:translate-x-0.5 group-hover:text-foreground" />
                  </div>
                  <p className="mt-3 text-sm text-muted-foreground">{desc}</p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-4 px-6 py-8 text-sm text-muted-foreground">
          <p>
            UDiff — a point-in-time snapshot. Estimated and text-mined figures are best-effort, not
            authoritative.
          </p>
          <div className="flex items-center gap-4">
            <Link href="/methodology" className="hover:text-foreground">
              Methodology
            </Link>
            <a
              href="https://github.com/RSGzen/udiff"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1 hover:text-foreground"
            >
              <Github className="h-4 w-4" /> GitHub
            </a>
          </div>
        </div>
      </footer>
    </div>
  )
}
