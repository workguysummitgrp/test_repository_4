import { describe, it, expect } from "vitest";
import type {
  Application,
  User,
  EvaluationInfo,
  ThresholdConfig,
  NotificationInfo,
  AuditLogEntry,
} from "@/types";

describe("TypeScript types", () => {
  it("Application type matches expected shape", () => {
    const app: Application = {
      id: 1,
      application_id: "APP-001",
      user_id: 1,
      status: "submitted",
      form_data: { name: "Test" },
      form_schema_version: "1.0",
      submitted_at: "2024-01-01T00:00:00Z",
      decision_at: null,
      final_decision: null,
      created_at: "2024-01-01T00:00:00Z",
      updated_at: "2024-01-01T00:00:00Z",
    };
    expect(app.status).toBe("submitted");
  });

  it("User type matches expected shape", () => {
    const user: User = {
      id: 1,
      email: "a@b.com",
      full_name: "Test",
      role: "customer",
      status: "active",
      created_at: "2024-01-01T00:00:00Z",
    };
    expect(user.role).toBe("customer");
  });

  it("EvaluationInfo includes all fields", () => {
    const ev: EvaluationInfo = {
      id: 1,
      application_id: 1,
      score: 85,
      confidence: "high",
      summary: "Good",
      flags: [],
      model_version: "gpt-4o",
      temperature: 0.1,
      retry_count: 0,
      is_valid: true,
      evaluated_at: "2024-01-01T00:00:00Z",
    };
    expect(ev.score).toBe(85);
  });

  it("ThresholdConfig type", () => {
    const t: ThresholdConfig = { id: 1, band_name: "auto_approve", min_score: 91, max_score: 100 };
    expect(t.min_score).toBe(91);
  });

  it("NotificationInfo type", () => {
    const n: NotificationInfo = {
      id: 1,
      user_id: 1,
      application_id: 1,
      channel: "both",
      event_type: "submission_confirmed",
      subject: "Submitted",
      body: "Your application has been submitted",
      is_read: false,
      sent_at: "2024-01-01T00:00:00Z",
      read_at: null,
    };
    expect(n.is_read).toBe(false);
  });

  it("AuditLogEntry type", () => {
    const a: AuditLogEntry = {
      id: 1,
      application_id: 1,
      actor_id: 2,
      actor_type: "admin",
      action: "config_updated",
      before_state: { threshold: 90 },
      after_state: { threshold: 85 },
      rationale: "Adjusted thresholds",
      created_at: "2024-01-01T00:00:00Z",
    };
    expect(a.action).toBe("config_updated");
  });
});
