-- OAuth2 Email Token Management Tables
-- Add encrypted user_email_tokens and oauth_states tables for OAuth2 functionality

-- Create user_email_tokens table for encrypted OAuth token storage
CREATE TABLE IF NOT EXISTS user_email_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL CHECK (provider IN ('google', 'microsoft', 'outlook', 'gmail')),
    email_address VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    
    -- Encrypted OAuth tokens (stored using app-level encryption)
    access_token_encrypted TEXT NOT NULL,
    refresh_token_encrypted TEXT,
    id_token_encrypted TEXT,
    
    -- Token metadata
    scope TEXT,
    token_type VARCHAR(50) NOT NULL DEFAULT 'Bearer',
    expires_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'expired', 'revoked', 'refresh_failed')),
    
    -- Provider-specific metadata
    provider_metadata JSONB,
    
    -- Sync settings
    sync_enabled BOOLEAN NOT NULL DEFAULT true,
    sync_folders JSONB, -- Array of folder names to sync
    last_sync_at TIMESTAMP WITH TIME ZONE,
    last_sync_status VARCHAR(50),
    last_sync_error TEXT,
    
    -- Security and audit
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_used_at TIMESTAMP WITH TIME ZONE,
    refresh_count INTEGER NOT NULL DEFAULT 0,
    
    -- Indexes
    CONSTRAINT idx_user_email_tokens_user_org UNIQUE (user_id, organization_id, provider, email_address)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_email_tokens_user_id ON user_email_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_user_email_tokens_organization_id ON user_email_tokens(organization_id);
CREATE INDEX IF NOT EXISTS idx_user_email_tokens_email_address ON user_email_tokens(email_address);
CREATE INDEX IF NOT EXISTS idx_user_email_tokens_provider ON user_email_tokens(provider);
CREATE INDEX IF NOT EXISTS idx_user_email_tokens_status ON user_email_tokens(status);
CREATE INDEX IF NOT EXISTS idx_user_email_tokens_expires_at ON user_email_tokens(expires_at);

-- Create oauth_states table for temporary OAuth state storage
CREATE TABLE IF NOT EXISTS oauth_states (
    id SERIAL PRIMARY KEY,
    state VARCHAR(255) NOT NULL UNIQUE,
    provider VARCHAR(50) NOT NULL CHECK (provider IN ('google', 'microsoft', 'outlook', 'gmail')),
    
    -- User context
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Flow metadata
    redirect_uri VARCHAR(500),
    scope TEXT,
    code_verifier VARCHAR(255), -- For PKCE
    nonce VARCHAR(255), -- For OpenID Connect
    
    -- Expiry
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for oauth_states
CREATE INDEX IF NOT EXISTS idx_oauth_states_state ON oauth_states(state);
CREATE INDEX IF NOT EXISTS idx_oauth_states_user_id ON oauth_states(user_id);
CREATE INDEX IF NOT EXISTS idx_oauth_states_organization_id ON oauth_states(organization_id);
CREATE INDEX IF NOT EXISTS idx_oauth_states_expires_at ON oauth_states(expires_at);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_email_tokens_updated_at 
    BEFORE UPDATE ON user_email_tokens 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE user_email_tokens IS 'Encrypted storage for OAuth2 email tokens with automatic refresh capability';
COMMENT ON COLUMN user_email_tokens.access_token_encrypted IS 'Encrypted OAuth2 access token using PII encryption key';
COMMENT ON COLUMN user_email_tokens.refresh_token_encrypted IS 'Encrypted OAuth2 refresh token using PII encryption key';
COMMENT ON COLUMN user_email_tokens.id_token_encrypted IS 'Encrypted OpenID Connect ID token using PII encryption key';
COMMENT ON COLUMN user_email_tokens.provider_metadata IS 'Provider-specific user information and metadata';
COMMENT ON COLUMN user_email_tokens.sync_folders IS 'JSON array of email folder names to sync';

COMMENT ON TABLE oauth_states IS 'Temporary storage for OAuth2 state during authorization flow';
COMMENT ON COLUMN oauth_states.code_verifier IS 'PKCE code verifier for secure OAuth2 flow';
COMMENT ON COLUMN oauth_states.nonce IS 'OpenID Connect nonce for security';

-- Create function to clean up expired OAuth states
CREATE OR REPLACE FUNCTION cleanup_expired_oauth_states()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM oauth_states WHERE expires_at < NOW();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Example of how to use the cleanup function (could be scheduled as a cron job)
-- SELECT cleanup_expired_oauth_states();