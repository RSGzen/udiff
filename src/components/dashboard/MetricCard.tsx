import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LucideIcon } from "lucide-react"; // Default icon library in Next.js

interface MetricCardProps {
  title: string;
  value: string | number;
  subtext?: string;
  icon?: LucideIcon;
  trend?: "up" | "down" | "neutral";
}

export function MetricCard({ title, value, subtext, icon: Icon, trend }: MetricCardProps) {
  return (
    <Card className="bg-card border-border">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        {Icon && <Icon className="h-4 w-4 text-muted-foreground" />}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-foreground tabular-nums">{value}</div>
        {subtext && (
          <p className="text-xs text-muted-foreground mt-1">
            {subtext}
          </p>
        )}
      </CardContent>
    </Card>
  );
}