-- OPTIONAL LOCAL FALLBACK ONLY. Do not run on Supabase: its project/database
-- already exists and managed roles must not be recreated. Set a local password
-- interactively; never store it here. Application migrations remain authoritative.
CREATE ROLE roamgenie_app LOGIN;
CREATE ROLE roamgenie_readonly NOLOGIN;
CREATE DATABASE roamgenie OWNER roamgenie_app;
-- If objects already exist, PostgreSQL will stop safely; do not add destructive drops.
