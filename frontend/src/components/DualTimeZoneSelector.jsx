import { useMemo, useState } from "react";
import { IconAlert, IconClock } from "./icons";
import {
  getTimeZoneMeta,
  resolveLocationTimeZone,
} from "../utils/timezone";

// Common time zones for fallback selection when location is ambiguous
const COMMON_FALLBACK_TIMEZONES = [
  { label: "India Standard Time (IST, UTC+05:30)", tz: "Asia/Kolkata" },
  { label: "Gulf Standard Time (GST, UTC+04:00)", tz: "Asia/Dubai" },
  { label: "Greenwich Mean Time (GMT, UTC+00:00)", tz: "Europe/London" },
  { label: "Central European Time (CET, UTC+01:00)", tz: "Europe/Paris" },
  { label: "Eastern Standard Time (EST, UTC-05:00)", tz: "America/New_York" },
  { label: "Central Standard Time (CST, UTC-06:00)", tz: "America/Chicago" },
  { label: "Pacific Standard Time (PST, UTC-08:00)", tz: "America/Los_Angeles" },
  { label: "Japan Standard Time (JST, UTC+09:00)", tz: "Asia/Tokyo" },
  { label: "Singapore Time (SGT, UTC+08:00)", tz: "Asia/Singapore" },
  { label: "Australian Eastern Time (AEST, UTC+10:00)", tz: "Australia/Sydney" },
];

