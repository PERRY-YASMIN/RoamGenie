/**
 * RoamGenie Time-Zone Resolution & Dual-Time-Zone Converter Utility
 *
 * Provides IANA time-zone resolution for destinations and origins,
 * metadata extraction (abbreviations, UTC offsets), and timezone-aware
 * wall-clock to instant conversion using standard Intl.DateTimeFormat.
 */

// Comprehensive mapping of country names to standard canonical IANA time zones
export const COUNTRY_TIMEZONE_MAP = {
  // Asia
  india: "Asia/Kolkata",
  "united arab emirates": "Asia/Dubai",
  uae: "Asia/Dubai",
  japan: "Asia/Tokyo",
  singapore: "Asia/Singapore",
  thailand: "Asia/Bangkok",
  vietnam: "Asia/Ho_Chi_Minh",
  malaysia: "Asia/Kuala_Lumpur",
  indonesia: "Asia/Jakarta",
  "south korea": "Asia/Seoul",
  korea: "Asia/Seoul",
  china: "Asia/Shanghai",
  "hong kong": "Asia/Hong_Kong",
  taiwan: "Asia/Taipei",
  macau: "Asia/Macau",
  nepal: "Asia/Kathmandu",
  bhutan: "Asia/Thimphu",
  "sri lanka": "Asia/Colombo",
  maldives: "Indian/Maldives",
  philippines: "Asia/Manila",
  cambodia: "Asia/Phnom_Penh",
  laos: "Asia/Vientiane",
  myanmar: "Asia/Yangon",
  qatar: "Asia/Qatar",
  "saudi arabia": "Asia/Riyadh",
  oman: "Asia/Muscat",
  bahrain: "Asia/Bahrain",
  kuwait: "Asia/Kuwait",
  jordan: "Asia/Amman",

  // Europe
  "united kingdom": "Europe/London",
  uk: "Europe/London",
  england: "Europe/London",
  scotland: "Europe/London",
  wales: "Europe/London",
  france: "Europe/Paris",
  germany: "Europe/Berlin",
  italy: "Europe/Rome",
  spain: "Europe/Madrid",
  netherlands: "Europe/Amsterdam",
  switzerland: "Europe/Zurich",
  austria: "Europe/Vienna",
  belgium: "Europe/Brussels",
  portugal: "Europe/Lisbon",
  greece: "Europe/Athens",
  turkey: "Europe/Istanbul",
  ireland: "Europe/Dublin",
  sweden: "Europe/Stockholm",
  norway: "Europe/Oslo",
  denmark: "Europe/Copenhagen",
  finland: "Europe/Helsinki",
  iceland: "Atlantic/Reykjavik",
  "czech republic": "Europe/Prague",
  hungary: "Europe/Budapest",
  poland: "Europe/Warsaw",
  croatia: "Europe/Zagreb",
  bulgaria: "Europe/Sofia",
  romania: "Europe/Bucharest",
  serbia: "Europe/Belgrade",
  slovakia: "Europe/Bratislava",
  slovenia: "Europe/Ljubljana",
  estonia: "Europe/Tallinn",
  latvia: "Europe/Riga",
  lithuania: "Europe/Vilnius",

  // Americas
  "united states": "America/New_York",
  usa: "America/New_York",
  us: "America/New_York",
  canada: "America/Toronto",
  mexico: "America/Mexico_City",
  brazil: "America/Sao_Paulo",
  argentina: "America/Argentina/Buenos_Aires",
  chile: "America/Santiago",
  peru: "America/Lima",
  colombia: "America/Bogota",
  "costa rica": "America/Costa_Rica",
  cuba: "America/Havana",
  ecuador: "America/Guayaquil",
  bolivia: "America/La_Paz",
  panama: "America/Panama",
  "puerto rico": "America/Puerto_Rico",
  guatemala: "America/Guatemala",

  // Africa & Indian Ocean
  egypt: "Africa/Cairo",
  morocco: "Africa/Casablanca",
  "south africa": "Africa/Johannesburg",
  kenya: "Africa/Nairobi",
  tanzania: "Africa/Dar_es_Salaam",
  mauritius: "Indian/Mauritius",
  seychelles: "Indian/Mahe",
  madagascar: "Indian/Antananarivo",
  ethiopia: "Africa/Addis_Ababa",
  ghana: "Africa/Accra",
  senegal: "Africa/Dakar",
  rwanda: "Africa/Kigali",
  uganda: "Africa/Kampala",
  botswana: "Africa/Gaborone",
  namibia: "Africa/Windhoek",
  zambia: "Africa/Lusaka",
  zimbabwe: "Africa/Harare",

  // Oceania
  australia: "Australia/Sydney",
  "new zealand": "Pacific/Auckland",
  fiji: "Pacific/Fiji",
  "french polynesia": "Pacific/Tahiti",
};

