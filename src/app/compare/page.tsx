import { AppShell } from "@/components/AppShell"

export default function ComparePage() {
  return (
    <AppShell>
      <main className="p-8">
        <div className="border-b border-border pb-8 mb-8">
          <h2 className="text-3xl font-bold tracking-tight text-foreground">Compare Markets</h2>
          <p className="text-muted-foreground mt-2">
            How Malaysia&apos;s demand and pay stack up against Singapore and Indonesia.
          </p>
        </div>

        <div className="border-2 border-dashed border-border rounded-xl p-12 text-center text-muted-foreground">
          Coming soon — skill gaps and salary deltas (<span className="text-foreground">my-vs-sg</span>,{" "}
          <span className="text-foreground">my-vs-id</span>).
        </div>
      </main>
    </AppShell>
  )
}
