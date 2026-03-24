"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { isAuthenticated, getRole } from "@/lib/auth";
import { scoreColor } from "@/lib/utils";
import type { ReviewerDecisionInfo, ApproverDecisionInfo, EvaluationInfo } from "@/types";

export default function ReviewPage() {
  const router = useRouter();
  const [role, setRole] = useState<string | null>(null);
  const [queue, setQueue] = useState<(ReviewerDecisionInfo | ApproverDecisionInfo)[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [evaluation, setEvaluation] = useState<EvaluationInfo | null>(null);
  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated()) { router.push("/login"); return; }
    setRole(getRole());
    loadQueue();
  }, []);

  const loadQueue = async () => {
    try {
      const data = role === "approver"
        ? await api.getApproverQueue()
        : await api.getReviewerQueue();
      setQueue(data as (ReviewerDecisionInfo | ApproverDecisionInfo)[]);
    } catch { /* empty */ }
    setLoading(false);
  };

  const loadEvaluation = async (applicationId: number) => {
    setSelectedId(applicationId);
    try {
      const ev = await api.getEvaluation(applicationId) as EvaluationInfo;
      setEvaluation(ev);
    } catch { setEvaluation(null); }
  };

  const handleDecision = async (decision: string) => {
    if (!selectedId) return;
    try {
      if (role === "approver") {
        await api.submitApproverDecision(selectedId, decision, comment);
      } else {
        await api.submitReviewerDecision(selectedId, decision, comment || undefined);
      }
      await loadQueue();
      setSelectedId(null);
      setEvaluation(null);
      setComment("");
    } catch { /* error handling */ }
  };

  if (loading) return <div className="flex items-center justify-center min-h-screen">Loading…</div>;

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-900">
            {role === "approver" ? "Approver" : "Reviewer"} Queue
          </h1>
          <button onClick={() => router.push("/dashboard")} className="text-sm text-gray-500 hover:text-gray-700">
            ← Dashboard
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Queue list */}
          <div className="space-y-3">
            {queue.length === 0 ? (
              <p className="text-gray-500 text-center py-12">No pending items</p>
            ) : (
              queue.map((item) => (
                <div
                  key={item.id}
                  className={`p-4 rounded-xl border cursor-pointer transition-colors ${
                    selectedId === item.application_id
                      ? "border-primary-400 bg-primary-50"
                      : "border-gray-200 bg-white hover:border-primary-200"
                  }`}
                  onClick={() => loadEvaluation(item.application_id)}
                >
                  <p className="font-medium text-gray-900">Application #{item.application_id}</p>
                  <p className="text-sm text-gray-500">Assigned {new Date(item.assigned_at).toLocaleDateString()}</p>
                </div>
              ))
            )}
          </div>

          {/* Detail panel */}
          {evaluation && (
            <div className="bg-white rounded-2xl p-6 border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-4">AI Evaluation</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Score</span>
                  <span className={`font-bold text-xl ${scoreColor(evaluation.score)}`}>
                    {evaluation.score}/100
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Confidence</span>
                  <span className="font-medium capitalize">{evaluation.confidence}</span>
                </div>
                <div>
                  <span className="text-gray-600 text-sm">Summary</span>
                  <p className="text-gray-800 mt-1">{evaluation.summary}</p>
                </div>
                {evaluation.flags.length > 0 && (
                  <div>
                    <span className="text-gray-600 text-sm">Flags</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {evaluation.flags.map((f, i) => (
                        <span key={i} className="px-2 py-0.5 bg-yellow-100 text-yellow-800 text-xs rounded">
                          {f}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <hr className="my-4" />

              <div className="space-y-3">
                <label className="block text-sm font-medium text-gray-700">Comment</label>
                <textarea
                  rows={3}
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder={role === "approver" ? "Comment required" : "Optional comment"}
                />
                <div className="flex gap-3">
                  <button
                    onClick={() => handleDecision("approved")}
                    disabled={role === "approver" && !comment.trim()}
                    className="flex-1 px-4 py-2 rounded-lg bg-green-600 text-white font-medium hover:bg-green-700 disabled:opacity-50"
                  >
                    Approve
                  </button>
                  <button
                    onClick={() => handleDecision("rejected")}
                    disabled={!comment.trim()}
                    className="flex-1 px-4 py-2 rounded-lg bg-red-600 text-white font-medium hover:bg-red-700 disabled:opacity-50"
                  >
                    Reject
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