// Specific city mappings (prioritized over country fallbacks for multi-timezone nations)
export const CITY_TIMEZONE_MAP = {
  // UAE
  "abu dhabi": "Asia/Dubai",
  dubai: "Asia/Dubai",
  sharjah: "Asia/Dubai",
  ajman: "Asia/Dubai",
  fujairah: "Asia/Dubai",
  "ras al khaimah": "Asia/Dubai",

  // India
  delhi: "Asia/Kolkata",
  "new delhi": "Asia/Kolkata",
  mumbai: "Asia/Kolkata",
  bengaluru: "Asia/Kolkata",
  bangalore: "Asia/Kolkata",
  kolkata: "Asia/Kolkata",
  calcutta: "Asia/Kolkata",
  chennai: "Asia/Kolkata",
  madras: "Asia/Kolkata",
  hyderabad: "Asia/Kolkata",
  jaipur: "Asia/Kolkata",
  agra: "Asia/Kolkata",
  varanasi: "Asia/Kolkata",
  amritsar: "Asia/Kolkata",
  rishikesh: "Asia/Kolkata",
  ahmedabad: "Asia/Kolkata",
  kochi: "Asia/Kolkata",
  cochin: "Asia/Kolkata",
  goa: "Asia/Kolkata",
  panaji: "Asia/Kolkata",
  pune: "Asia/Kolkata",
  mysuru: "Asia/Kolkata",
  mysore: "Asia/Kolkata",
  udaipur: "Asia/Kolkata",
  jodhpur: "Asia/Kolkata",
  trivandrum: "Asia/Kolkata",
  thiruvananthapuram: "Asia/Kolkata",
  shimla: "Asia/Kolkata",
  manali: "Asia/Kolkata",
  srinagar: "Asia/Kolkata",
  chandigarh: "Asia/Kolkata",
  guwahati: "Asia/Kolkata",

  // USA - Multi timezone
  "new york": "America/New_York",
  nyc: "America/New_York",
  boston: "America/New_York",
  miami: "America/New_York",
  orlando: "America/New_York",
  washington: "America/New_York",
  "washington dc": "America/New_York",
  philadelphia: "America/New_York",
  atlanta: "America/New_York",
  chicago: "America/Chicago",
  houston: "America/Chicago",
  dallas: "America/Chicago",
  austin: "America/Chicago",
  "new orleans": "America/Chicago",
  minneapolis: "America/Chicago",
  denver: "America/Denver",
  "salt lake city": "America/Denver",
  phoenix: "America/Phoenix",
  "los angeles": "America/Los_Angeles",
  la: "America/Los_Angeles",
  "san francisco": "America/Los_Angeles",
  sfo: "America/Los_Angeles",
  seattle: "America/Los_Angeles",
  "las vegas": "America/Los_Angeles",
  "san diego": "America/Los_Angeles",
  portland: "America/Los_Angeles",
  honolulu: "Pacific/Honolulu",
  anchorage: "America/Anchorage",

  // Canada - Multi timezone
  toronto: "America/Toronto",
  montreal: "America/Toronto",
  ottawa: "America/Toronto",
  "quebec city": "America/Toronto",
  vancouver: "America/Vancouver",
  victoria: "America/Vancouver",
  whistler: "America/Vancouver",
  calgary: "America/Edmonton",
  edmonton: "America/Edmonton",
  banff: "America/Edmonton",

  // Australia - Multi timezone
  sydney: "Australia/Sydney",
  melbourne: "Australia/Melbourne",
  brisbane: "Australia/Brisbane",
  cairns: "Australia/Brisbane",
  "gold coast": "Australia/Brisbane",
  perth: "Australia/Perth",
  adelaide: "Australia/Adelaide",
  darwin: "Australia/Darwin",
  hobart: "Australia/Hobart",

  // Indonesia
  bali: "Asia/Makassar",
  denpasar: "Asia/Makassar",
  ubud: "Asia/Makassar",
  kuta: "Asia/Makassar",
  seminyak: "Asia/Makassar",
  jakarta: "Asia/Jakarta",
  surabaya: "Asia/Jakarta",
  yogyakarta: "Asia/Jakarta",
  medan: "Asia/Jakarta",

  // Western Europe
  london: "Europe/London",
  manchester: "Europe/London",
  edinburgh: "Europe/London",
  paris: "Europe/Paris",
  nice: "Europe/Paris",
  lyon: "Europe/Paris",
  marseille: "Europe/Paris",
  bordeaux: "Europe/Paris",
  berlin: "Europe/Berlin",
  munich: "Europe/Berlin",
  frankfurt: "Europe/Berlin",
  rome: "Europe/Rome",
  milan: "Europe/Rome",
  florence: "Europe/Rome",
  venice: "Europe/Rome",
  naples: "Europe/Rome",
  madrid: "Europe/Madrid",
  barcelona: "Europe/Madrid",
  seville: "Europe/Madrid",
  valencia: "Europe/Madrid",
  amsterdam: "Europe/Amsterdam",
  rotterdam: "Europe/Amsterdam",
  brussels: "Europe/Brussels",
  bruges: "Europe/Brussels",
  zurich: "Europe/Zurich",
  geneva: "Europe/Zurich",
  vienna: "Europe/Vienna",
  salzburg: "Europe/Vienna",
  lisbon: "Europe/Lisbon",
  porto: "Europe/Lisbon",
  athens: "Europe/Athens",
  santorini: "Europe/Athens",
  mykonos: "Europe/Athens",
  dublin: "Europe/Dublin",

  // East Asia
  tokyo: "Asia/Tokyo",
  kyoto: "Asia/Tokyo",
  osaka: "Asia/Tokyo",
  sapporo: "Asia/Tokyo",
  hiroshima: "Asia/Tokyo",
  nara: "Asia/Tokyo",
  fukuoka: "Asia/Tokyo",
  seoul: "Asia/Seoul",
  busan: "Asia/Seoul",
  jeju: "Asia/Seoul",
  "jeju city": "Asia/Seoul",
  beijing: "Asia/Shanghai",
  shanghai: "Asia/Shanghai",
  guangzhou: "Asia/Shanghai",
  shenzhen: "Asia/Shanghai",
  chengdu: "Asia/Shanghai",
  "hong kong": "Asia/Hong_Kong",
  taipei: "Asia/Taipei",

  // Southeast Asia
  bangkok: "Asia/Bangkok",
  phuket: "Asia/Bangkok",
  "chiang mai": "Asia/Bangkok",
  pattaya: "Asia/Bangkok",
  krabi: "Asia/Bangkok",
  "ho chi minh": "Asia/Ho_Chi_Minh",
  "ho chi minh city": "Asia/Ho_Chi_Minh",
  hanoi: "Asia/Ho_Chi_Minh",
  "da nang": "Asia/Ho_Chi_Minh",
  "hoi an": "Asia/Ho_Chi_Minh",
  singapore: "Asia/Singapore",
  "kuala lumpur": "Asia/Kuala_Lumpur",
  penang: "Asia/Kuala_Lumpur",
  langkawi: "Asia/Kuala_Lumpur",
  manila: "Asia/Manila",
  cebu: "Asia/Manila",
  boracay: "Asia/Manila",
  "siem reap": "Asia/Phnom_Penh",
  "phnom penh": "Asia/Phnom_Penh",

  // Middle East & Africa
  doha: "Asia/Qatar",
  riyadh: "Asia/Riyadh",
  jeddah: "Asia/Riyadh",
  muscat: "Asia/Muscat",
  manama: "Asia/Bahrain",
  "kuwait city": "Asia/Kuwait",
  amman: "Asia/Amman",
  petra: "Asia/Amman",
  cairo: "Africa/Cairo",
  luxor: "Africa/Cairo",
  aswan: "Africa/Cairo",
  alexandria: "Africa/Cairo",
  marrakech: "Africa/Casablanca",
  casablanca: "Africa/Casablanca",
  fes: "Africa/Casablanca",
  "cape town": "Africa/Johannesburg",
  johannesburg: "Africa/Johannesburg",
  durban: "Africa/Johannesburg",
  nairobi: "Africa/Nairobi",
  mombasa: "Africa/Nairobi",
  zanzibar: "Africa/Dar_es_Salaam",
  "dar es salaam": "Africa/Dar_es_Salaam",
  istanbul: "Europe/Istanbul",
  antalya: "Europe/Istanbul",
  cappadocia: "Europe/Istanbul",
  goreme: "Europe/Istanbul",
};

