"use client"

import * as React from "react"
import { Area, AreaChart, CartesianGrid, XAxis } from "recharts"

import { useIsMobile } from "@/hooks/use-mobile"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  ToggleGroup,
  ToggleGroupItem,
} from "@/components/ui/toggle-group"
const chartData = [
  { date: "2024-04-01", approved: 12, pending: 8 },
  { date: "2024-04-02", approved: 15, pending: 6 },
  { date: "2024-04-03", approved: 18, pending: 7 },
  { date: "2024-04-04", approved: 14, pending: 9 },
  { date: "2024-04-05", approved: 21, pending: 5 },
  { date: "2024-04-06", approved: 19, pending: 8 },
  { date: "2024-04-07", approved: 16, pending: 6 },
  { date: "2024-04-08", approved: 23, pending: 7 },
  { date: "2024-04-09", approved: 17, pending: 9 },
  { date: "2024-04-10", approved: 20, pending: 6 },
  { date: "2024-04-11", approved: 22, pending: 8 },
  { date: "2024-04-12", approved: 18, pending: 7 },
  { date: "2024-04-13", approved: 25, pending: 5 },
  { date: "2024-04-14", approved: 19, pending: 10 },
  { date: "2024-04-15", approved: 21, pending: 6 },
  { date: "2024-04-16", approved: 24, pending: 8 },
  { date: "2024-04-17", approved: 20, pending: 7 },
  { date: "2024-04-18", approved: 26, pending: 9 },
  { date: "2024-04-19", approved: 22, pending: 6 },
  { date: "2024-04-20", approved: 18, pending: 8 },
  { date: "2024-04-21", approved: 23, pending: 7 },
  { date: "2024-04-22", approved: 27, pending: 5 },
  { date: "2024-04-23", approved: 21, pending: 9 },
  { date: "2024-04-24", approved: 24, pending: 6 },
  { date: "2024-04-25", approved: 28, pending: 8 },
  { date: "2024-04-26", approved: 19, pending: 7 },
  { date: "2024-04-27", approved: 25, pending: 6 },
  { date: "2024-04-28", approved: 22, pending: 9 },
  { date: "2024-04-29", approved: 26, pending: 5 },
  { date: "2024-04-30", approved: 29, pending: 8 },
  { date: "2024-05-01", approved: 23, pending: 7 },
  { date: "2024-05-02", approved: 27, pending: 6 },
  { date: "2024-05-03", approved: 21, pending: 9 },
  { date: "2024-05-04", approved: 30, pending: 5 },
  { date: "2024-05-05", approved: 25, pending: 8 },
  { date: "2024-05-06", approved: 28, pending: 7 },
  { date: "2024-05-07", approved: 24, pending: 6 },
  { date: "2024-05-08", approved: 31, pending: 9 },
  { date: "2024-05-09", approved: 26, pending: 5 },
  { date: "2024-05-10", approved: 29, pending: 8 },
  { date: "2024-05-11", approved: 27, pending: 7 },
  { date: "2024-05-12", approved: 23, pending: 6 },
  { date: "2024-05-13", approved: 32, pending: 9 },
  { date: "2024-05-14", approved: 28, pending: 5 },
  { date: "2024-05-15", approved: 25, pending: 8 },
  { date: "2024-05-16", approved: 30, pending: 7 },
  { date: "2024-05-17", approved: 26, pending: 6 },
  { date: "2024-05-18", approved: 33, pending: 9 },
  { date: "2024-05-19", approved: 24, pending: 5 },
  { date: "2024-05-20", approved: 29, pending: 8 },
  { date: "2024-05-21", approved: 27, pending: 7 },
  { date: "2024-05-22", approved: 31, pending: 6 },
  { date: "2024-05-23", approved: 28, pending: 9 },
  { date: "2024-05-24", approved: 25, pending: 5 },
  { date: "2024-05-25", approved: 34, pending: 8 },
  { date: "2024-05-26", approved: 30, pending: 7 },
  { date: "2024-05-27", approved: 26, pending: 6 },
  { date: "2024-05-28", approved: 32, pending: 9 },
  { date: "2024-05-29", approved: 29, pending: 5 },
  { date: "2024-05-30", approved: 27, pending: 8 },
  { date: "2024-05-31", approved: 35, pending: 7 },
  { date: "2024-06-01", approved: 31, pending: 6 },
  { date: "2024-06-02", approved: 28, pending: 9 },
  { date: "2024-06-03", approved: 33, pending: 5 },
  { date: "2024-06-04", approved: 30, pending: 8 },
  { date: "2024-06-05", approved: 26, pending: 7 },
  { date: "2024-06-06", approved: 36, pending: 6 },
  { date: "2024-06-07", approved: 32, pending: 9 },
  { date: "2024-06-08", approved: 29, pending: 5 },
  { date: "2024-06-09", approved: 34, pending: 8 },
  { date: "2024-06-10", approved: 27, pending: 7 },
  { date: "2024-06-11", approved: 31, pending: 6 },
  { date: "2024-06-12", approved: 37, pending: 9 },
  { date: "2024-06-13", approved: 33, pending: 5 },
  { date: "2024-06-14", approved: 30, pending: 8 },
  { date: "2024-06-15", approved: 35, pending: 7 },
  { date: "2024-06-16", approved: 28, pending: 6 },
  { date: "2024-06-17", approved: 32, pending: 9 },
  { date: "2024-06-18", approved: 38, pending: 5 },
  { date: "2024-06-19", approved: 34, pending: 8 },
  { date: "2024-06-20", approved: 31, pending: 7 },
  { date: "2024-06-21", approved: 36, pending: 6 },
  { date: "2024-06-22", approved: 29, pending: 9 },
  { date: "2024-06-23", approved: 33, pending: 5 },
  { date: "2024-06-24", approved: 39, pending: 8 },
  { date: "2024-06-25", approved: 35, pending: 7 },
  { date: "2024-06-26", approved: 32, pending: 6 },
  { date: "2024-06-27", approved: 37, pending: 9 },
  { date: "2024-06-28", approved: 30, pending: 5 },
  { date: "2024-06-29", approved: 34, pending: 8 },
  { date: "2024-06-30", approved: 40, pending: 7 },
]

