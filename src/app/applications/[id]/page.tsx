"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import { formatDate, statusColor } from "@/lib/utils";
import { ArrowLeft } from "lucide-react";
import type { Application } from "@/types";

export default function ApplicationDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [application, setApplication] = useState<Application | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated()) { router.push("/login"); return; }
    const id = params.id as string;
    if (id) loadApplication(id);
  }, [params.id]);

  const loadApplication = async (id: string) => {
    try {
      const app = await api.getApplication(id) as Application;
      setApplication(app);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load application");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin h-8 w-8 border-4 border-primary-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (error || !application) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 gap-4">
        <p className="text-red-600">{error || "Application not found"}</p>
        <button onClick={() => router.push("/dashboard")} className="text-primary-600 hover:underline">
          Back to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <button onClick={() => router.push("/dashboard")} className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
          <ArrowLeft size={16} /> Back to Dashboard
        </button>
      </header>
      <main className="max-w-3xl mx-auto p-6 space-y-6">
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold text-gray-900">Application {application.application_id}</h1>
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColor(application.status)}`}>
              {application.status.replace(/_/g, " ")}
            </span>
          </div>
          <dl className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <dt className="text-gray-500">Submitted</dt>
              <dd className="font-medium">{application.submitted_at ? formatDate(application.submitted_at) : "Not submitted"}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Decision</dt>
              <dd className="font-medium">{application.final_decision || "Pending"}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Created</dt>
              <dd className="font-medium">{formatDate(application.created_at)}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Updated</dt>
              <dd className="font-medium">{formatDate(application.updated_at)}</dd>
            </div>
          </dl>
        </div>
        {application.form_data && Object.keys(application.form_data).length > 0 && (
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-lg font-semibold mb-3">Form Data</h2>
            <pre className="text-sm bg-gray-50 rounded-lg p-4 overflow-auto max-h-96">
              {JSON.stringify(application.form_data, null, 2)}
            </pre>
          </div>
        )}
      </main>
    </div>
  );
}
