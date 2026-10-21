import { describe, expect, it } from "vitest";
import {
  convertScheduledTime,
  getInstantFromWallClock,
  getTimeZoneMeta,
  isValidTimeZone,
  resolveLocationTimeZone,
} from "./timezone";

describe("Time-Zone Utility: Resolution & Conversion (WCAG & Precision)", () => {
  describe("resolveLocationTimeZone", () => {
    it("resolves domestic destinations within India to Asia/Kolkata", () => {
      expect(resolveLocationTimeZone("Delhi")).toEqual({
        timeZone: "Asia/Kolkata",
        locationName: "Delhi",
        isAmbiguous: false,
      });

      expect(resolveLocationTimeZone("Jaipur, India")).toEqual({
        timeZone: "Asia/Kolkata",
        locationName: "Jaipur",
        isAmbiguous: false,
      });

      expect(resolveLocationTimeZone("Bengaluru Airport Terminal")).toEqual({
        timeZone: "Asia/Kolkata",
        locationName: "Bengaluru Airport Terminal",
        isAmbiguous: false,
      });
    });

    it("resolves international destinations like Abu Dhabi and Tokyo accurately", () => {
      const abuDhabi = resolveLocationTimeZone("Abu Dhabi");
      expect(abuDhabi.timeZone).toBe("Asia/Dubai");
      expect(abuDhabi.isAmbiguous).toBe(false);

      const tokyo = resolveLocationTimeZone({ city: "Tokyo", country: "Japan" });
      expect(tokyo.timeZone).toBe("Asia/Tokyo");
      expect(tokyo.isAmbiguous).toBe(false);

      const london = resolveLocationTimeZone("London, United Kingdom");
      expect(london.timeZone).toBe("Europe/London");
      expect(london.isAmbiguous).toBe(false);
    });

    it("handles direct IANA timezone identifiers if provided", () => {
      const res = resolveLocationTimeZone("Asia/Dubai");
      expect(res.timeZone).toBe("Asia/Dubai");
      expect(res.isAmbiguous).toBe(false);
    });

    it("returns isAmbiguous=true for unknown or missing locations without guessing", () => {
      const unknown = resolveLocationTimeZone("Atlantis Unknown Realm");
      expect(unknown.timeZone).toBeNull();
      expect(unknown.isAmbiguous).toBe(true);

      const empty = resolveLocationTimeZone("");
      expect(empty.timeZone).toBeNull();
      expect(empty.isAmbiguous).toBe(true);
    });
  });

  describe("getTimeZoneMeta", () => {
    it("produces standard abbreviations and UTC offsets for Abu Dhabi (GST) and India (IST)", () => {
      const refDate = "2026-10-28";
      const uaeMeta = getTimeZoneMeta("Asia/Dubai", refDate, "Abu Dhabi");
      expect(uaeMeta.timeZone).toBe("Asia/Dubai");
      expect(uaeMeta.abbr).toBe("GST");
      expect(uaeMeta.utcOffset).toBe("UTC+04:00");
      expect(uaeMeta.labelWithAbbr).toBe("GST, UTC+04:00");
      expect(uaeMeta.locationName).toBe("Abu Dhabi");

      const indiaMeta = getTimeZoneMeta("Asia/Kolkata", refDate, "Delhi");
      expect(indiaMeta.timeZone).toBe("Asia/Kolkata");
      expect(indiaMeta.abbr).toBe("IST");
      expect(indiaMeta.utcOffset).toBe("UTC+05:30");
      expect(indiaMeta.labelWithAbbr).toBe("IST, UTC+05:30");
      expect(indiaMeta.locationName).toBe("Delhi");
    });

    it("provides safe fallback metadata when timezone is null or invalid", () => {
      const fallback = getTimeZoneMeta(null, new Date(), "Unknown Place");
      expect(fallback.isFallback).toBe(true);
      expect(fallback.labelWithAbbr).toBe("Local Time");
    });
  });

  describe("convertScheduledTime: Dual Time-Zone Scenarios", () => {
    it("Scenario 1: Domestic trip where origin and destination share a time zone (Delhi -> Jaipur)", () => {
      const converted = convertScheduledTime({
        dateStr: "2026-10-28",
        timeStr: "14:30",
        sourceTimeZone: "Asia/Kolkata",
        targetTimeZone: "Asia/Kolkata",
      });

      expect(converted.time).toBe("02:30 PM");
      expect(converted.period).toBe("Afternoon");
      expect(converted.dateShift).toBeNull();
      expect(converted.convertedDate).toBe("2026-10-28");
    });

    it("Scenario 2: India -> Abu Dhabi, showing both IST and Abu Dhabi local time", () => {
      // 09:30 AM local in Abu Dhabi
      const destView = convertScheduledTime({
        dateStr: "2026-10-28",
        timeStr: "09:30",
        sourceTimeZone: "Asia/Dubai",
        targetTimeZone: "Asia/Dubai",
      });
      expect(destView.time).toBe("09:30 AM");
      expect(destView.period).toBe("Morning");
      expect(destView.dateShift).toBeNull();

      // Switched to Origin Time (IST) -> Abu Dhabi (UTC+4) to India (UTC+5:30) is +1.5 hours -> 11:00 AM
      const originView = convertScheduledTime({
        dateStr: "2026-10-28",
        timeStr: "09:30",
        sourceTimeZone: "Asia/Dubai",
        targetTimeZone: "Asia/Kolkata",
      });
      expect(originView.time).toBe("11:00 AM");
      expect(originView.period).toBe("Morning");
      expect(originView.dateShift).toBeNull();
    });

    it("Scenario 3: Midnight crossing (+1 day forward and -1 day backward)", () => {
      // Late night Abu Dhabi 23:30 (11:30 PM) converted to India (IST) becomes 01:00 AM the next day (+1 day)
      const forwardCrossing = convertScheduledTime({
        dateStr: "2026-10-28",
        timeStr: "23:30",
        sourceTimeZone: "Asia/Dubai",
        targetTimeZone: "Asia/Kolkata",
      });
      expect(forwardCrossing.time).toBe("01:00 AM");
      expect(forwardCrossing.period).toBe("Morning");
      expect(forwardCrossing.convertedDate).toBe("2026-10-29");
      expect(forwardCrossing.dateShift).not.toBeNull();
      expect(forwardCrossing.dateShift.diffDays).toBe(1);
      expect(forwardCrossing.dateShift.label).toContain("+1 day");

      // Early morning Tokyo 02:00 AM converted to New York (America/New_York) becomes 01:00 PM previous day (-1 day)
      const backwardCrossing = convertScheduledTime({
        dateStr: "2026-10-28",
        timeStr: "02:00",
        sourceTimeZone: "Asia/Tokyo",
        targetTimeZone: "America/New_York",
      });
      expect(backwardCrossing.time).toBe("01:00 PM");
      expect(backwardCrossing.period).toBe("Afternoon");
      expect(backwardCrossing.convertedDate).toBe("2026-10-27");
      expect(backwardCrossing.dateShift).not.toBeNull();
      expect(backwardCrossing.dateShift.diffDays).toBe(-1);
      expect(backwardCrossing.dateShift.label).toContain("-1 day");
    });

    it("Scenario 4: Gracefully handles missing or ambiguous time zone information", () => {
      const result = convertScheduledTime({
        dateStr: "2026-10-28",
        timeStr: "10:15",
        sourceTimeZone: null,
        targetTimeZone: null,
      });

      expect(result.time).toBe("10:15 AM");
      expect(result.period).toBe("Morning");
      expect(result.dateShift).toBeNull();
    });

    it("Scenario 5: Repeated switching preserves the underlying scheduled instant", () => {
      const originalDate = "2026-10-28";
      const originalTime = "15:00";
      const instant = getInstantFromWallClock(originalDate, originalTime, "Asia/Dubai");

      // Convert to Origin (Kolkata)
      const toOrigin = convertScheduledTime({
        dateStr: originalDate,
        timeStr: originalTime,
        sourceTimeZone: "Asia/Dubai",
        targetTimeZone: "Asia/Kolkata",
      });
      expect(toOrigin.time).toBe("04:30 PM");

      // Convert back to Destination (Dubai)
      const backToDest = convertScheduledTime({
        dateStr: originalDate,
        timeStr: originalTime,
        sourceTimeZone: "Asia/Dubai",
        targetTimeZone: "Asia/Dubai",
      });
      expect(backToDest.time).toBe("03:00 PM");

      // Underlying instant remains identical
      const instantAgain = getInstantFromWallClock(originalDate, originalTime, "Asia/Dubai");
      expect(instant.toISOString()).toBe(instantAgain.toISOString());
    });
  });

  describe("isValidTimeZone", () => {
    it("validates real IANA time zones and rejects fake ones", () => {
      expect(isValidTimeZone("Asia/Kolkata")).toBe(true);
      expect(isValidTimeZone("Asia/Dubai")).toBe(true);
      expect(isValidTimeZone("Europe/London")).toBe(true);
      expect(isValidTimeZone("Fake/Timezone")).toBe(false);
      expect(isValidTimeZone(null)).toBe(false);
    });
  });
});
