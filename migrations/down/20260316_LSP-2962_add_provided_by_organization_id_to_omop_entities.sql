-- Rollback: LSP-2962 Add provided_by_organization_id to OMOP entities
-- Drops the provided_by_organization_id column from all affected OMOP tables.
-- Idempotent: each column is only dropped if it exists.

IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[person]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[person] DROP COLUMN provided_by_organization_id;

IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[observation_period]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[observation_period] DROP COLUMN provided_by_organization_id;

IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[visit_occurrence]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[visit_occurrence] DROP COLUMN provided_by_organization_id;

IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[visit_detail]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[visit_detail] DROP COLUMN provided_by_organization_id;

IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[condition_occurrence]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[condition_occurrence] DROP COLUMN provided_by_organization_id;

IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[procedure_occurrence]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[procedure_occurrence] DROP COLUMN provided_by_organization_id;

IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[drug_exposure]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[drug_exposure] DROP COLUMN provided_by_organization_id;

IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[device_exposure]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[device_exposure] DROP COLUMN provided_by_organization_id;

IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[measurement]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[measurement] DROP COLUMN provided_by_organization_id;

IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[observation]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[observation] DROP COLUMN provided_by_organization_id;

IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[specimen]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[specimen] DROP COLUMN provided_by_organization_id;

IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[note]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[note] DROP COLUMN provided_by_organization_id;

IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[death]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[death] DROP COLUMN provided_by_organization_id;

IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[payer_plan_period]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[payer_plan_period] DROP COLUMN provided_by_organization_id;

IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[omop].[cost]') AND name = 'provided_by_organization_id')
    ALTER TABLE [omop].[cost] DROP COLUMN provided_by_organization_id;
