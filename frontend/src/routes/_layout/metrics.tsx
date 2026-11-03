import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute, redirect } from "@tanstack/react-router"

import { UsersService } from "@/client"
import { canViewMetrics } from "@/utils/roles"

function getMetricsQueryOptions() {
  return {
    queryFn: async () =>
      (await UsersService.readUsers({ query: { skip: 0, limit: 100 } })).data,
    queryKey: ["metrics"],
  }
}

export const Route = createFileRoute("/_layout/metrics")({
  component: Metrics,
  beforeLoad: async () => {
    const { data: user } = await UsersService.readUserMe()
    if (!canViewMetrics(user)) {
      throw redirect({
        to: "/forbidden",
      })
    }
  },
  head: () => ({
    meta: [
      {
        title: "Metrics - FastAPI Template",
      },
    ],
  }),
})

function Metrics() {
  const { data: result } = useSuspenseQuery(getMetricsQueryOptions())

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Metrics</h1>
        <p className="text-muted-foreground">
          Manager and admin insights for the current workspace.
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded border p-4">
          <p className="text-sm text-muted-foreground">Total users</p>
          <p className="text-2xl font-semibold">{result.count}</p>
        </div>
      </div>
    </div>
  )
}
