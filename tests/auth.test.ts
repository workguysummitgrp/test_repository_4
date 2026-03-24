import { describe, it, expect, beforeEach } from "vitest";
import { setAuth, getToken, getRole, getUserId, clearAuth, isAuthenticated } from "@/lib/auth";

// Mock localStorage for Node/jsdom
const store: Record<string, string> = {};
const mockStorage = {
  getItem: (key: string) => store[key] ?? null,
  setItem: (key: string, val: string) => { store[key] = val; },
  removeItem: (key: string) => { delete store[key]; },
};

Object.defineProperty(globalThis, "localStorage", { value: mockStorage, writable: true });

describe("auth helpers", () => {
  beforeEach(() => {
    for (const key of Object.keys(store)) delete store[key];
  });

  it("setAuth stores token, role and userId", () => {
    setAuth("tok123", "customer", 42);
    expect(getToken()).toBe("tok123");
    expect(getRole()).toBe("customer");
    expect(getUserId()).toBe(42);
  });

  it("isAuthenticated returns true when token exists", () => {
    setAuth("tok", "admin", 1);
    expect(isAuthenticated()).toBe(true);
  });

  it("isAuthenticated returns false when no token", () => {
    expect(isAuthenticated()).toBe(false);
  });

  it("clearAuth removes all keys", () => {
    setAuth("tok", "customer", 1);
    clearAuth();
    expect(getToken()).toBeNull();
    expect(getRole()).toBeNull();
    expect(getUserId()).toBeNull();
  });
});