// Common recognizable abbreviation overrides for cleaner travel display
export const TIMEZONE_ABBR_MAP = {
  "Asia/Dubai": "GST",
  "Asia/Kolkata": "IST",
  "Asia/Calcutta": "IST",
  "Asia/Tokyo": "JST",
  "Asia/Singapore": "SGT",
  "Asia/Bangkok": "ICT",
  "Asia/Jakarta": "WIB",
  "Asia/Makassar": "WITA",
  "Asia/Seoul": "KST",
  "Asia/Hong_Kong": "HKT",
  "Asia/Shanghai": "CST",
  "Asia/Qatar": "AST",
  "Asia/Riyadh": "AST",
  "Europe/London": "GMT",
  "Europe/Paris": "CET",
  "Europe/Berlin": "CET",
  "Europe/Rome": "CET",
  "Europe/Madrid": "CET",
  "Europe/Amsterdam": "CET",
  "Europe/Athens": "EET",
  "Europe/Istanbul": "TRT",
  "America/New_York": "EST",
  "America/Chicago": "CST",
  "America/Denver": "MST",
  "America/Phoenix": "MST",
  "America/Los_Angeles": "PST",
  "America/Toronto": "EST",
  "America/Vancouver": "PST",
  "Australia/Sydney": "AEST",
  "Australia/Melbourne": "AEST",
  "Australia/Perth": "AWST",
  "Pacific/Auckland": "NZST",
};

