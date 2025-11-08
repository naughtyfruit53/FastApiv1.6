-- Entitlements and Licensing Schema
-- Designed for FastAPI v1.6 with PostgreSQL
-- Adapts org_id FK type to INT (matching current Organization.id)

-- Module taxonomy table
CREATE TABLE IF NOT EXISTS modules (
    id SERIAL PRIMARY KEY,
    module_key VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    icon VARCHAR(100),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_modules_key ON modules(module_key);
CREATE INDEX idx_modules_active ON modules(is_active);

-- Submodule taxonomy table
CREATE TABLE IF NOT EXISTS submodules (
    id SERIAL PRIMARY KEY,
    module_id INTEGER NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    submodule_key VARCHAR(100) NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    menu_path VARCHAR(500),
    permission_key VARCHAR(200),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(module_id, submodule_key)
);

CREATE INDEX idx_submodules_module ON submodules(module_id);
CREATE INDEX idx_submodules_key ON submodules(submodule_key);
CREATE INDEX idx_submodules_active ON submodules(is_active);

-- License plans (e.g., Starter, Professional, Enterprise)
CREATE TABLE IF NOT EXISTS plans (
    id SERIAL PRIMARY KEY,
    plan_key VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    price_monthly DECIMAL(10, 2),
    price_annual DECIMAL(10, 2),
    is_active BOOLEAN DEFAULT true NOT NULL,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_plans_key ON plans(plan_key);
CREATE INDEX idx_plans_active ON plans(is_active);

-- Plan entitlements (which modules/submodules are included in each plan)
CREATE TABLE IF NOT EXISTS plan_entitlements (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER NOT NULL REFERENCES plans(id) ON DELETE CASCADE,
    module_id INTEGER NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    submodule_id INTEGER REFERENCES submodules(id) ON DELETE CASCADE,
    is_included BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(plan_id, module_id, submodule_id)
);

CREATE INDEX idx_plan_entitlements_plan ON plan_entitlements(plan_id);
CREATE INDEX idx_plan_entitlements_module ON plan_entitlements(module_id);
CREATE INDEX idx_plan_entitlements_submodule ON plan_entitlements(submodule_id);

-- Organization-level module entitlements
CREATE TABLE IF NOT EXISTS org_entitlements (
    id SERIAL PRIMARY KEY,
    org_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    module_id INTEGER NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'disabled' NOT NULL CHECK (status IN ('enabled', 'disabled', 'trial')),
    trial_expires_at TIMESTAMP WITH TIME ZONE,
    source VARCHAR(100) DEFAULT 'manual',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(org_id, module_id)
);

CREATE INDEX idx_org_entitlements_org ON org_entitlements(org_id);
CREATE INDEX idx_org_entitlements_module ON org_entitlements(module_id);
CREATE INDEX idx_org_entitlements_org_module ON org_entitlements(org_id, module_id);
CREATE INDEX idx_org_entitlements_status ON org_entitlements(status);

-- Organization-level submodule entitlements (fine-grained control)
CREATE TABLE IF NOT EXISTS org_subentitlements (
    id SERIAL PRIMARY KEY,
    org_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    module_id INTEGER NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    submodule_id INTEGER NOT NULL REFERENCES submodules(id) ON DELETE CASCADE,
    enabled BOOLEAN DEFAULT true NOT NULL,
    source VARCHAR(100) DEFAULT 'manual',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(org_id, module_id, submodule_id)
);

CREATE INDEX idx_org_subentitlements_org ON org_subentitlements(org_id);
CREATE INDEX idx_org_subentitlements_module ON org_subentitlements(module_id);
CREATE INDEX idx_org_subentitlements_submodule ON org_subentitlements(submodule_id);
CREATE INDEX idx_org_subentitlements_org_module ON org_subentitlements(org_id, module_id);
CREATE INDEX idx_org_subentitlements_org_module_sub ON org_subentitlements(org_id, module_id, submodule_id);

-- Entitlement audit/event log
CREATE TABLE IF NOT EXISTS entitlement_events (
    id SERIAL PRIMARY KEY,
    org_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    actor_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    reason TEXT,
    payload JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_entitlement_events_org ON entitlement_events(org_id);
CREATE INDEX idx_entitlement_events_type ON entitlement_events(event_type);
CREATE INDEX idx_entitlement_events_actor ON entitlement_events(actor_user_id);
CREATE INDEX idx_entitlement_events_created ON entitlement_events(created_at);

-- View for effective entitlements (combines org_entitlements and org_subentitlements)
CREATE OR REPLACE VIEW v_effective_entitlements AS
SELECT 
    oe.org_id,
    m.id AS module_id,
    m.module_key,
    m.display_name AS module_display_name,
    oe.status AS module_status,
    oe.trial_expires_at,
    s.id AS submodule_id,
    s.submodule_key,
    s.display_name AS submodule_display_name,
    COALESCE(ose.enabled, true) AS submodule_enabled,
    CASE 
        WHEN oe.status = 'enabled' AND COALESCE(ose.enabled, true) = true THEN 'enabled'
        WHEN oe.status = 'trial' AND COALESCE(ose.enabled, true) = true AND (oe.trial_expires_at IS NULL OR oe.trial_expires_at > CURRENT_TIMESTAMP) THEN 'trial'
        ELSE 'disabled'
    END AS effective_status,
    oe.source AS module_source,
    ose.source AS submodule_source
FROM org_entitlements oe
INNER JOIN modules m ON oe.module_id = m.id
LEFT JOIN submodules s ON s.module_id = m.id
LEFT JOIN org_subentitlements ose ON ose.org_id = oe.org_id AND ose.module_id = m.id AND ose.submodule_id = s.id
WHERE m.is_active = true;

-- Comments for documentation
COMMENT ON TABLE modules IS 'Module taxonomy - top-level features like sales, inventory, manufacturing';
COMMENT ON TABLE submodules IS 'Submodule taxonomy - fine-grained features within modules';
COMMENT ON TABLE plans IS 'License plans (Starter, Professional, Enterprise)';
COMMENT ON TABLE plan_entitlements IS 'Default entitlements included in each plan';
COMMENT ON TABLE org_entitlements IS 'Organization-level module entitlements with status (enabled/disabled/trial)';
COMMENT ON TABLE org_subentitlements IS 'Organization-level submodule entitlements for fine-grained control';
COMMENT ON TABLE entitlement_events IS 'Audit log for all entitlement changes';
COMMENT ON VIEW v_effective_entitlements IS 'Computed view of effective entitlements per org combining modules and submodules';
