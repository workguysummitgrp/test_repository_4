"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import type { ThresholdConfig, WorkflowConfig } from "@/types";

export default function AdminPage() {
  const router = useRouter();
  const [thresholds, setThresholds] = useState<ThresholdConfig[]>([]);
  const [workflows, setWorkflows] = useState<WorkflowConfig[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated()) { router.push("/login"); return; }
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [t, w] = await Promise.all([
        api.getThresholds() as Promise<ThresholdConfig[]>,
        api.getWorkflowConfigs() as Promise<WorkflowConfig[]>,
      ]);
      setThresholds(t);
      setWorkflows(w);
    } catch { /* error handling */ }
    setLoading(false);
  };

  const toggleNode = async (node: WorkflowConfig) => {
    await api.updateWorkflowConfig(node.node_name, !node.is_enabled);
    await loadData();
  };

  if (loading) return <div className="flex items-center justify-center min-h-screen">Loading…</div>;

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">Admin Configuration</h1>
          <button onClick={() => router.push("/dashboard")} className="text-sm text-gray-500 hover:text-gray-700">
            ← Dashboard
          </button>
        </div>

        {/* Thresholds */}
        <section className="bg-white rounded-2xl p-6 border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Decision Thresholds</h2>
          <div className="space-y-3">
            {thresholds.map((t) => (
              <div key={t.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="font-medium capitalize">{t.band_name.replace(/_/g, " ")}</span>
                <span className="text-sm text-gray-600">
                  {t.min_score} – {t.max_score}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* Workflow Nodes */}
        <section className="bg-white rounded-2xl p-6 border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Workflow Nodes</h2>
          <div className="space-y-3">
            {workflows.map((w) => (
              <div key={w.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="font-medium capitalize">{w.node_name.replace(/_/g, " ")}</span>
                <button
                  onClick={() => toggleNode(w)}
                  className={`px-3 py-1 rounded-full text-xs font-medium ${
                    w.is_enabled ? "bg-green-100 text-green-800" : "bg-gray-200 text-gray-600"
                  }`}
                >
                  {w.is_enabled ? "Enabled" : "Disabled"}
                </button>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