/**
 * Clean and normalize a location string
 */
function cleanLocationString(str) {
  if (!str) return "";
  return str
    .toLowerCase()
    .replace(/\b(airport|terminal|station|central|intl|international)\b/gi, "")
    .replace(/[(),]/g, " ")
    .trim()
    .replace(/\s+/g, " ");
}

/**
 * Verify whether an IANA time-zone string is supported by the runtime
 */
export function isValidTimeZone(tz) {
  if (!tz || typeof tz !== "string") return false;
  try {
    Intl.DateTimeFormat(undefined, { timeZone: tz });
    return true;
  } catch {
    return false;
  }
}

/**
 * Resolves a destination or origin location string or object to an IANA time zone
 *
 * @param {string|object} location - Location string (e.g. "Abu Dhabi", "Delhi", "Paris, France") or object { city, country }
 * @param {string} fallbackCountry - Optional country hint
 * @returns {object} { timeZone: string|null, locationName: string, isAmbiguous: boolean }
 */
export function resolveLocationTimeZone(location, fallbackCountry = "") {
  if (!location) {
    return {
      timeZone: null,
      locationName: "Unknown",
      isAmbiguous: true,
    };
  }

  // If already an object with city & country
  if (typeof location === "object") {
    const city = location.city || "";
    const country = location.country || fallbackCountry || "";
    const locationName = city ? (country ? `${city}, ${country}` : city) : country || "Unknown";

    // 1. Check city
    const cleanCity = cleanLocationString(city);
    if (cleanCity && CITY_TIMEZONE_MAP[cleanCity]) {
      return {
        timeZone: CITY_TIMEZONE_MAP[cleanCity],
        locationName: city || locationName,
        isAmbiguous: false,
      };
    }

    // 2. Check country
    const cleanCountry = cleanLocationString(country);
    if (cleanCountry && COUNTRY_TIMEZONE_MAP[cleanCountry]) {
      return {
        timeZone: COUNTRY_TIMEZONE_MAP[cleanCountry],
        locationName: city || country || locationName,
        isAmbiguous: false,
      };
    }

    return {
      timeZone: null,
      locationName,
      isAmbiguous: true,
    };
  }

  // Location is a string
  const rawStr = String(location).trim();

  // If user or API directly supplied an IANA time zone name (e.g. "Asia/Dubai")
  if (rawStr.includes("/") && isValidTimeZone(rawStr)) {
    return {
      timeZone: rawStr,
      locationName: rawStr.split("/").pop().replace(/_/g, " "),
      isAmbiguous: false,
    };
  }

  // Parse "City, Country"
  const parts = rawStr.split(",").map((s) => s.trim());
  const cityPart = cleanLocationString(parts[0]);
  const countryPart = parts.length > 1 ? cleanLocationString(parts[1]) : cleanLocationString(fallbackCountry);

  // 1. Direct city lookup
  if (cityPart && CITY_TIMEZONE_MAP[cityPart]) {
    return {
      timeZone: CITY_TIMEZONE_MAP[cityPart],
      locationName: parts[0],
      isAmbiguous: false,
    };
  }

  // 2. Multi-word city partial check (e.g. "Delhi Airport Terminal" -> "delhi")
  for (const [knownCity, tz] of Object.entries(CITY_TIMEZONE_MAP)) {
    if (cityPart === knownCity || cityPart.startsWith(knownCity + " ") || cityPart.endsWith(" " + knownCity)) {
      return {
        timeZone: tz,
        locationName: parts[0],
        isAmbiguous: false,
      };
    }
  }

  // 3. Country lookup
  if (countryPart && COUNTRY_TIMEZONE_MAP[countryPart]) {
    return {
      timeZone: COUNTRY_TIMEZONE_MAP[countryPart],
      locationName: parts[0],
      isAmbiguous: false,
    };
  }

  // 4. Try matching the whole string against countries
  const wholeClean = cleanLocationString(rawStr);
  if (COUNTRY_TIMEZONE_MAP[wholeClean]) {
    return {
      timeZone: COUNTRY_TIMEZONE_MAP[wholeClean],
      locationName: rawStr,
      isAmbiguous: false,
    };
  }

  // 5. Unrecognized / Ambiguous
  return {
    timeZone: null,
    locationName: rawStr,
    isAmbiguous: true,
  };
}

