import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { redirect, useNavigate } from "@tanstack/react-router"
import { AxiosError } from "axios"

import {
  type Body_login_login_access_token as AccessToken,
  LoginService,
  type Permission,
  type UserMePublic,
  type UserRegister,
  UsersService,
} from "@/client"
import { handleError } from "@/utils"
import useCustomToast from "./useCustomToast"

const isLoggedIn = () => {
  return localStorage.getItem("access_token") !== null
}

// Route guard for `beforeLoad`. It fetches the current user on every
// navigation, so a role change applies without logging in again.
const requirePermission = async (permission: Permission) => {
  let user: UserMePublic
  try {
    user = (await UsersService.readUserMe()).data
  } catch (error) {
    if (error instanceof AxiosError && error.response?.status === 401) {
      localStorage.removeItem("access_token")
      throw redirect({ to: "/login" })
    }
    throw error
  }
  if (!user.permissions.includes(permission)) {
    throw redirect({ to: "/forbidden" })
  }
}

const useAuth = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { showErrorToast } = useCustomToast()

  const { data: user } = useQuery<UserMePublic | null, Error>({
    queryKey: ["currentUser"],
    queryFn: async () => (await UsersService.readUserMe()).data,
    enabled: isLoggedIn(),
  })

  const can = (permission: Permission) =>
    user?.permissions.includes(permission) ?? false

  const signUpMutation = useMutation({
    mutationFn: (data: UserRegister) =>
      UsersService.registerUser({ body: data }),
    onSuccess: () => {
      navigate({ to: "/login" })
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] })
    },
  })

  const login = async (data: AccessToken) => {
    const response = await LoginService.loginAccessToken({
      body: data,
    })
    localStorage.setItem("access_token", response.data.access_token)
  }

  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: () => {
      navigate({ to: "/" })
    },
    onError: handleError.bind(showErrorToast),
  })

  const logout = () => {
    localStorage.removeItem("access_token")
    navigate({ to: "/login" })
  }

  return {
    signUpMutation,
    loginMutation,
    logout,
    user,
    can,
  }
}

export { isLoggedIn, requirePermission }
export default useAuth