export default function DualTimeZoneSelector({
  activeMode = "destination",
  onModeChange,
  origin = "Delhi",
  destination = "Abu Dhabi",
  referenceDate = new Date(),
  customOriginTz = null,
  onCustomOriginTzChange = null,
}) {
  const [showFallbackSelect, setShowFallbackSelect] = useState(false);

  // Resolve destination time zone
  const destTzMeta = useMemo(() => {
    const res = resolveLocationTimeZone(destination);
    const tz = res.timeZone || "Asia/Dubai";
    return getTimeZoneMeta(tz, referenceDate, res.locationName || (typeof destination === "string" ? destination : destination?.city || "Destination"));
  }, [destination, referenceDate]);

  // Resolve origin time zone (or use custom override if user picked one)
  const originResolution = useMemo(() => {
    if (customOriginTz) {
      return { timeZone: customOriginTz, locationName: origin || "Origin", isAmbiguous: false };
    }
    return resolveLocationTimeZone(origin);
  }, [origin, customOriginTz]);

  const originTzMeta = useMemo(() => {
    const tz = originResolution.timeZone;
    if (!tz) {
      return {
        timeZone: null,
        longName: "Unrecognized Time Zone",
        abbr: "",
        utcOffset: "Unknown",
        labelWithAbbr: "Time zone unverified",
        locationName: originResolution.locationName || origin || "Origin",
        isFallback: true,
      };
    }
    return getTimeZoneMeta(tz, referenceDate, originResolution.locationName || origin || "Origin");
  }, [originResolution, referenceDate, origin]);

  const isSameTimeZone = Boolean(
    destTzMeta.timeZone &&
    originTzMeta.timeZone &&
    (destTzMeta.timeZone === originTzMeta.timeZone || destTzMeta.utcOffset === originTzMeta.utcOffset)
  );

  function handleKeyDown(e) {
    if (e.key === "ArrowRight" || e.key === "ArrowDown") {
      e.preventDefault();
      onModeChange("origin");
    } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
      e.preventDefault();
      onModeChange("destination");
    }
  }

  function handleFallbackTzSelect(e) {
    const val = e.target.value;
    if (typeof onCustomOriginTzChange === "function") {
      onCustomOriginTzChange(val || null);
    }
    setShowFallbackSelect(false);
  }

  return (
    <div
      className="dual-tz-selector-container"
      role="region"
      aria-label="Itinerary time zone display options"
    >
      <div className="dual-tz-header-bar">
        <div className="dual-tz-title-wrap">
          <IconClock size={16} className="dual-tz-icon" aria-hidden="true" />
          <span className="dual-tz-heading">SCHEDULE TIME ZONE</span>
        </div>

        {isSameTimeZone ? (
          <span className="dual-tz-same-pill" title="Origin and Destination operate on the same time offset">
            Same Time Zone ({destTzMeta.abbr || destTzMeta.utcOffset})
          </span>
        ) : (
          <span className="dual-tz-status-indicator">
            Active: <strong>{activeMode === "origin" ? "Origin Time" : "Destination Time"}</strong>
          </span>
        )}
      </div>

      <div
        className="dual-tz-pills-group"
        role="radiogroup"
        aria-label="Select itinerary display time zone"
        onKeyDown={handleKeyDown}
      >
        {/* Destination Time Option */}
        <button
          type="button"
          role="radio"
          aria-checked={activeMode === "destination"}
          className={`dual-tz-pill ${activeMode === "destination" ? "active" : ""}`}
          onClick={() => onModeChange("destination")}
          aria-label={`Destination Time: ${destTzMeta.locationName}, ${destTzMeta.labelWithAbbr}`}
        >
          <div className="tz-pill-top">
            <span className="tz-pill-role">Destination Time</span>
            <span className="tz-pill-offset">{destTzMeta.labelWithAbbr}</span>
          </div>
          <div className="tz-pill-bottom">
            <strong className="tz-pill-location">{destTzMeta.locationName}</strong>
            {activeMode === "destination" && <span className="tz-active-dot" aria-hidden="true" />}
          </div>
        </button>

        {/* Origin Time Option */}
        <button
          type="button"
          role="radio"
          aria-checked={activeMode === "origin"}
          className={`dual-tz-pill ${activeMode === "origin" ? "active" : ""}`}
          onClick={() => onModeChange("origin")}
          aria-label={`Origin Time: ${originTzMeta.locationName}, ${originTzMeta.labelWithAbbr}`}
        >
          <div className="tz-pill-top">
            <span className="tz-pill-role">Origin Time</span>
            <span className={`tz-pill-offset ${originTzMeta.isFallback ? "offset-warning" : ""}`}>
              {originTzMeta.labelWithAbbr}
            </span>
          </div>
          <div className="tz-pill-bottom">
            <strong className="tz-pill-location">{originTzMeta.locationName}</strong>
            {activeMode === "origin" && <span className="tz-active-dot" aria-hidden="true" />}
          </div>
        </button>
      </div>

      {/* Fallback / Ambiguous Notice */}
      {originResolution.isAmbiguous && (
        <div className="dual-tz-ambiguous-notice" role="alert">
          <IconAlert size={14} className="tz-notice-icon" aria-hidden="true" />
          <div className="tz-notice-content">
            <p>
              Time zone for origin &quot;{originResolution.locationName}&quot; could not be detected automatically.
            </p>
            {!showFallbackSelect ? (
              <button
                type="button"
                className="tz-fallback-action-btn"
                onClick={() => setShowFallbackSelect(true)}
              >
                Choose origin standard time zone →
              </button>
            ) : (
              <div className="tz-fallback-selector-row">
                <label htmlFor="origin-fallback-tz" className="sr-only">
                  Select standard time zone for origin
                </label>
                <select
                  id="origin-fallback-tz"
                  className="tz-fallback-select"
                  onChange={handleFallbackTzSelect}
                  defaultValue=""
                >
                  <option value="" disabled>Choose time zone...</option>
                  {COMMON_FALLBACK_TIMEZONES.map((item) => (
                    <option key={item.tz} value={item.tz}>
                      {item.label}
                    </option>
                  ))}
                </select>
                <button
                  type="button"
                  className="tz-fallback-cancel-btn"
                  onClick={() => setShowFallbackSelect(false)}
                >
                  Cancel
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