/**
 * Extracts comprehensive time zone metadata (long name, abbreviation, standard UTC offset)
 *
 * @param {string} timeZone - IANA time-zone name
 * @param {Date|string} referenceDate - Reference date to determine daylight saving vs standard time
 * @param {string} locationName - Optional display location name
 * @returns {object} metadata
 */
export function getTimeZoneMeta(timeZone, referenceDate = new Date(), locationName = "") {
  if (!timeZone || !isValidTimeZone(timeZone)) {
    return {
      timeZone: null,
      longName: "Unspecified Time Zone",
      abbr: "",
      utcOffset: "UTC+00:00",
      labelWithAbbr: "Local Time",
      locationName: locationName || "Local",
      isFallback: true,
    };
  }

  const date = typeof referenceDate === "string" ? new Date(referenceDate) : referenceDate;
  const validDate = isNaN(date.getTime()) ? new Date() : date;

  const longFormatter = new Intl.DateTimeFormat("en-US", { timeZone, timeZoneName: "long" });
  const shortFormatter = new Intl.DateTimeFormat("en-US", { timeZone, timeZoneName: "short" });
  const offsetFormatter = new Intl.DateTimeFormat("en-US", { timeZone, timeZoneName: "shortOffset" });

  const longParts = longFormatter.formatToParts(validDate);
  const shortParts = shortFormatter.formatToParts(validDate);
  const offsetParts = offsetFormatter.formatToParts(validDate);

  const longName = longParts.find((p) => p.type === "timeZoneName")?.value || timeZone;
  const shortName = shortParts.find((p) => p.type === "timeZoneName")?.value || "";
  const gmtOffset = offsetParts.find((p) => p.type === "timeZoneName")?.value || "GMT";

  // Normalize GMT+X / GMT-X to standard UTC+HH:MM
  let utcOffset = "UTC+00:00";
  const match = gmtOffset.match(/GMT([+-])(\d+)(?::(\d+))?/);
  if (match) {
    const sign = match[1];
    const hours = match[2].padStart(2, "0");
    const mins = (match[3] || "00").padStart(2, "0");
    utcOffset = `UTC${sign}${hours}:${mins}`;
  } else if (gmtOffset === "GMT") {
    utcOffset = "UTC+00:00";
  }

  const abbr = TIMEZONE_ABBR_MAP[timeZone] || (shortName.startsWith("GMT") ? "" : shortName);
  const labelWithAbbr = abbr ? `${abbr}, ${utcOffset}` : utcOffset;

  return {
    timeZone,
    longName,
    abbr,
    utcOffset,
    labelWithAbbr,
    locationName: locationName || timeZone.split("/").pop().replace(/_/g, " "),
    isFallback: false,
  };
}

/**
 * Calculates the exact absolute UTC instant (Date object) for a scheduled local wall-clock date & time in an IANA time zone.
 *
 * @param {string} dateStr - Date string 'YYYY-MM-DD'
 * @param {string} timeStr - Time string 'HH:MM' or 'HH:MM:SS'
 * @param {string} timeZone - IANA time zone of the schedule
 * @returns {Date} The exact unambiguous Date instant
 */
