import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Suspense } from "react"

import { MetricsService } from "@/client"
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { requirePermission } from "@/hooks/useAuth"
import { roleLabels, USER_ROLES } from "@/lib/roles"

function getMetricsQueryOptions() {
  return {
    queryFn: async () => (await MetricsService.readMetrics()).data,
    queryKey: ["metrics"],
  }
}

export const Route = createFileRoute("/_layout/metrics")({
  component: Metrics,
  beforeLoad: () => requirePermission("metrics:read"),
  head: () => ({
    meta: [
      {
        title: "Metrics - FastAPI Template",
      },
    ],
  }),
})

function MetricsCards() {
  const { data: metrics } = useSuspenseQuery(getMetricsQueryOptions())

  const cards = [
    { label: "Total users", value: metrics.total_users },
    { label: "Active users", value: metrics.active_users },
    ...USER_ROLES.map((role) => ({
      label: `${roleLabels[role]}s`,
      value: metrics.users_by_role[role] ?? 0,
    })),
    { label: "Items", value: metrics.total_items },
  ]

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {cards.map((card) => (
        <Card key={card.label}>
          <CardHeader>
            <CardDescription>{card.label}</CardDescription>
            <CardTitle className="text-3xl tabular-nums">
              {card.value}
            </CardTitle>
          </CardHeader>
        </Card>
      ))}
    </div>
  )
}

function Metrics() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Metrics</h1>
        <p className="text-muted-foreground">An overview of users and items</p>
      </div>
      <Suspense fallback={<Skeleton className="h-32 w-full" />}>
        <MetricsCards />
      </Suspense>
    </div>
  )
}
