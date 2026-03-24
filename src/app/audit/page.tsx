"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import { formatDate } from "@/lib/utils";
import type { AuditLogEntry } from "@/types";

export default function AuditPage() {
  const router = useRouter();
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);

  useEffect(() => {
    if (!isAuthenticated()) { router.push("/login"); return; }
    loadLogs();
  }, [page]);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await api.getAuditLogs(undefined, page, 30) as { items: AuditLogEntry[]; total: number };
      setLogs(data.items);
    } catch { /* error */ }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Audit Log</h1>
          <button onClick={() => router.push("/dashboard")} className="text-sm text-gray-500 hover:text-gray-700">
            ← Dashboard
          </button>
        </div>

        <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="p-3 text-left font-medium text-gray-600">Timestamp</th>
                <th className="p-3 text-left font-medium text-gray-600">Action</th>
                <th className="p-3 text-left font-medium text-gray-600">Actor</th>
                <th className="p-3 text-left font-medium text-gray-600">Application</th>
                <th className="p-3 text-left font-medium text-gray-600">Rationale</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={5} className="p-8 text-center text-gray-400">Loading…</td></tr>
              ) : logs.length === 0 ? (
                <tr><td colSpan={5} className="p-8 text-center text-gray-400">No audit entries</td></tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="p-3 text-gray-600">{formatDate(log.created_at)}</td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 bg-blue-100 text-blue-800 text-xs rounded font-medium">
                        {log.action}
                      </span>
                    </td>
                    <td className="p-3 text-gray-700 capitalize">{log.actor_type} #{log.actor_id}</td>
                    <td className="p-3 text-gray-700">{log.application_id ?? "—"}</td>
                    <td className="p-3 text-gray-600 max-w-xs truncate">{log.rationale ?? "—"}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="flex justify-center gap-4 mt-6">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-30"
          >
            Previous
          </button>
          <span className="px-4 py-2 text-gray-600">Page {page}</span>
          <button
            onClick={() => setPage((p) => p + 1)}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
