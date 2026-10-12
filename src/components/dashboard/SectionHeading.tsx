interface SectionHeadingProps {
  title: string
  scope?: string
}

export function SectionHeading({ title, scope }: SectionHeadingProps) {
  return (
    <div className="flex items-center gap-3 pt-2">
      <h3 className="text-sm font-semibold text-foreground">{title}</h3>
      {scope && (
        <span className="rounded-full border border-border bg-muted px-2 py-0.5 text-[11px] font-medium text-muted-foreground">
          {scope}
        </span>
      )}
      <div className="h-px flex-1 bg-border" />
    </div>
  )
}
