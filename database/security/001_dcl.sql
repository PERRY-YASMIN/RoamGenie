-- ============================================================================
-- RoamGenie — Data Control Language (DCL) Security Specification
-- Demonstrates Role-Based Access Control (RBAC), Privilege Grants (GRANT),
-- and Privilege Revocations (REVOKE) for PostgreSQL
-- ============================================================================

-- Step 1: Create application service and analytics roles safely
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'roamgenie_app_role') THEN
        CREATE ROLE roamgenie_app_role WITH NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'roamgenie_analyst_role') THEN
        CREATE ROLE roamgenie_analyst_role WITH NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'roamgenie_auditor_role') THEN
        CREATE ROLE roamgenie_auditor_role WITH NOLOGIN;
    END IF;
END $$;

-- Step 2: Grant schema usage
GRANT USAGE ON SCHEMA public TO roamgenie_app_role, roamgenie_analyst_role, roamgenie_auditor_role;

-- Step 3: Grant operational privileges to application role (CRUD for application services)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO roamgenie_app_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO roamgenie_app_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO roamgenie_app_role;
GRANT EXECUTE ON ALL PROCEDURES IN SCHEMA public TO roamgenie_app_role;

-- Step 4: Grant read-only reporting privileges to analytics role
GRANT SELECT ON ALL TABLES IN SCHEMA public TO roamgenie_analyst_role;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO roamgenie_analyst_role;

-- Step 5: Grant specialized audit & view privileges to auditor role
GRANT SELECT ON trip_audit TO roamgenie_auditor_role;
GRANT SELECT ON v_trip_budget_summary TO roamgenie_auditor_role;
GRANT SELECT ON v_destination_catalogue TO roamgenie_auditor_role;

-- Step 6: Revoke dangerous modification privileges from analyst and public roles
-- Enforce principle of least privilege: Analysts cannot mutate catalogue or transactions
REVOKE INSERT, UPDATE, DELETE, TRUNCATE ON ALL TABLES IN SCHEMA public FROM roamgenie_analyst_role;
REVOKE INSERT, UPDATE, DELETE, TRUNCATE ON ALL TABLES IN SCHEMA public FROM roamgenie_auditor_role;

-- Ensure public cannot execute arbitrary DDL or read sensitive audit logs
REVOKE ALL ON trip_audit FROM PUBLIC;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

-- Default privileges for future tables created in public schema
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO roamgenie_app_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO roamgenie_analyst_role;
