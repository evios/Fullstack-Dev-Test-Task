import { createFileRoute, Link } from "@tanstack/react-router"

import { Button } from "@/components/ui/button"

export const Route = createFileRoute("/_layout/forbidden")({
  component: Forbidden,
  head: () => ({
    meta: [
      {
        title: "Access denied - FastAPI Template",
      },
    ],
  }),
})

function Forbidden() {
  return (
    <div
      className="flex flex-col items-center justify-center gap-2 py-16 text-center"
      data-testid="forbidden"
    >
      <h1 className="text-2xl font-bold tracking-tight">Access denied</h1>
      <p className="text-muted-foreground">
        You don't have permission to view this page.
      </p>
      <Link to="/">
        <Button className="mt-4">Go to dashboard</Button>
      </Link>
    </div>
  )
}
