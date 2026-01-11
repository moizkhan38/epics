"""initial migration

Revision ID: 001
Revises:
Create Date: 2026-01-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('description_embedding', Vector(384), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)

    # Create vector index for similarity search
    op.execute('''
        CREATE INDEX ix_projects_description_embedding
        ON projects USING ivfflat (description_embedding vector_cosine_ops)
        WITH (lists = 100)
    ''')

    # Create generation_histories table
    op.create_table(
        'generation_histories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('prompt_used', sa.Text(), nullable=True),
        sa.Column('model_version', sa.String(length=100), nullable=True),
        sa.Column('generation_metadata', sa.JSON(), nullable=True),
        sa.Column('similar_projects', sa.JSON(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('approved_at', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_generation_histories_id'), 'generation_histories', ['id'], unique=False)
    op.create_index(op.f('ix_generation_histories_project_id'), 'generation_histories', ['project_id'], unique=False)
    op.create_index(op.f('ix_generation_histories_status'), 'generation_histories', ['status'], unique=False)

    # Create epics table
    op.create_table(
        'epics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('generation_history_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('story_points', sa.Integer(), nullable=True),
        sa.Column('priority', sa.String(length=50), nullable=True),
        sa.Column('is_approved', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['generation_history_id'], ['generation_histories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_epics_id'), 'epics', ['id'], unique=False)
    op.create_index(op.f('ix_epics_project_id'), 'epics', ['project_id'], unique=False)
    op.create_index(op.f('ix_epics_generation_history_id'), 'epics', ['generation_history_id'], unique=False)

    # Create user_stories table
    op.create_table(
        'user_stories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('epic_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('acceptance_criteria', sa.Text(), nullable=True),
        sa.Column('story_points', sa.Integer(), nullable=True),
        sa.Column('priority', sa.String(length=50), nullable=True),
        sa.Column('is_approved', sa.Boolean(), nullable=True),
        sa.Column('test_cases', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['epic_id'], ['epics.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_stories_id'), 'user_stories', ['id'], unique=False)
    op.create_index(op.f('ix_user_stories_epic_id'), 'user_stories', ['epic_id'], unique=False)


def downgrade() -> None:
    op.drop_table('user_stories')
    op.drop_table('epics')
    op.drop_table('generation_histories')
    op.drop_table('projects')
    op.execute('DROP EXTENSION IF EXISTS vector')
