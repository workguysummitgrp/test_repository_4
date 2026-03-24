"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import { formatDate } from "@/lib/utils";
import type { NotificationInfo } from "@/types";

export default function NotificationsPage() {
  const router = useRouter();
  const [notifications, setNotifications] = useState<NotificationInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated()) { router.push("/login"); return; }
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    try {
      const data = await api.listNotifications() as { items: NotificationInfo[] };
      setNotifications(data.items);
    } catch { /* error */ }
    setLoading(false);
  };

  const markRead = async (id: number) => {
    await api.markNotificationRead(id);
    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
  };

  if (loading) return <div className="flex items-center justify-center min-h-screen">Loading…</div>;

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Notifications</h1>
          <button onClick={() => router.push("/dashboard")} className="text-sm text-gray-500 hover:text-gray-700">
            ← Dashboard
          </button>
        </div>

        <div className="space-y-3">
          {notifications.length === 0 ? (
            <p className="text-gray-500 text-center py-12">No notifications</p>
          ) : (
            notifications.map((n) => (
              <div
                key={n.id}
                className={`p-4 rounded-xl border transition-colors ${
                  n.is_read ? "bg-white border-gray-200" : "bg-blue-50 border-blue-200"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{n.subject}</p>
                    <p className="text-sm text-gray-600 mt-1">{n.body}</p>
                    <p className="text-xs text-gray-400 mt-2">{formatDate(n.sent_at)}</p>
                  </div>
                  {!n.is_read && (
                    <button
                      onClick={() => markRead(n.id)}
                      className="text-xs text-primary-600 hover:underline whitespace-nowrap"
                    >
                      Mark read
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
