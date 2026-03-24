import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock fetch globally
const mockFetch = vi.fn();
globalThis.fetch = mockFetch;

// Mock localStorage
const store: Record<string, string> = {};
Object.defineProperty(globalThis, "localStorage", {
  value: {
    getItem: (k: string) => store[k] ?? null,
    setItem: (k: string, v: string) => { store[k] = v; },
    removeItem: (k: string) => { delete store[k]; },
  },
  writable: true,
});

// Import after mocks
import { api } from "@/lib/api";

describe("API client", () => {
  beforeEach(() => {
    mockFetch.mockReset();
    for (const k of Object.keys(store)) delete store[k];
  });

  it("register sends POST with email and name", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ id: 1, email: "a@b.com" }),
    });

    await api.register("a@b.com", "Test User");

    expect(mockFetch).toHaveBeenCalledTimes(1);
    const [url, opts] = mockFetch.mock.calls[0];
    expect(url).toContain("/auth/register");
    expect(opts.method).toBe("POST");
    expect(JSON.parse(opts.body)).toEqual({ email: "a@b.com", full_name: "Test User" });
  });

  it("requestOTP sends email", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ message: "OTP sent" }),
    });

    const res = await api.requestOTP("a@b.com");
    expect(res.message).toBe("OTP sent");
  });

  it("throws on non-ok response", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ detail: "Not found" }),
    });

    await expect(api.requestOTP("a@b.com")).rejects.toThrow("Not found");
  });

  it("includes authorization header when token is set", async () => {
    store["access_token"] = "test-token";
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ items: [], total: 0 }),
    });

    await api.listApplications();

    const headers = mockFetch.mock.calls[0][1].headers;
    expect(headers.Authorization).toBe("Bearer test-token");
  });

  it("listApplications uses correct URL with pagination", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ items: [], total: 0 }),
    });

    await api.listApplications(2, 10);

    const url = mockFetch.mock.calls[0][0];
    expect(url).toContain("page=2");
    expect(url).toContain("size=10");
  });
});
