import { useEffect, useMemo, useState } from "react";
import { useToast } from "../context/ToastContext";
import { executeCustomSQL, executeReportQuery, getAuditLogs, getReportQueries } from "../services/api";
import { IconDatabase, IconCode, IconShield, IconCopy, IconCheck, IconRefresh } from "../components/icons";

export default function ShowcasePage() {
  const { error: toastError, success } = useToast();
  const [activeTab, setActiveTab] = useState("predefined"); // predefined | custom | audit
  const [queries, setQueries] = useState([]);
  const [selectedQueryId, setSelectedQueryId] = useState("Q01");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [queryResult, setQueryResult] = useState(null);
  const [executing, setExecuting] = useState(false);
  const [execError, setExecError] = useState(null);
  const [copiedSql, setCopiedSql] = useState(false);

  // Custom SQL Editor state
  const [customSQL, setCustomSQL] = useState(
    "SELECT d.city, COUNT(h.id) AS hotel_count, ROUND(AVG(h.price_per_night), 2) AS avg_price FROM destinations d LEFT JOIN hotels h ON h.destination_id = d.id GROUP BY d.city ORDER BY avg_price DESC LIMIT 10;"
  );

  // Audit logs state
  const [auditLogs, setAuditLogs] = useState([]);
  const [auditLoading, setAuditLoading] = useState(false);

  useEffect(() => {
    async function loadQueries() {
      try {
        const list = await getReportQueries();
        setQueries(list);
        if (list.length > 0) {
          setSelectedQueryId(list[0].id);
          runPredefinedQuery(list[0].id);
        }
      } catch (err) {
        console.error("Failed to load DBMS queries", err);
        toastError(err.message || "Failed to load benchmark queries.");
      }
    }
    loadQueries();
  }, []);

  async function runPredefinedQuery(qid) {
    setExecuting(true);
    setExecError(null);
    try {
      const res = await executeReportQuery(qid);
      setQueryResult(res);
    } catch (err) {
      setExecError(err.message);
      setQueryResult(null);
      toastError(err.message || `Failed to execute ${qid}.`);
    } finally {
      setExecuting(false);
    }
  }

  async function handleCustomSQLExecute(e) {
    e.preventDefault();
    setExecuting(true);
    setExecError(null);
    try {
      const res = await executeCustomSQL(customSQL);
      setQueryResult(res);
      success(`Query executed: ${res.row_count} rows returned in ${res.execution_time_ms} ms.`);
    } catch (err) {
      setExecError(err.message);
      setQueryResult(null);
      toastError(err.message || "Failed to execute custom SQL query.");
    } finally {
      setExecuting(false);
    }
  }

  async function loadAuditTriggerLogs() {
    setAuditLoading(true);
    try {
      const logs = await getAuditLogs(50);
      setAuditLogs(logs);
    } catch (err) {
      console.error(err);
      toastError(err.message || "Failed to load audit logs.");
    } finally {
      setAuditLoading(false);
    }
  }

  useEffect(() => {
    if (activeTab === "audit") {
      loadAuditTriggerLogs();
    }
  }, [activeTab]);

  const categories = useMemo(() => {
    const set = new Set();
    queries.forEach((q) => {
      if (q.category) set.add(q.category);
    });
    return ["All", ...Array.from(set)];
  }, [queries]);

  const filteredQueries = useMemo(() => {
    if (selectedCategory === "All") return queries;
    return queries.filter((q) => q.category === selectedCategory);
  }, [queries, selectedCategory]);

  const currentQueryMeta = queries.find((q) => q.id === selectedQueryId);

  const handleCopySQL = () => {
    if (!currentQueryMeta?.sql) return;
    navigator.clipboard.writeText(currentQueryMeta.sql).then(() => {
      setCopiedSql(true);
      setTimeout(() => setCopiedSql(false), 2000);
    });
  };

  return (
    <div className="showcase-editorial-page">
      {/* Editorial Header */}
      <header className="editorial-page-header">
        <p className="editorial-eyebrow">DATABASE INTELLIGENCE</p>
        <h1 className="editorial-page-title">Relational Engine & SQL Playground</h1>
        <p className="editorial-page-subtitle">
          Explore 18 optimized PostgreSQL queries, triggers, stored procedures, and audit logs powering RoamGenie’s travel & budget engine.
        </p>

        {/* Primary Tabs */}
        <div className="showcase-editorial-tabs" role="tablist" aria-label="DBMS showcase sections">
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === "predefined"}
            className={`showcase-nav-btn ${activeTab === "predefined" ? "active" : ""}`}
            onClick={() => setActiveTab("predefined")}
          >
            <IconDatabase size={15} /> Benchmark Queries (18)
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === "custom"}
            className={`showcase-nav-btn ${activeTab === "custom" ? "active" : ""}`}
            onClick={() => setActiveTab("custom")}
          >
            <IconCode size={15} /> Custom SQL Console
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === "audit"}
            className={`showcase-nav-btn ${activeTab === "audit" ? "active" : ""}`}
            onClick={() => setActiveTab("audit")}
          >
            <IconShield size={15} /> Audit Trigger History
          </button>
        </div>
      </header>

      {/* Tab 1: 18 Predefined Benchmark Queries */}
      {activeTab === "predefined" && (
        <div className="showcase-split-layout">
          {/* Left Column: Clean List of Queries */}
          <aside className="query-index-column" aria-label="Benchmark Query Selector">
            <div className="query-index-header">
              <span className="query-index-title">INDEX</span>
              <span className="query-count-tag">{filteredQueries.length} of {queries.length}</span>
            </div>

            {/* Category Filter Links */}
            <div className="query-category-filter-row" role="toolbar" aria-label="Filter queries by category">
              {categories.map((cat) => (
                <button
                  key={cat}
                  type="button"
                  className={`query-filter-chip ${selectedCategory === cat ? "active" : ""}`}
                  onClick={() => setSelectedCategory(cat)}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* Queries List */}
            <div className="query-index-stream" role="tablist" aria-orientation="vertical">
              {filteredQueries.map((q) => {
                const isActive = selectedQueryId === q.id;
                return (
                  <button
                    key={q.id}
                    type="button"
                    role="tab"
                    aria-selected={isActive}
                    className={`query-index-row ${isActive ? "active" : ""}`}
                    onClick={() => {
                      setSelectedQueryId(q.id);
                      runPredefinedQuery(q.id);
                    }}
                    aria-label={`Select query ${q.id}: ${q.title}`}
                  >
                    <span className="query-index-id">{q.id}</span>
                    <div className="query-index-text">
                      <span className="query-row-title">{q.title}</span>
                      <span className="query-row-category">{q.category}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </aside>

          {/* Right Column: Query Detail, Code & Live Results */}
          <main className="query-workspace-column" aria-label="Query Execution Output">
            {currentQueryMeta && (
              <div className="query-meta-editorial">
                <div className="query-headline-row">
                  <div>
                    <span className="query-category-pill">{currentQueryMeta.category}</span>
                    <h2 className="query-title-text">
                      <span className="query-hero-id">{currentQueryMeta.id} ·</span> {currentQueryMeta.title}
                    </h2>
                  </div>
                  <span className="postgres-version-tag">PostgreSQL 15+</span>
                </div>

                <p className="query-explanation">{currentQueryMeta.description}</p>

                {/* SQL Code Block */}
                <div className="editorial-sql-block">
                  <div className="sql-block-header">
                    <span className="sql-header-label">SQL STATEMENT</span>
                    <button
                      type="button"
                      className="sql-copy-btn"
                      onClick={handleCopySQL}
                      title="Copy SQL statement to clipboard"
                    >
                      {copiedSql ? (
                        <>
                          <IconCheck size={12} /> Copied
                        </>
                      ) : (
                        <>
                          <IconCopy size={12} /> Copy SQL
                        </>
                      )}
                    </button>
                  </div>
                  <pre className="sql-code-pre">
                    <code>{currentQueryMeta.sql}</code>
                  </pre>
                </div>

                <div className="query-action-bar">
                  <button
                    type="button"
                    className="editorial-action-btn btn-sm"
                    disabled={executing}
                    onClick={() => runPredefinedQuery(selectedQueryId)}
                  >
                    <IconRefresh size={13} /> {executing ? "Executing..." : "Re-run Query"}
                  </button>
                </div>
              </div>
            )}

            {/* Results Area */}
            {execError ? (
              <div className="editorial-error-box" role="alert">
                <p>{execError}</p>
              </div>
            ) : executing ? (
              <div className="editorial-loading-state" role="status" aria-live="polite">
                <div className="editorial-spinner" />
                <p>Executing relational query against PostgreSQL...</p>
              </div>
            ) : queryResult ? (
              <div className="editorial-data-table-container">
                <div className="data-table-metrics">
                  <span className="metric-unit">
                    Returned: <strong>{queryResult.row_count} rows</strong>
                  </span>
                  <span className="metric-separator">·</span>
                  <span className="metric-unit">
                    Latency: <strong>{queryResult.execution_time_ms} ms</strong>
                  </span>
                </div>

                <div className="data-table-scroll">
                  <table className="editorial-data-table" aria-label={`Results table for ${selectedQueryId}`}>
                    <thead>
                      <tr>
                        {queryResult.columns.map((col) => (
                          <th key={col}>{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {queryResult.rows.length === 0 ? (
                        <tr>
                          <td colSpan={queryResult.columns.length} className="no-rows-cell">
                            No rows matched the query conditions.
                          </td>
                        </tr>
                      ) : (
                        queryResult.rows.map((row, rIdx) => (
                          <tr key={rIdx}>
                            {queryResult.columns.map((col) => (
                              <td key={col}>{String(row[col] ?? "NULL")}</td>
                            ))}
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : null}
          </main>
        </div>
      )}

      {/* Tab 2: Interactive Custom SQL Editor */}
      {activeTab === "custom" && (
        <div className="custom-editor-layout">
          <div className="custom-editor-shell" role="region" aria-label="Custom SQL Editor">
            <div className="custom-editor-header">
              <div>
                <span className="editorial-eyebrow">READ-ONLY PLAYGROUND</span>
                <h2 className="editor-title">Custom Relational SQL</h2>
              </div>
              <span className="postgres-version-tag">PostgreSQL 15+</span>
            </div>
            <p className="editor-explanation">
              Execute custom <code>SELECT</code> queries with multi-table joins, subqueries, or window aggregations directly against the normalized database schema.
            </p>

            <form onSubmit={handleCustomSQLExecute} className="custom-sql-form">
              <div className="sql-input-wrap">
                <textarea
                  className="editorial-sql-textarea"
                  rows={6}
                  value={customSQL}
                  onChange={(e) => setCustomSQL(e.target.value)}
                  placeholder="Type your SELECT query here..."
                  required
                  disabled={executing}
                  aria-label="SQL Query Input"
                />
              </div>

              <div className="custom-editor-footer">
                <div className="sample-queries-list">
                  <span className="sample-label">Sample queries:</span>
                  <button
                    type="button"
                    className="sample-link"
                    onClick={() => setCustomSQL("SELECT * FROM view_trip_costs_by_category LIMIT 10;")}
                    disabled={executing}
                  >
                    Category Costs View
                  </button>
                  <button
                    type="button"
                    className="sample-link"
                    onClick={() =>
                      setCustomSQL(
                        "SELECT d.city, COUNT(h.id) AS hotels, COUNT(r.id) AS dining FROM destinations d LEFT JOIN hotels h ON h.destination_id = d.id LEFT JOIN restaurants r ON r.destination_id = d.id GROUP BY d.city ORDER BY hotels DESC LIMIT 10;"
                      )
                    }
                    disabled={executing}
                  >
                    Multi-JOIN Aggregate
                  </button>
                </div>

                <button type="submit" className="editorial-action-btn" disabled={executing}>
                  {executing ? "Executing Query..." : "Execute SQL"}
                </button>
              </div>
            </form>
          </div>

          {execError && (
            <div className="editorial-error-box" role="alert">
              <p>{execError}</p>
            </div>
          )}

          {executing ? (
            <div className="editorial-loading-state" role="status" aria-live="polite">
              <div className="editorial-spinner" />
              <p>Executing query on PostgreSQL database...</p>
            </div>
          ) : (
            queryResult && (
              <div className="editorial-data-table-container">
                <div className="data-table-metrics">
                  <span className="metric-unit">
                    Returned: <strong>{queryResult.row_count} rows</strong>
                  </span>
                  <span className="metric-separator">·</span>
                  <span className="metric-unit">
                    Latency: <strong>{queryResult.execution_time_ms} ms</strong>
                  </span>
                </div>

                <div className="data-table-scroll">
                  <table className="editorial-data-table" aria-label="Custom SQL Query Results">
                    <thead>
                      <tr>
                        {queryResult.columns.map((col) => (
                          <th key={col}>{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {queryResult.rows.length === 0 ? (
                        <tr>
                          <td colSpan={queryResult.columns.length} className="no-rows-cell">
                            No rows matched the query conditions.
                          </td>
                        </tr>
                      ) : (
                        queryResult.rows.map((row, rIdx) => (
                          <tr key={rIdx}>
                            {queryResult.columns.map((col) => (
                              <td key={col}>{String(row[col] ?? "NULL")}</td>
                            ))}
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )
          )}
        </div>
      )}

      {/* Tab 3: PL/pgSQL Audit Trigger Logs */}
      {activeTab === "audit" && (
        <div className="audit-logs-layout">
          <div className="audit-header-row">
            <div>
              <span className="editorial-eyebrow">INTEGRITY ENFORCEMENT</span>
              <h2 className="editor-title">PL/pgSQL Audit Triggers</h2>
            </div>
            <button
              type="button"
              className="editorial-quiet-btn"
              onClick={loadAuditTriggerLogs}
              disabled={auditLoading}
            >
              <IconRefresh size={13} /> {auditLoading ? "Refreshing..." : "Refresh Logs"}
            </button>
          </div>
          <p className="editor-explanation">
            Automated database triggers record every table modification into the <code>audit_logs</code> relation, capturing transaction timestamp, user ID, operation type (INSERT/UPDATE/DELETE), and change deltas.
          </p>

          {auditLoading ? (
            <div className="editorial-loading-state" role="status" aria-live="polite">
              <div className="editorial-spinner" />
              <p>Fetching trigger audit trail from PostgreSQL...</p>
            </div>
          ) : auditLogs.length === 0 ? (
            <div className="editorial-empty-state">
              <p className="empty-title">No Audit Events Logged</p>
              <p className="empty-desc">Create or update a trip itinerary to trigger PL/pgSQL audit records.</p>
            </div>
          ) : (
            <div className="editorial-data-table-container">
              <div className="data-table-scroll">
                <table className="editorial-data-table" aria-label="PL/pgSQL Audit Trigger Logs">
                  <thead>
                    <tr>
                      <th>LOG ID</th>
                      <th>ACTION</th>
                      <th>TABLE</th>
                      <th>RECORD ID</th>
                      <th>CHANGED AT</th>
                      <th>PAYLOAD CHANGES</th>
                    </tr>
                  </thead>
                  <tbody>
                    {auditLogs.map((log) => (
                      <tr key={log.id}>
                        <td>{log.id}</td>
                        <td>
                          <span className={`audit-action-tag tag-${log.action.toLowerCase()}`}>
                            {log.action}
                          </span>
                        </td>
                        <td><code>{log.table_name}</code></td>
                        <td>{log.record_id}</td>
                        <td>{log.changed_at ? new Date(log.changed_at).toLocaleString() : "N/A"}</td>
                        <td>
                          <pre className="audit-json-snippet">
                            {JSON.stringify(log.changed_fields, null, 2)}
                          </pre>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
