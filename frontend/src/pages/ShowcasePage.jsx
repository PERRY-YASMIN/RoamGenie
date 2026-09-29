import { useEffect, useMemo, useState } from "react";
import { useToast } from "../context/ToastContext";
import { executeCustomSQL, executeReportQuery, getAuditLogs, getReportQueries } from "../services/api";

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
    <div className="showcase-container">
      <div className="showcase-overlay-card">
        {/* Page Header */}
        <div className="page-header showcase-header">
          <p className="eyebrow">DBMS Course Project Demonstration</p>
          <h1>Relational Engine & SQL Query Playground</h1>
          <p className="showcase-intro">
            Interactive demonstration interface showcasing 18 analytical SQL benchmark queries,
            multi-table relational joins, subqueries, aggregations, window functions, and PL/pgSQL
            audit triggers executing live against PostgreSQL.
          </p>

          {/* Primary Navigation Tabs */}
          <div className="showcase-tabs" role="tablist" aria-label="DBMS showcase sections">
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === "predefined"}
              className={`tab-btn ${activeTab === "predefined" ? "active" : ""}`}
              onClick={() => setActiveTab("predefined")}
            >
              📊 18 SQL Benchmark Queries
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === "custom"}
              className={`tab-btn ${activeTab === "custom" ? "active" : ""}`}
              onClick={() => setActiveTab("custom")}
            >
              ⚡ Custom SQL Editor
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === "audit"}
              className={`tab-btn ${activeTab === "audit" ? "active" : ""}`}
              onClick={() => setActiveTab("audit")}
            >
              🛡️ PL/pgSQL Audit Trigger Logs
            </button>
          </div>
        </div>

        {/* Tab 1: 18 Predefined Benchmark Queries */}
        {activeTab === "predefined" && (
          <div className="showcase-layout">
            {/* Sidebar Query Selector */}
            <aside className="query-selector-sidebar" aria-label="Benchmark Query Selector">
              <div className="sidebar-header">
                <h3>Benchmark Queries</h3>
                <span className="query-count-badge">{filteredQueries.length} of {queries.length}</span>
              </div>

              {/* Category Filter Chips */}
              <div className="category-filter-chips" role="toolbar" aria-label="Filter queries by category">
                {categories.map((cat) => (
                  <button
                    key={cat}
                    type="button"
                    className={`category-chip ${selectedCategory === cat ? "active" : ""}`}
                    onClick={() => setSelectedCategory(cat)}
                  >
                    {cat}
                  </button>
                ))}
              </div>

              {/* Query Buttons List */}
              <div className="query-list" role="tablist" aria-orientation="vertical">
                {filteredQueries.map((q) => (
                  <button
                    key={q.id}
                    type="button"
                    role="tab"
                    aria-selected={selectedQueryId === q.id}
                    className={`query-item-btn ${selectedQueryId === q.id ? "active" : ""}`}
                    onClick={() => {
                      setSelectedQueryId(q.id);
                      runPredefinedQuery(q.id);
                    }}
                    aria-label={`Select query ${q.id}: ${q.title}`}
                  >
                    <span className="query-id-chip">{q.id}</span>
                    <div className="query-info">
                      <strong className="query-title">{q.title}</strong>
                      <span className="query-category-tag">{q.category}</span>
                    </div>
                  </button>
                ))}
              </div>
            </aside>

            {/* Main Execution Output Panel */}
            <main className="query-output-panel" aria-label="Query Execution Output">
              {currentQueryMeta && (
                <div className="query-meta-card">
                  <div className="meta-top">
                    <span className="category-pill">{currentQueryMeta.category}</span>
                    <span className="sql-version-tag">PostgreSQL 15+</span>
                  </div>

                  <h2>
                    <span className="query-hero-id">{currentQueryMeta.id}:</span> {currentQueryMeta.title}
                  </h2>
                  <p className="query-desc">{currentQueryMeta.description}</p>

                  {/* SQL Code Block */}
                  <div className="sql-card">
                    <div className="sql-card-header">
                      <span>SQL Statement</span>
                      <button
                        type="button"
                        className="copy-sql-btn"
                        onClick={handleCopySQL}
                        title="Copy SQL statement to clipboard"
                      >
                        {copiedSql ? "✓ Copied" : "📋 Copy SQL"}
                      </button>
                    </div>
                    <pre className="sql-code-block">
                      <code>{currentQueryMeta.sql}</code>
                    </pre>
                  </div>

                  <div className="meta-actions">
                    <button
                      type="button"
                      className="button button-primary"
                      disabled={executing}
                      onClick={() => runPredefinedQuery(selectedQueryId)}
                    >
                      {executing ? "Executing Query..." : "▶ Re-run Query"}
                    </button>
                  </div>
                </div>
              )}

              {/* Results Table Area */}
              {execError ? (
                <div className="error-banner" role="alert">
                  <p>⚠️ {execError}</p>
                </div>
              ) : executing ? (
                <div className="loading-state" role="status" aria-live="polite">
                  <div className="spinner"></div>
                  <p>Executing SQL query against PostgreSQL...</p>
                </div>
              ) : queryResult ? (
                <div className="results-table-card">
                  <div className="table-header-metrics">
                    <div className="metric-chip">
                      <span>Returned Rows:</span>
                      <strong>{queryResult.row_count}</strong>
                    </div>
                    <div className="metric-chip">
                      <span>Execution Time:</span>
                      <strong>{queryResult.execution_time_ms} ms</strong>
                    </div>
                  </div>

                  <div className="table-responsive">
                    <table className="db-table" aria-label={`Results table for ${selectedQueryId}`}>
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
                            <td colSpan={queryResult.columns.length} className="no-rows">
                              No rows matched the query criteria.
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
          <div className="custom-sql-panel">
            <div className="custom-editor-card" role="region" aria-label="Custom SQL Editor">
              <div className="editor-card-header">
                <h2>Interactive SQL Playground (Read-Only)</h2>
                <span className="sql-version-tag">PostgreSQL 15+</span>
              </div>
              <p className="editor-desc">
                Execute custom <code>SELECT</code> queries with multi-table joins, subqueries, or
                window aggregations directly against the normalized database schema.
              </p>

              <form onSubmit={handleCustomSQLExecute}>
                <div className="sql-textarea-wrapper">
                  <textarea
                    className="sql-textarea"
                    rows={6}
                    value={customSQL}
                    onChange={(e) => setCustomSQL(e.target.value)}
                    placeholder="Type your SELECT query here..."
                    required
                    disabled={executing}
                    aria-label="SQL Query Input"
                  />
                </div>

                <div className="editor-footer">
                  <div className="quick-sql-hints">
                    <span className="hints-label">Sample queries:</span>
                    <button
                      type="button"
                      className="hint-chip"
                      onClick={() => setCustomSQL("SELECT * FROM view_trip_costs_by_category LIMIT 10;")}
                      disabled={executing}
                    >
                      Category Costs View
                    </button>
                    <button
                      type="button"
                      className="hint-chip"
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

                  <button type="submit" className="button button-primary" disabled={executing}>
                    {executing ? "Running Query..." : "▶ Execute SQL"}
                  </button>
                </div>
              </form>
            </div>

            {execError && (
              <div className="error-banner" role="alert">
                <p>⚠️ {execError}</p>
              </div>
            )}

            {executing ? (
              <div className="loading-state" role="status" aria-live="polite">
                <div className="spinner"></div>
                <p>Executing SQL query on PostgreSQL...</p>
              </div>
            ) : (
              queryResult && (
                <div className="results-table-card">
                  <div className="table-header-metrics">
                    <div className="metric-chip">
                      <span>Returned Rows:</span>
                      <strong>{queryResult.row_count}</strong>
                    </div>
                    <div className="metric-chip">
                      <span>Execution Time:</span>
                      <strong>{queryResult.execution_time_ms} ms</strong>
                    </div>
                  </div>

                  <div className="table-responsive">
                    <table className="db-table" aria-label="Custom SQL Query Results">
                      <thead>
                        <tr>
                          {queryResult.columns.map((col) => (
                            <th key={col}>{col}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {queryResult.rows.map((row, rIdx) => (
                          <tr key={rIdx}>
                            {queryResult.columns.map((col) => (
                              <td key={col}>{String(row[col] ?? "NULL")}</td>
                            ))}
                          </tr>
                        ))}
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
          <div className="audit-logs-panel">
            <div className="audit-header-card">
              <div className="audit-meta">
                <h2>PL/pgSQL Trigger: <code>trg_trip_audit</code></h2>
                <p>
                  Every row-level mutation (<code>INSERT</code>, <code>UPDATE</code>, <code>DELETE</code>)
                  on the <code>trips</code> table executes the database trigger and automatically commits
                  immutable JSONB snapshots into <code>trip_audit</code>.
                </p>
              </div>
              <button
                type="button"
                className="button button-primary"
                onClick={loadAuditTriggerLogs}
                disabled={auditLoading}
              >
                {auditLoading ? "Refreshing..." : "🔄 Refresh Audit Logs"}
              </button>
            </div>

            {auditLoading ? (
              <div className="loading-state" role="status" aria-live="polite">
                <div className="spinner"></div>
                <p>Fetching trigger logs from trip_audit...</p>
              </div>
            ) : auditLogs.length === 0 ? (
              <div className="empty-state">
                <div className="placeholder-icon">🛡️</div>
                <p>
                  No mutation records logged yet. Create, edit, or delete a trip to see audit trigger logs
                  appear here in real-time!
                </p>
              </div>
            ) : (
              <div className="audit-table-card">
                <div className="table-responsive">
                  <table className="db-table" aria-label="Audit Trigger Logs Table">
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Trip ID</th>
                        <th>Action</th>
                        <th>Timestamp (UTC)</th>
                        <th>User ID</th>
                        <th>Captured Row Snapshot</th>
                      </tr>
                    </thead>
                    <tbody>
                      {auditLogs.map((log) => (
                        <tr key={log.id}>
                          <td>{log.id}</td>
                          <td>{log.trip_id || "N/A"}</td>
                          <td>
                            <span className={`action-badge ${log.action.toLowerCase()}`}>
                              {log.action}
                            </span>
                          </td>
                          <td>{new Date(log.changed_at).toLocaleString()}</td>
                          <td>{log.changed_by || "system"}</td>
                          <td>
                            <pre className="json-snippet">
                              {JSON.stringify(log.new_row || log.old_row, null, 2)}
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
    </div>
  );
}
