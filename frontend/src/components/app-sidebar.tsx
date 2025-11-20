"use client"

import * as React from "react"
import Image from "next/image"
import {
  BarChartIcon,
  CreditCardIcon,
  UsersIcon,
  BrainCircuitIcon,
  TrendingUpIcon,
} from "lucide-react"

import { NavMain } from "@/components/nav-main"
import { NavUser } from "@/components/nav-user"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"

const data = {
  user: {
    name: "Loan Officer",
    email: "officer@amarta.ai",
    avatar: "/avatars/user.jpg",
  },
  navMain: [
    {
      title: "Dashboard",
      url: "/",
      icon: BarChartIcon,
    },
    {
      title: "Borrowers",
      url: "/borrowers",
      icon: UsersIcon,
    },
    {
      title: "Loans",
      url: "/loans",
      icon: CreditCardIcon,
    },
    {
      title: "Credit Assessment",
      url: "/credit-assessment",
      icon: BrainCircuitIcon,
    },
    {
      title: "Analytics",
      url: "/analytics",
      icon: TrendingUpIcon,
    },
  ],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="offcanvas" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              asChild
              className="data-[slot=sidebar-menu-button]:!p-1.5"
            >
              <a href="/">
                <Image
                  src="/logo.png"
                  alt="Amarta AI Logo"
                  width={28}
                  height={28}
                  className="shrink-0"
                />
                <span className="text-base font-semibold">Amarta AI</span>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user} />
      </SidebarFooter>
    </Sidebar>
  )
}
