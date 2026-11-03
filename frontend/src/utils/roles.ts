import type { UserPublic } from "@/client"

export enum Role {
  ADMIN = "admin",
  MANAGER = "manager",
  MEMBER = "member",
}

export const getUserRole = (user?: UserPublic | null): Role => {
  if (!user) return Role.MEMBER
  return (user.role ?? Role.MEMBER) as Role
}

export const canManageUsers = (user?: UserPublic | null) =>
  getUserRole(user) === Role.ADMIN

export const canViewUsers = (user?: UserPublic | null) =>
  [Role.ADMIN, Role.MANAGER].includes(getUserRole(user))

export const canViewMetrics = (user?: UserPublic | null) =>
  [Role.ADMIN, Role.MANAGER].includes(getUserRole(user))
