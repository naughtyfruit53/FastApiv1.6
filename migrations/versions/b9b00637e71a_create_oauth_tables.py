"""create_oauth_tables

Revision ID: b9b00637e71a
Revises: 321e6d5d5137
Create Date: 2025-10-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b9b00637e71a'
down_revision = '321e6d5d5137'
branch_labels = None
depends_on = None


def upgrade():
    # Conditional creation for ENUM types
    conn = op.get_bind()
    
    # Check and create oauthprovider
    exists = conn.execute(sa.text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'oauthprovider')")).scalar()
    if not exists:
        op.execute("CREATE TYPE oauthprovider AS ENUM ('google', 'microsoft', 'outlook', 'gmail')")
    
    # Check and create tokenstatus
    exists = conn.execute(sa.text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tokenstatus')")).scalar()
    if not exists:
        op.execute("CREATE TYPE tokenstatus AS ENUM ('active', 'expired', 'revoked', 'refresh_failed')")
    
    # Check and create oauth_states table
    table_exists = conn.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'oauth_states')"
    )).scalar()
    if not table_exists:
        op.create_table('oauth_states',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('state', sa.String(length=255), nullable=False),
            sa.Column('provider', postgresql.ENUM('google', 'microsoft', 'outlook', 'gmail', name='oauthprovider', create_type=False), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('organization_id', sa.Integer(), nullable=True),
            sa.Column('redirect_uri', sa.String(length=500), nullable=True),
            sa.Column('scope', sa.Text(), nullable=True),
            sa.Column('code_verifier', sa.String(length=255), nullable=True),
            sa.Column('nonce', sa.String(length=255), nullable=True),
            sa.Column('expires_at', sa.DateTime(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('state')
        )
    else:
        print("Table oauth_states already exists, skipping creation.")
    
    op.create_index(op.f('ix_oauth_states_id'), 'oauth_states', ['id'], unique=False, if_not_exists=True)
    op.create_index(op.f('ix_oauth_states_organization_id'), 'oauth_states', ['organization_id'], unique=False, if_not_exists=True)
    op.create_index(op.f('ix_oauth_states_state'), 'oauth_states', ['state'], unique=False, if_not_exists=True)
    op.create_index(op.f('ix_oauth_states_user_id'), 'oauth_states', ['user_id'], unique=False, if_not_exists=True)
    
    # Check and create user_email_tokens table
    table_exists = conn.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'user_email_tokens')"
    )).scalar()
    if not table_exists:
        op.create_table('user_email_tokens',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('organization_id', sa.Integer(), nullable=True),
            sa.Column('provider', postgresql.ENUM('google', 'microsoft', 'outlook', 'gmail', name='oauthprovider', create_type=False), nullable=False),
            sa.Column('email_address', sa.String(length=255), nullable=False),
            sa.Column('display_name', sa.String(length=255), nullable=True),
            sa.Column('access_token_encrypted', sa.String(), nullable=False),
            sa.Column('refresh_token_encrypted', sa.String(), nullable=True),
            sa.Column('id_token_encrypted', sa.String(), nullable=True),
            sa.Column('scope', sa.Text(), nullable=True),
            sa.Column('token_type', sa.String(length=50), nullable=False),
            sa.Column('expires_at', sa.DateTime(), nullable=True),
            sa.Column('status', postgresql.ENUM('active', 'expired', 'revoked', 'refresh_failed', name='tokenstatus', create_type=False), nullable=False),
            sa.Column('provider_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
            sa.Column('sync_enabled', sa.Boolean(), nullable=False),
            sa.Column('sync_folders', postgresql.JSON(astext_type=sa.Text()), nullable=True),
            sa.Column('last_sync_at', sa.DateTime(), nullable=True),
            sa.Column('last_sync_status', sa.String(length=50), nullable=True),
            sa.Column('last_sync_error', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.Column('last_used_at', sa.DateTime(), nullable=True),
            sa.Column('refresh_count', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    else:
        print("Table user_email_tokens already exists, skipping creation.")
    
    op.create_index(op.f('ix_user_email_tokens_email_address'), 'user_email_tokens', ['email_address'], unique=False, if_not_exists=True)
    op.create_index(op.f('ix_user_email_tokens_id'), 'user_email_tokens', ['id'], unique=False, if_not_exists=True)
    op.create_index(op.f('ix_user_email_tokens_organization_id'), 'user_email_tokens', ['organization_id'], unique=False, if_not_exists=True)
    op.create_index(op.f('ix_user_email_tokens_user_id'), 'user_email_tokens', ['user_id'], unique=False, if_not_exists=True)
    # ### end Alembic commands ###


def downgrade():
    # Drop indexes (Alembic handles if_exists internally for drop_index)
    op.drop_index(op.f('ix_user_email_tokens_user_id'), table_name='user_email_tokens', if_exists=True)
    op.drop_index(op.f('ix_user_email_tokens_organization_id'), table_name='user_email_tokens', if_exists=True)
    op.drop_index(op.f('ix_user_email_tokens_id'), table_name='user_email_tokens', if_exists=True)
    op.drop_index(op.f('ix_user_email_tokens_email_address'), table_name='user_email_tokens', if_exists=True)
    
    # Conditional drop for user_email_tokens table
    op.execute("DROP TABLE IF EXISTS user_email_tokens")
    
    op.drop_index(op.f('ix_oauth_states_user_id'), table_name='oauth_states', if_exists=True)
    op.drop_index(op.f('ix_oauth_states_state'), table_name='oauth_states', if_exists=True)
    op.drop_index(op.f('ix_oauth_states_organization_id'), table_name='oauth_states', if_exists=True)
    op.drop_index(op.f('ix_oauth_states_id'), table_name='oauth_states', if_exists=True)
    
    # Conditional drop for oauth_states table
    op.execute("DROP TABLE IF EXISTS oauth_states")
    
    # Drop ENUM types if needed (caution: only if no dependencies)
    op.execute("DROP TYPE IF EXISTS tokenstatus")
    op.execute("DROP TYPE IF EXISTS oauthprovider")
    # ### end Alembic commands ###