const chartConfig = {
  loans: {
    label: "Loan Applications",
  },
  approved: {
    label: "Approved",
    color: "hsl(var(--chart-1))",
  },
  pending: {
    label: "Pending Review",
    color: "hsl(var(--chart-2))",
  },
} satisfies ChartConfig

export function ChartAreaInteractive() {
  const isMobile = useIsMobile()
  const [timeRange, setTimeRange] = React.useState("30d")

  React.useEffect(() => {
    if (isMobile) {
      setTimeRange("7d")
    }
  }, [isMobile])

  const filteredData = chartData.filter((item) => {
    const date = new Date(item.date)
    const referenceDate = new Date("2024-06-30")
    let daysToSubtract = 90
    if (timeRange === "30d") {
      daysToSubtract = 30
    } else if (timeRange === "7d") {
      daysToSubtract = 7
    }
    const startDate = new Date(referenceDate)
    startDate.setDate(startDate.getDate() - daysToSubtract)
    return date >= startDate
  })

  return (
    <Card className="@container/card">
      <CardHeader className="relative">
        <CardTitle>Loan Applications</CardTitle>
        <CardDescription>
          <span className="@[540px]/card:block hidden">
            Application trends for the last 3 months
          </span>
          <span className="@[540px]/card:hidden">Last 3 months</span>
        </CardDescription>
        <div className="absolute right-4 top-4">
          <ToggleGroup
            type="single"
            value={timeRange}
            onValueChange={setTimeRange}
            variant="outline"
            className="@[767px]/card:flex hidden"
          >
            <ToggleGroupItem value="90d" className="h-8 px-2.5">
              Last 3 months
            </ToggleGroupItem>
            <ToggleGroupItem value="30d" className="h-8 px-2.5">
              Last 30 days
            </ToggleGroupItem>
            <ToggleGroupItem value="7d" className="h-8 px-2.5">
              Last 7 days
            </ToggleGroupItem>
          </ToggleGroup>
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger
              className="@[767px]/card:hidden flex w-40"
              aria-label="Select a value"
            >
              <SelectValue placeholder="Last 3 months" />
            </SelectTrigger>
            <SelectContent className="rounded-xl">
              <SelectItem value="90d" className="rounded-lg">
                Last 3 months
              </SelectItem>
              <SelectItem value="30d" className="rounded-lg">
                Last 30 days
              </SelectItem>
              <SelectItem value="7d" className="rounded-lg">
                Last 7 days
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
      </CardHeader>
      <CardContent className="px-2 pt-4 sm:px-6 sm:pt-6">
        <ChartContainer
          config={chartConfig}
          className="aspect-auto h-[250px] w-full"
        >
          <AreaChart data={filteredData}>
            <defs>
              <linearGradient id="fillDesktop" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="var(--color-approved)"
                  stopOpacity={1.0}
                />
                <stop
                  offset="95%"
                  stopColor="var(--color-approved)"
                  stopOpacity={0.1}
                />
              </linearGradient>
              <linearGradient id="fillMobile" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="var(--color-pending)"
                  stopOpacity={0.8}
                />
                <stop
                  offset="95%"
                  stopColor="var(--color-pending)"
                  stopOpacity={0.1}
                />
              </linearGradient>
            </defs>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="date"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              minTickGap={32}
              tickFormatter={(value) => {
                const date = new Date(value)
                return date.toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                })
              }}
            />
            <ChartTooltip
              cursor={false}
              content={
                <ChartTooltipContent
                  labelFormatter={(value) => {
                    return new Date(value).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                    })
                  }}
                  indicator="dot"
                />
              }
            />
            <Area
              dataKey="pending"
              type="natural"
              fill="url(#fillMobile)"
              stroke="var(--color-pending)"
              stackId="a"
            />
            <Area
              dataKey="approved"
              type="natural"
              fill="url(#fillDesktop)"
              stroke="var(--color-approved)"
              stackId="a"
            />
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
