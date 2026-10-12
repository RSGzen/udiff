"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard,
  ArrowLeftRight,
  Route,
  GraduationCap,
  PanelLeftClose,
  PanelLeftOpen,
  Menu,
  X,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

const NAV = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/compare", label: "Compare", icon: ArrowLeftRight },
  { href: "/roadmap", label: "Roadmap", icon: Route },
  { href: "/curriculum", label: "Curriculum", icon: GraduationCap },
]

function NavList({ collapsed, onNavigate }: { collapsed: boolean; onNavigate?: () => void }) {
  const pathname = usePathname()

  return (
    <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
      {NAV.map(({ href, label, icon: Icon }) => {
        const active = href === "/" ? pathname === "/" : pathname.startsWith(href)
        return (
          <Button
            key={href}
            asChild
            variant={active ? "secondary" : "ghost"}
            title={collapsed ? label : undefined}
            className={cn(
              "w-full",
              collapsed ? "justify-center px-0" : "justify-start",
              active
                ? "bg-muted text-foreground"
                : "text-muted-foreground hover:text-foreground hover:bg-muted"
            )}
          >
            <Link href={href} onClick={onNavigate}>
              <Icon className={cn("h-4 w-4 shrink-0", !collapsed && "mr-2")} />
              {!collapsed && label}
            </Link>
          </Button>
        )
      })}
    </nav>
  )
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <div className="min-h-screen bg-background text-foreground flex">
      {/* Desktop sidebar (collapsible to icon rail) */}
      <aside
        className={cn(
          "hidden lg:flex flex-col border-r border-border bg-background h-screen sticky top-0 shrink-0 overflow-hidden transition-[width] duration-200",
          collapsed ? "w-[4.5rem]" : "w-64"
        )}
      >
        <div className={cn("py-6 border-b border-border shrink-0", collapsed ? "px-2 text-center" : "px-6")}>
          <Link href="/" className="block">
            <h1 className={cn("font-bold text-primary", collapsed ? "text-lg" : "text-2xl")}>
              {collapsed ? "U" : "UDiff"}
            </h1>
            {!collapsed && <p className="text-muted-foreground text-xs mt-1">Student to Founder</p>}
          </Link>
        </div>

        <NavList collapsed={collapsed} />

        <div className="p-2 border-t border-border shrink-0">
          <Button
            variant="ghost"
            className="w-full justify-center text-muted-foreground hover:text-foreground"
            onClick={() => setCollapsed((v) => !v)}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {collapsed ? (
              <PanelLeftOpen className="h-4 w-4" />
            ) : (
              <>
                <PanelLeftClose className="h-4 w-4" />
                <span className="ml-2">Collapse</span>
              </>
            )}
          </Button>
        </div>
      </aside>

      {/* Mobile top bar */}
      <header className="lg:hidden fixed top-0 inset-x-0 z-40 h-14 border-b border-border bg-background flex items-center justify-between px-4">
        <Link href="/" className="text-lg font-bold text-primary">UDiff</Link>
        <Button variant="ghost" size="icon" onClick={() => setMobileOpen(true)} aria-label="Open menu">
          <Menu className="h-5 w-5" />
        </Button>
      </header>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="lg:hidden fixed inset-0 z-50">
          <div
            className="absolute inset-0 bg-background/70 backdrop-blur-sm"
            onClick={() => setMobileOpen(false)}
          />
          <div className="absolute left-0 top-0 bottom-0 w-64 bg-background border-r border-border flex flex-col">
            <div className="flex items-center justify-between px-6 py-6 border-b border-border shrink-0">
              <span className="text-xl font-bold text-primary">UDiff</span>
              <Button variant="ghost" size="icon" onClick={() => setMobileOpen(false)} aria-label="Close menu">
                <X className="h-5 w-5" />
              </Button>
            </div>
            <NavList collapsed={false} onNavigate={() => setMobileOpen(false)} />
          </div>
        </div>
      )}

      <div className="flex-1 min-w-0 pt-14 lg:pt-0">{children}</div>
    </div>
  )
}
