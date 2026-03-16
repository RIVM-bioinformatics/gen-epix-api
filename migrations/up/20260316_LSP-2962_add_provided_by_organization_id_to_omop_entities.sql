-- Migration: LSP-2962 Add provided_by_organization_id to OMOP entities
-- Adds an optional FK column to all non-derived OMOP tables linked to Person.
-- Idempotent: each column is only added if it does not already exist.

IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[person]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[person] ADD provided_by_organization_id UNIQUEIDENTIFIER NULL;

IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[observation_period]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[observation_period] ADD provided_by_organization_id UNIQUEIDENTIFIER NULL;

IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[visit_occurrence]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[visit_occurrence] ADD provided_by_organization_id UNIQUEIDENTIFIER NULL;

IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[visit_detail]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[visit_detail] ADD provided_by_organization_id UNIQUEIDENTIFIER NULL;

IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[condition_occurrence]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[condition_occurrence] ADD provided_by_organization_id UNIQUEIDENTIFIER NULL;

IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[procedure_occurrence]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[procedure_occurrence] ADD provided_by_organization_id UNIQUEIDENTIFIER NULL;

IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[drug_exposure]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[drug_exposure] ADD provided_by_organization_id UNIQUEIDENTIFIER NULL;

IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[device_exposure]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[device_exposure] ADD provided_by_organization_id UNIQUEIDENTIFIER NULL;

IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[measurement]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[measurement] ADD provided_by_organization_id UNIQUEIDENTIFIER NULL;

IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[observation]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[observation] ADD provided_by_organization_id UNIQUEIDENTIFIER NULL;

IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[specimen]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[specimen] ADD provided_by_organization_id UNIQUEIDENTIFIER NULL;

IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[note]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[note] ADD provided_by_organization_id UNIQUEIDENTIFIER NULL;

IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[death]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[death] ADD provided_by_organization_id UNIQUEIDENTIFIER NULL;

IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[payer_plan_period]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[payer_plan_period] ADD provided_by_organization_id UNIQUEIDENTIFIER NULL;

IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[cost]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[cost] ADD provided_by_organization_id UNIQUEIDENTIFIER NULL;