export function getInstantFromWallClock(dateStr, timeStr, timeZone) {
  const safeDate = dateStr && /^\d{4}-\d{2}-\d{2}$/.test(dateStr) ? dateStr : "2026-01-01";
  const [year, month, day] = safeDate.split("-").map(Number);

  const timeParts = (timeStr || "09:00").split(":");
  const hour = parseInt(timeParts[0], 10) || 0;
  const minute = parseInt(timeParts[1], 10) || 0;
  const second = parseInt(timeParts[2], 10) || 0;

  const utcGuess = new Date(Date.UTC(year, month - 1, day, hour, minute, second));

  if (!timeZone || !isValidTimeZone(timeZone)) {
    return utcGuess;
  }

  const formatter = new Intl.DateTimeFormat("en-US", {
    timeZone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });

  const parts = formatter.formatToParts(utcGuess);
  const getPart = (type) => Number(parts.find((p) => p.type === type)?.value);

  const y = getPart("year");
  const m = getPart("month");
  const d = getPart("day");
  let h = getPart("hour");
  if (h === 24) h = 0;
  const min = getPart("minute");
  const sec = getPart("second");

  const wallClockAsUtc = Date.UTC(y, m - 1, d, h, min, sec);
  const offsetMs = wallClockAsUtc - utcGuess.getTime();

  return new Date(utcGuess.getTime() - offsetMs);
}

/**
 * Converts a scheduled date & time from a source time zone to a target time zone.
 * Accurately detects midnight crossing (+1 day / -1 day) and recalculates the period (Morning, Afternoon, Evening).
 *
 * @param {object} params
 * @param {string} params.dateStr - 'YYYY-MM-DD'
 * @param {string} params.timeStr - 'HH:MM' or 'HH:MM:SS'
 * @param {string} params.sourceTimeZone - Source IANA time zone (e.g. destination's time zone)
 * @param {string} params.targetTimeZone - Target IANA time zone (e.g. origin's time zone)
 * @returns {object} { time, period, dateShift, convertedDate }
 */
export function convertScheduledTime({
  dateStr,
  timeStr,
  sourceTimeZone,
  targetTimeZone,
}) {
  if (!timeStr) {
    return {
      time: "--:--",
      period: "Daytime",
      dateShift: null,
      convertedDate: dateStr,
    };
  }

  // If source and target time zones are identical or either is missing
  if (!sourceTimeZone || !targetTimeZone || sourceTimeZone === targetTimeZone) {
    const [hStr, mStr = "00"] = timeStr.split(":");
    const h = parseInt(hStr, 10);
    const m = mStr.substring(0, 2);
    const ampm = h >= 12 ? "PM" : "AM";
    const displayHour = h % 12 === 0 ? 12 : h % 12;
    const formatted = `${displayHour < 10 ? "0" : ""}${displayHour}:${m} ${ampm}`;
    const period = h < 12 ? "Morning" : h < 17 ? "Afternoon" : "Evening";

    return {
      time: formatted,
      period,
      dateShift: null,
      convertedDate: dateStr,
    };
  }

  const instant = getInstantFromWallClock(dateStr, timeStr, sourceTimeZone);

  const timeFormatter = new Intl.DateTimeFormat("en-US", {
    timeZone: targetTimeZone,
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  });

  const hourFormatter = new Intl.DateTimeFormat("en-US", {
    timeZone: targetTimeZone,
    hour: "numeric",
    hour12: false,
  });

  const dateFormatter = new Intl.DateTimeFormat("en-CA", {
    timeZone: targetTimeZone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });

  const shortDateFormatter = new Intl.DateTimeFormat("en-US", {
    timeZone: targetTimeZone,
    month: "short",
    day: "numeric",
  });

  const convertedTime = timeFormatter.format(instant);
  const convertedHour = parseInt(hourFormatter.format(instant), 10);
  const convertedDateStr = dateFormatter.format(instant);
  const formattedShortDate = shortDateFormatter.format(instant);

  let dateShift = null;
  if (dateStr && convertedDateStr !== dateStr) {
    const origD = new Date(dateStr + "T00:00:00Z");
    const convD = new Date(convertedDateStr + "T00:00:00Z");
    const diffDays = Math.round((convD - origD) / (1000 * 60 * 60 * 24));
    dateShift = {
      diffDays,
      label: diffDays > 0 ? `+${diffDays} day (${formattedShortDate})` : `${diffDays} day (${formattedShortDate})`,
      shortDate: formattedShortDate,
    };
  }

  const period = convertedHour < 12 ? "Morning" : convertedHour < 17 ? "Afternoon" : "Evening";

  return {
    time: convertedTime,
    period,
    dateShift,
    convertedDate: convertedDateStr,
  };
}
