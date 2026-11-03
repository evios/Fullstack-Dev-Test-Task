import { createFileRoute, Link } from "@tanstack/react-router"

export const Route = createFileRoute("/forbidden")({
  component: Forbidden,
})

function Forbidden() {
  return (
    <div className="flex min-h-screen items-center justify-center px-6">
      <div className="w-full max-w-md rounded-lg border bg-background p-8 text-center shadow-sm">
        <p className="mb-3 text-sm font-medium uppercase tracking-[0.2em] text-muted-foreground">
          Access denied
        </p>
        <h1 className="text-3xl font-bold">Forbidden</h1>
        <p className="mt-4 text-muted-foreground">
          You do not have permission to view this page.
        </p>
        <Link className="mt-6 inline-flex rounded-md bg-primary px-4 py-2 text-primary-foreground" to="/">
          Return home
        </Link>
      </div>
    </div>
  )
}
