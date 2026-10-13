import { AppShell } from "@/components/AppShell"
import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { generatedAt, getCountries, getCountry, getCountryName } from "@/lib/data"
import type { ObservedSalary } from "@/types"

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-3">
      <h3 className="text-lg font-semibold text-foreground">{title}</h3>
      <div className="space-y-2 text-sm leading-relaxed text-muted-foreground">{children}</div>
    </section>
  )
}

function ObservedList({ data }: { data: ObservedSalary[] }) {
  if (data.length === 0) {
    return <p className="text-sm text-muted-foreground">No mentions mined for this market.</p>
  }
  return (
    <ul className="space-y-2">
      {data.map((s, i) => (
        <li key={i} className="flex items-start gap-3">
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
              <Badge variant="outline" className="border-border px-1.5 text-[10px] font-medium text-muted-foreground">
                annual
              </Badge>
            )}
          </div>
        </li>
      ))}
    </ul>
  )
}

export default function MethodologyPage() {
  const countries = getCountries()

  return (
    <AppShell>
      <main className="p-8">
        <div className="mx-auto max-w-3xl">
          {/* Header */}
          <div className="mb-10 border-b border-border pb-8">
            <h2 className="text-3xl font-bold tracking-tight text-foreground">Methodology &amp; Data</h2>
            <p className="mt-2 text-muted-foreground">
              How UDiff gathers and processes Malaysian, Singaporean and Indonesian tech-job demand — and
              where it falls short.
            </p>
            <p className="mt-1 text-xs text-muted-foreground/70">Snapshot generated {generatedAt}.</p>
          </div>

          <div className="space-y-10">
            <Section title="1. Where the data comes from">
              <ul className="list-disc space-y-1 pl-5">
                <li>
                  Job postings come from the <span className="text-foreground">JSearch API</span> (a
                  &ldquo;Google for Jobs&rdquo; aggregator), queried per role keyword with the location in the
                  query, for <span className="text-foreground">Malaysia, Singapore and Indonesia</span>{" "}
                  (<code>language=en</code>).
                </li>
                <li>Each posting is de-duplicated by (country, job id); its full description is kept.</li>
                <li>
                  <span className="text-foreground">Vietnam was dropped</span> — with <code>language=en</code>{" "}
                  the API returns no VN postings.
                </li>
                <li>
                  It is a <span className="text-foreground">point-in-time snapshot</span> ({generatedAt});
                  there is no scheduler or live refresh.
                </li>
              </ul>
            </Section>

            <Section title="2. How it's processed">
              <ol className="list-decimal space-y-1 pl-5">
                <li>
                  <span className="text-foreground">Extract</span> — a local LLM (Qwen3 8B via Ollama) reads
                  each description and returns <code>hard_skills</code>, <code>soft_skills</code>,{" "}
                  <code>technical_context</code>, <code>experience_level</code>.
                </li>
                <li>
                  <span className="text-foreground">Analyze</span> — titles are bucketed into role categories
                  (keyword heuristics); skills/contexts are aggregated per country × role × level, plus{" "}
                  <code>states</code>, <code>top_companies</code> and text-mined <code>observed_salaries</code>.
                </li>
                <li>
                  <span className="text-foreground">Estimate pay</span> — JSearch&rsquo;s{" "}
                  <code>/estimated-salary</code> gives a range per role × level (reliability-guarded),
                  converted to <span className="text-foreground">nominal MYR</span> (dated FX) and{" "}
                  <span className="text-foreground">PPP-adjusted MYR</span> (World Bank private-consumption PPP).
                </li>
                <li>
                  <span className="text-foreground">Compare</span> — every market is compared to Malaysia
                  (<code>my-vs-sg</code>, <code>my-vs-id</code>): skill-gap and salary deltas.
                </li>
                <li>
                  <span className="text-foreground">Curriculum</span> — an LLM generates plausible course
                  names per top skill → the skill→course dictionary behind the checker.
                </li>
              </ol>
            </Section>

            <Section title="3. Caveats & limitations">
              <ul className="list-disc space-y-1 pl-5">
                <li>
                  <span className="text-foreground">Salary sparsity:</span> most postings hide pay. The{" "}
                  <span className="text-foreground">salary estimate is a publisher estimate</span> for a
                  representative title per category (not per posting); its period is normalised to monthly
                  (<code>period_raw</code> keeps the source). <code>observed_salaries</code> are{" "}
                  <span className="text-foreground">text-mined from ad copy</span> — sparse and best-effort.
                </li>
                <li>
                  <span className="text-foreground">No ground truth:</span> skill/context extraction is
                  prompt-based and unvalidated; category assignment is keyword heuristics and brittle.
                </li>
                <li>
                  <span className="text-foreground">Curriculum is synthetic:</span> course names are
                  LLM-generated, and matching is <span className="text-foreground">lexical, not semantic</span>.
                </li>
                <li>
                  <span className="text-foreground">Currency:</span> FX and PPP live in dated static tables
                  and go stale; PPP is an economy-wide basket, not expat cost-of-living.
                </li>
              </ul>
            </Section>

            <Section title="4. Known data quirks">
              <p>
                A few markets show non-monotonic pay — e.g.{" "}
                <span className="text-foreground">SG Cybersecurity Junior &gt; Mid</span> and{" "}
                <span className="text-foreground">ID Fullstack Mid ≈ Senior</span> — which is upstream{" "}
                <code>/estimated-salary</code> variance on small samples. The pipeline normalises periods and
                suppresses inverting fallbacks, but does not smooth real reported values.
              </p>
            </Section>

            <Section title="5. Sample sizes">
              <div className="grid gap-3 sm:grid-cols-3">
                {countries.map((cc) => {
                  const c = getCountry(cc)
                  return (
                    <div key={cc} className="rounded-lg border border-border bg-card p-4">
                      <div className="text-2xl font-bold tabular-nums text-foreground">
                        {c.total_jobs_analyzed.toLocaleString()}
                      </div>
                      <div className="text-xs text-muted-foreground">{getCountryName(cc)} postings analysed</div>
                    </div>
                  )
                })}
              </div>
            </Section>

            <Section title="6. Full observed salary mentions">
              <p>
                Every pay string mined from ad text, per market. Values are shown in the source currency and
                flagged <em>annual</em> when the text implies a yearly figure.
              </p>
              <div className="mt-4 space-y-6">
                {countries.map((cc) => (
                  <Card key={cc} className="bg-card border-border">
                    <CardHeader>
                      <CardTitle className="text-sm text-foreground">
                        {getCountryName(cc)}{" "}
                        <span className="font-normal text-muted-foreground">
                          · {getCountry(cc).observed_salaries.length} mentions
                        </span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ObservedList data={getCountry(cc).observed_salaries} />
                    </CardContent>
                  </Card>
                ))}
              </div>
            </Section>
          </div>
          <p className="mt-10 border-t border-border pt-6 text-xs text-muted-foreground/70">
            See also:{" "}
            <Link href="/privacy" className="text-primary hover:underline">
              Privacy
            </Link>
            .
          </p>
        </div>
      </main>
    </AppShell>
  )
}
