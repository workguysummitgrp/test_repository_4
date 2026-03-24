import { describe, it, expect } from "vitest";
import { cn, formatDate, statusColor, scoreColor } from "@/lib/utils";

describe("cn", () => {
  it("merges class names", () => {
    expect(cn("px-4", "py-2")).toBe("px-4 py-2");
  });

  it("handles conditional classes", () => {
    expect(cn("base", false && "hidden", "visible")).toBe("base visible");
  });

  it("deduplicates tailwind classes", () => {
    expect(cn("px-2", "px-4")).toBe("px-4");
  });
});

describe("formatDate", () => {
  it("formats ISO string", () => {
    const result = formatDate("2024-06-15T10:30:00Z");
    expect(result).toContain("2024");
  });

  it("returns dash for null", () => {
    expect(formatDate(null)).toBe("—");
  });
});

describe("statusColor", () => {
  it("returns green for approved", () => {
    expect(statusColor("approved")).toContain("green");
  });

  it("returns red for rejected", () => {
    expect(statusColor("rejected")).toContain("red");
  });

  it("returns blue for submitted", () => {
    expect(statusColor("submitted")).toContain("blue");
  });

  it("returns gray for unknown", () => {
    expect(statusColor("unknown")).toContain("gray");
  });
});

describe("scoreColor", () => {
  it("green for 90+", () => {
    expect(scoreColor(95)).toContain("green");
  });

  it("blue for 80-89", () => {
    expect(scoreColor(85)).toContain("blue");
  });

  it("yellow for 70-79", () => {
    expect(scoreColor(75)).toContain("yellow");
  });

  it("red for below 70", () => {
    expect(scoreColor(50)).toContain("red");
  });
});
