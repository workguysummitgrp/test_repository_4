import type { UserRole } from "@/types";

const TOKEN_KEY = "access_token";
const ROLE_KEY = "user_role";
const USER_ID_KEY = "user_id";

export function setAuth(token: string, role: string, userId: number) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(ROLE_KEY, role);
  localStorage.setItem(USER_ID_KEY, String(userId));
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function getRole(): UserRole | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ROLE_KEY) as UserRole | null;
}

export function getUserId(): number | null {
  if (typeof window === "undefined") return null;
  const id = localStorage.getItem(USER_ID_KEY);
  return id ? parseInt(id, 10) : null;
}

export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(ROLE_KEY);
  localStorage.removeItem(USER_ID_KEY);
}

export function isAuthenticated(): boolean {
  return !!getToken();
}
