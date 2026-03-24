"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { getRole, clearAuth, isAuthenticated } from "@/lib/auth";
import { formatDate, statusColor } from "@/lib/utils";
import { FileText, Bell, Plus, LogOut, Settings, ClipboardList, Shield } from "lucide-react";
import type { Application, NotificationList, UserRole } from "@/types";

export default function DashboardPage() {
  const router = useRouter();
  const [role, setRole] = useState<UserRole | null>(null);
  const [applications, setApplications] = useState<Application[]>([]);
  const [notifications, setNotifications] = useState<NotificationList | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated()) { router.push("/login"); return; }
    setRole(getRole());
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [apps, notifs] = await Promise.all([
        api.listApplications() as Promise<{ items: Application[]; total: number }>,
        api.listNotifications() as Promise<NotificationList>,
      ]);
      setApplications(apps.items);
      setNotifications(notifs);
    } catch {
      // Session expired
      clearAuth();
      router.push("/login");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => { clearAuth(); router.push("/login"); };

  if (loading) return <div className="flex items-center justify-center min-h-screen">Loading…</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-900">Onboarding Portal</h1>
        <div className="flex items-center gap-4">
          <button className="relative p-2 hover:bg-gray-100 rounded-lg" onClick={() => router.push("/notifications")}>
            <Bell className="w-5 h-5 text-gray-600" />
            {notifications && notifications.unread_count > 0 && (
              <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                {notifications.unread_count}
              </span>
            )}
          </button>
          {(role === "reviewer" || role === "approver") && (
            <button className="p-2 hover:bg-gray-100 rounded-lg" onClick={() => router.push("/review")}>
              <ClipboardList className="w-5 h-5 text-gray-600" />
            </button>
          )}
          {role === "admin" && (
            <button className="p-2 hover:bg-gray-100 rounded-lg" onClick={() => router.push("/admin")}>
              <Settings className="w-5 h-5 text-gray-600" />
            </button>
          )}
          {(role === "compliance" || role === "admin") && (
            <button className="p-2 hover:bg-gray-100 rounded-lg" onClick={() => router.push("/audit")}>
              <Shield className="w-5 h-5 text-gray-600" />
            </button>
          )}
          <button className="p-2 hover:bg-gray-100 rounded-lg" onClick={handleLogout}>
            <LogOut className="w-5 h-5 text-gray-600" />
          </button>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-5xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">My Applications</h2>
          {role === "customer" && (
            <button
              onClick={() => router.push("/apply")}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary-600 text-white font-medium hover:bg-primary-700"
            >
              <Plus className="w-4 h-4" /> New Application
            </button>
          )}
        </div>

        {applications.length === 0 ? (
          <div className="text-center py-16 text-gray-500">
            <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>No applications yet. Start your onboarding!</p>
          </div>
        ) : (
          <div className="space-y-3">
            {applications.map((app) => (
              <div
                key={app.id}
                className="flex items-center justify-between p-4 bg-white rounded-xl border border-gray-200 hover:border-primary-200 cursor-pointer transition-colors"
                onClick={() => router.push(`/applications/${app.application_id}`)}
              >
                <div>
                  <p className="font-medium text-gray-900">{app.application_id}</p>
                  <p className="text-sm text-gray-500">Submitted {formatDate(app.submitted_at)}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColor(app.status)}`}>
                  {app.status.replace(/_/g, " ")}
                </span>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
