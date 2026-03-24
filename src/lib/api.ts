const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_V1 = `${API_BASE}/api/v1`;

function getAuthHeaders(): HeadersInit {
  if (typeof window === "undefined") return {};
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_V1}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
      ...init?.headers,
    },
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || "Request failed");
  }
  return res.json();
}

// Auth
export const api = {
  register: (email: string, full_name: string) =>
    request("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, full_name }),
    }),

  requestOTP: (email: string) =>
    request<{ message: string; otp_debug?: string }>("/auth/otp/request", {
      method: "POST",
      body: JSON.stringify({ email }),
    }),

  verifyOTP: (email: string, otp: string) =>
    request<{ access_token: string; role: string; user_id: number }>(
      "/auth/otp/verify",
      { method: "POST", body: JSON.stringify({ email, otp }) }
    ),

  getMe: () => request<{ id: number; email: string; full_name: string; role: string }>("/auth/me"),

  // Applications
  createApplication: (form_data: Record<string, unknown>) =>
    request("/applications/", {
      method: "POST",
      body: JSON.stringify({ form_data }),
    }),

  listApplications: (page = 1, size = 20) =>
    request<{ items: unknown[]; total: number }>(`/applications/?page=${page}&size=${size}`),

  getApplication: (appId: string) => request(`/applications/${appId}`),

  submitApplication: (appId: string) =>
    request(`/applications/${appId}/submit`, { method: "POST" }),

  saveDraft: (form_data: Record<string, unknown>, current_step: number) =>
    request("/applications/drafts", {
      method: "POST",
      body: JSON.stringify({ form_data, current_step }),
    }),

  getDraft: () => request("/applications/drafts/current"),

  // Documents
  uploadDocument: async (appId: string, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_V1}/documents/${appId}/upload`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: formData,
    });
    if (!res.ok) throw new Error("Upload failed");
    return res.json();
  },

  listDocuments: (appId: string) => request(`/documents/${appId}`),

  // Notifications
  listNotifications: () =>
    request<{ items: unknown[]; total: number; unread_count: number }>("/notifications/"),

  markNotificationRead: (id: number) =>
    request(`/notifications/${id}/read`, { method: "POST" }),

  // Reviews
  getReviewerQueue: () => request("/reviews/reviewer/queue"),
  getApproverQueue: () => request("/reviews/approver/queue"),

  submitReviewerDecision: (appId: number, decision: string, comment?: string) =>
    request(`/reviews/${appId}/reviewer-decision`, {
      method: "POST",
      body: JSON.stringify({ decision, comment }),
    }),

  submitApproverDecision: (appId: number, decision: string, comment: string) =>
    request(`/reviews/${appId}/approver-decision`, {
      method: "POST",
      body: JSON.stringify({ decision, comment }),
    }),

  // Evaluations
  getEvaluation: (applicationId: number) =>
    request(`/evaluations/${applicationId}`),

  // Admin
  getThresholds: () => request("/admin/thresholds"),
  updateThreshold: (band_name: string, min_score: number, max_score: number) =>
    request("/admin/thresholds", {
      method: "PUT",
      body: JSON.stringify({ band_name, min_score, max_score }),
    }),

  getWorkflowConfigs: () => request("/admin/workflow-config"),
  updateWorkflowConfig: (node_name: string, is_enabled: boolean) =>
    request("/admin/workflow-config", {
      method: "PUT",
      body: JSON.stringify({ node_name, is_enabled }),
    }),

  // Audit
  getAuditLogs: (applicationId?: number, page = 1, size = 20) => {
    const params = new URLSearchParams({ page: String(page), size: String(size) });
    if (applicationId) params.set("application_id", String(applicationId));
    return request(`/audit/?${params}`);
  },
};
