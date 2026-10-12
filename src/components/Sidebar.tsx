"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { LayoutDashboard, GraduationCap, Briefcase, Search, Settings } from "lucide-react"

interface SidebarProps {
  categories: string[]
  selectedCategory: string
  onSelectCategory: (cat: string) => void
  selectedLevel: string
  onSelectLevel: (level: string) => void
}

export function Sidebar({
  categories,
  selectedCategory,
  onSelectCategory,
  selectedLevel,
  onSelectLevel
}: SidebarProps) {

  const router = useRouter()

  // 1. Local State for Search
  const [searchTerm, setSearchTerm] = useState("")

  // 2. Filter Logic
  const filteredCategories = categories.filter(cat =>
    cat.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="w-64 border-r border-border bg-background flex flex-col h-screen fixed left-0 top-0">

      {/* --- HEADER SECTION (Fixed) --- */}
      <div className="p-6 border-b border-border shrink-0">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
          UDiff
        </h1>
        <p className="text-muted-foreground text-xs mt-1">Student to Founder</p>
      </div>

      <div className="px-4 pt-6 shrink-0 space-y-4">
        {/* Experience Slider */}
        <div>
           <h3 className="mb-2 px-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Experience Level
          </h3>
          <Tabs defaultValue="All" value={selectedLevel} onValueChange={onSelectLevel} className="w-full">
            <TabsList className="w-full bg-card border border-border">
              <TabsTrigger value="All" className="flex-1 text-xs">All</TabsTrigger>
              <TabsTrigger value="Junior" className="flex-1 text-xs">Jun</TabsTrigger>
              <TabsTrigger value="Mid" className="flex-1 text-xs">Mid</TabsTrigger>
              <TabsTrigger value="Senior" className="flex-1 text-xs">Sen</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search roles..."
            className="pl-8 bg-card border-border text-foreground focus-visible:ring-ring h-9"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {/* --- SCROLLABLE LIST (Flex Grow) --- */}
      <div className="flex-1 py-4 px-4 overflow-y-auto min-h-0">
        <h3 className="mb-2 px-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          Career Paths
        </h3>
        <div className="space-y-1">
          {filteredCategories.length > 0 ? (
            filteredCategories.map((cat) => (
              <Button
                key={cat}
                variant={selectedCategory === cat ? "secondary" : "ghost"}
                className={`w-full justify-start ${
                  selectedCategory === cat
                    ? "bg-muted text-foreground"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted"
                }`}
                onClick={() => onSelectCategory(cat)}
              >
                <Briefcase className="mr-2 h-4 w-4 shrink-0" />
                <span className="truncate">{cat}</span>
              </Button>
            ))
          ) : (
            <div className="text-xs text-muted-foreground/70 px-2 py-4 text-center">
              No roles found
            </div>
          )}
        </div>
      </div>

      {/* --- FOOTER SECTION (Pinned Bottom) --- */}
      <div className="p-4 border-t border-border bg-background shrink-0">
        <h3 className="mb-2 px-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          Tools
        </h3>
        <div className="space-y-1">
          <Button variant="ghost" className="w-full justify-start text-muted-foreground hover:text-foreground"
          onClick={() => router.push('/roadmap')}>
            <LayoutDashboard className="mr-2 h-4 w-4" />
            My Roadmap
          </Button>
          <Button variant="ghost" className="w-full justify-start text-muted-foreground hover:text-foreground"
          onClick={() => router.push('/curriculum')}>
            <GraduationCap className="mr-2 h-4 w-4" />
            Curriculum Check
          </Button>
           <Button variant="ghost" className="w-full justify-start text-muted-foreground hover:text-foreground">
            <Settings className="mr-2 h-4 w-4" />
            Settings
          </Button>
        </div>
      </div>

    </div>
  )
}
