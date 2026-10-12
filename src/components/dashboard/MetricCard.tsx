import { Card, CardTitle } from "@/components/ui/card";
import { LucideIcon } from "lucide-react"; // Default icon library in Next.js

interface MetricCardProps {
  title: string;
  value: string | number;
  subtext?: string;
  icon?: LucideIcon;
}

export function MetricCard({ title, value, subtext, icon: Icon }: MetricCardProps) {
  return (
    <Card className="relative bg-card border-border">
      <CardTitle className="absolute top-6 left-6 text-base font-medium text-muted-foreground">
        {title}
      </CardTitle>
      {Icon && <Icon className="absolute top-6 right-6 h-4 w-4 text-muted-foreground" />}
      <div className="flex min-h-[7rem] items-center px-6">
        <div className="text-4xl font-bold text-foreground tabular-nums">{value}</div>
      </div>
      {subtext && (
        <p className="absolute bottom-6 left-6 text-sm text-muted-foreground">
          {subtext}
        </p>
      )}
    </Card>
  );
}
