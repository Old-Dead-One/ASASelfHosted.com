-- ASASelfHosted.com - Sprint 5 Anomaly Detection
-- This migration adds anomaly detection fields to servers table
-- Run this in Supabase SQL Editor after 006_sprint_4_agent_auth.sql

-- ============================================================================
-- SERVERS TABLE EXTENSIONS
-- ============================================================================

-- Add anomaly detection fields (derived metrics, computed by worker)
DO $$ BEGIN
    ALTER TABLE servers ADD COLUMN anomaly_players_spike BOOLEAN;
EXCEPTION
    WHEN duplicate_column THEN null;
END $$;

DO $$ BEGIN
    ALTER TABLE servers ADD COLUMN anomaly_last_detected_at TIMESTAMPTZ;
EXCEPTION
    WHEN duplicate_column THEN null;
END $$;

COMMENT ON COLUMN servers.anomaly_players_spike IS 'Anomaly flag: True if impossible/suspicious player spike detected, False if cleared, NULL if never set. Derived metric computed by worker.';
COMMENT ON COLUMN servers.anomaly_last_detected_at IS 'Timestamp of last detected anomaly (for decay logic). Cleared when anomaly flag is cleared.';
