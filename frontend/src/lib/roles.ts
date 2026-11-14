import type { UserRole } from "@/client"

export const USER_ROLES = [
  "admin",
  "manager",
  "member",
] as const satisfies readonly UserRole[]

export const roleLabels: Record<UserRole, string> = {
  admin: "Admin",
  manager: "Manager",
  member: "Member",
}
