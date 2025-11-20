import Image from "next/image"
import { Separator } from "@/components/ui/separator"
import { SidebarTrigger } from "@/components/ui/sidebar"

export function SiteHeader() {
  return (
    <header className="group-has-data-[collapsible=icon]/sidebar-wrapper:h-12 flex h-12 shrink-0 items-center gap-2 border-b transition-[width,height] ease-linear">
      <div className="flex w-full items-center gap-1 px-4 lg:gap-2 lg:px-6">
        <SidebarTrigger className="-ml-1" />
        <Separator
          orientation="vertical"
          className="mx-2 data-[orientation=vertical]:h-4"
        />
        <Image
          src="/logo.png"
          alt="Amarta AI"
          width={24}
          height={24}
          className="shrink-0"
        />
        <h1 className="text-base font-semibold">Amarta AI Dashboard</h1>
      </div>
    </header>
  )
}
