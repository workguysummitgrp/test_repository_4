"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import { Upload } from "lucide-react";

const STEPS = [
  { label: "Personal Info", fields: ["full_name", "date_of_birth", "nationality", "phone"] },
  { label: "Business Info", fields: ["business_name", "business_type", "registration_number", "annual_revenue"] },
  { label: "Financial Info", fields: ["bank_name", "account_number", "credit_score_self_reported"] },
  { label: "Documents", fields: [] },
];

export default function ApplyPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [files, setFiles] = useState<File[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isAuthenticated()) { router.push("/login"); return; }
    loadDraft();
  }, []);

  const loadDraft = async () => {
    try {
      const draft = await api.getDraft() as { form_data: Record<string, string>; current_step: number } | null;
      if (draft) {
        setFormData(draft.form_data);
        setStep(draft.current_step - 1);
      }
    } catch { /* no draft */ }
  };

  const updateField = (key: string, value: string) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
  };

  const saveDraft = async () => {
    try {
      await api.saveDraft(formData, step + 1);
    } catch { /* best effort */ }
  };

  const handleNext = async () => {
    await saveDraft();
    setStep((s) => Math.min(s + 1, STEPS.length - 1));
  };

  const handleBack = () => setStep((s) => Math.max(s - 1, 0));

  const handleSubmit = async () => {
    setError("");
    setLoading(true);
    try {
      const app = await api.createApplication(formData) as { application_id: string };
      // Upload documents
      for (const file of files) {
        await api.uploadDocument(app.application_id, file);
      }
      await api.submitApplication(app.application_id);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Submission failed");
    } finally {
      setLoading(false);
    }
  };

  const currentStep = STEPS[step];

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Progress */}
        <div className="flex items-center gap-2 mb-8">
          {STEPS.map((s, i) => (
            <div key={i} className="flex-1">
              <div
                className={`h-2 rounded-full ${i <= step ? "bg-primary-600" : "bg-gray-200"}`}
              />
              <p className={`text-xs mt-1 ${i === step ? "text-primary-600 font-medium" : "text-gray-400"}`}>
                {s.label}
              </p>
            </div>
          ))}
        </div>

        <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm">
          <h2 className="text-xl font-bold text-gray-900 mb-6">{currentStep.label}</h2>

          {error && <div className="rounded-lg bg-error-50 p-3 text-sm text-error-500 mb-4">{error}</div>}

          {step < 3 ? (
            <div className="space-y-4">
              {currentStep.fields.map((field) => (
                <div key={field}>
                  <label className="block text-sm font-medium text-gray-700 mb-1 capitalize">
                    {field.replace(/_/g, " ")}
                  </label>
                  <input
                    type="text"
                    value={formData[field] || ""}
                    onChange={(e) => updateField(field, e.target.value)}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-gray-300 rounded-xl cursor-pointer hover:border-primary-400 transition-colors">
                <Upload className="w-8 h-8 text-gray-400 mb-2" />
                <span className="text-sm text-gray-500">Click to upload PDF, JPG, or PNG (max 10MB)</span>
                <input
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  multiple
                  className="hidden"
                  onChange={(e) => setFiles(Array.from(e.target.files || []))}
                />
              </label>
              {files.length > 0 && (
                <ul className="text-sm text-gray-600 space-y-1">
                  {files.map((f, i) => (
                    <li key={i} className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-green-500" />
                      {f.name} ({(f.size / 1024).toFixed(0)} KB)
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}

          <div className="flex justify-between mt-8">
            <button
              onClick={handleBack}
              disabled={step === 0}
              className="px-4 py-2 rounded-lg border border-gray-300 text-gray-700 disabled:opacity-30"
            >
              Back
            </button>
            {step < STEPS.length - 1 ? (
              <button
                onClick={handleNext}
                className="px-6 py-2 rounded-lg bg-primary-600 text-white font-medium hover:bg-primary-700"
              >
                Next
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="px-6 py-2 rounded-lg bg-primary-600 text-white font-medium hover:bg-primary-700 disabled:opacity-50"
              >
                {loading ? "Submitting…" : "Submit Application"}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
