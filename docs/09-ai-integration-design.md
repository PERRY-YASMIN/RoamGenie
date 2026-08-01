# AI Integration Design

Input: trip facts plus allow-listed catalogue IDs/names/costs and optional weather. Output: `{summary, days[], budget_split[], warnings[], packing_items[]}` validated by Pydantic. The service chooses `mock` by default or a configured adapter, applies a short timeout and at most one transient retry, parses JSON, rejects unknown IDs/missing fields/negative costs, and falls back to deterministic mock output. It does not expose credentials, query/write PostgreSQL or treat provider text as trusted SQL/HTML.
