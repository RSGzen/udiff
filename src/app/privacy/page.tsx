import type { Metadata } from "next"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import { generatedAt } from "@/lib/data"

export const metadata: Metadata = {
  title: "Privacy — UDiff",
  description:
    "What UDiff collects, what it doesn't, and where its job-market data comes from.",
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-3">
      <h3 className="text-lg font-semibold text-foreground">{title}</h3>
      <div className="space-y-2 text-sm leading-relaxed text-muted-foreground">{children}</div>
    </section>
  )
}

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Minimal header */}
      <header className="border-b border-border">
        <div className="mx-auto flex h-16 max-w-3xl items-center justify-between px-6">
          <Link href="/" className="text-xl font-bold text-primary">
            UDiff
          </Link>
          <Button asChild variant="ghost" className="text-muted-foreground hover:text-foreground">
            <Link href="/dashboard">
              <ArrowLeft className="mr-2 h-4 w-4" /> Back to dashboard
            </Link>
          </Button>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-6 py-12">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Privacy</h1>
        <p className="mt-2 text-muted-foreground">
          UDiff is a data-visualisation project about job-market demand. It is built so that there is
          almost nothing personal to protect. Snapshot generated {generatedAt}.
        </p>

        <div className="mt-10 space-y-10">
          <Section title="The short version">
            <p>
              No accounts. No cookies. No analytics. Nothing you do here is stored on our servers. The
              only thing kept is your career-roadmap progress, and it lives in <em>your</em> browser.
            </p>
          </Section>

          <Section title="What we don't collect">
            <ul className="list-disc space-y-1 pl-5">
              <li>No sign-up, login, or email.</li>
              <li>No cookies and no third-party trackers.</li>
              <li>No analytics or advertising.</li>
              <li>
                The <span className="text-foreground">Curriculum Checker runs entirely in your browser</span> —
                the syllabus you paste is <span className="text-foreground">never uploaded or sent anywhere</span>.
              </li>
            </ul>
          </Section>

          <Section title="What stays in your browser">
            <p>
              Career-roadmap progress is saved under a single <code>localStorage</code> key
              (<code>udiff-roadmap-progress</code>). It never leaves your device; clearing your browser
              storage removes it.
            </p>
          </Section>

          <Section title="What the server sees">
            <p>
              The site is hosted on <span className="text-foreground">Vercel</span>, which — like any web
              host — records standard access logs (IP address, user-agent, requested path) for security and
              operations. These are handled under Vercel&rsquo;s privacy policy and are not used by UDiff to
              identify you.
            </p>
          </Section>

          <Section title="Where the data comes from">
            <p>
              The dashboard does not collect data from you; it displays an{" "}
              <span className="text-foreground">aggregate snapshot of public job listings</span> gathered
              via the <span className="text-foreground">JSearch API (Google for Jobs)</span>, with salary
              estimates from <span className="text-foreground">Glassdoor</span> (attributed as
              &ldquo;Glassdoor via JSearch&rdquo;). Raw postings are not redistributed — only derived
              aggregates (skills, percentages, pay bands, deltas) are shown.
            </p>
            <p>
              Figures are <span className="text-foreground">best-effort and not authoritative</span>. UDiff
              is an independent project and is <span className="text-foreground">not affiliated with</span>{" "}
              LinkedIn, Indeed, Glassdoor, or Google. See{" "}
              <Link href="/methodology" className="text-primary hover:underline">
                Methodology
              </Link>{" "}
              for full caveats.
            </p>
          </Section>

          <Section title="Removing a listing or company">
            <p>
              If you are an employer or recruiter and want a company or posting removed from the dataset,
              open an issue on the{" "}
              <a
                href="https://github.com/RSGzen/udiff/issues"
                target="_blank"
                rel="noreferrer"
                className="text-primary hover:underline"
              >
                project&rsquo;s GitHub
              </a>{" "}
              and we will remove it.
            </p>
          </Section>

          <Section title="Changes">
            <p>
              Because this is a point-in-time project, this page may be updated as the data sources or
              hosting change. Material changes (e.g. adding analytics) would be reflected here.
            </p>
          </Section>
        </div>

        <p className="mt-12 border-t border-border pt-6 text-xs text-muted-foreground/70">
          This page is a plain-language summary, not legal advice.
        </p>
      </main>
    </div>
  )
}
