"""Initial schema with core models

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=False, default={}),
        sa.Column('timezone', sa.String(50), nullable=False, default='America/Mexico_City'),
        sa.Column('telegram_chat_id', sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('telegram_chat_id')
    )
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_email', 'users', ['email'])

    # Create characters table
    op.create_table(
        'characters',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('character_class', sa.String(20), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False, default=1),
        sa.Column('experience', sa.Integer(), nullable=False, default=0),
        sa.Column('experience_to_next', sa.Integer(), nullable=False, default=100),
        sa.Column('health_current', sa.Integer(), nullable=False, default=100),
        sa.Column('health_max', sa.Integer(), nullable=False, default=100),
        sa.Column('mana_current', sa.Integer(), nullable=False, default=100),
        sa.Column('mana_max', sa.Integer(), nullable=False, default=100),
        sa.Column('energy_current', sa.Integer(), nullable=False, default=0),
        sa.Column('energy_max', sa.Integer(), nullable=False, default=100),
        sa.Column('gold', sa.Integer(), nullable=False, default=0),
        sa.Column('gems', sa.Integer(), nullable=False, default=0),
        sa.Column('streak_days', sa.Integer(), nullable=False, default=0),
        sa.Column('total_tasks_completed', sa.Integer(), nullable=False, default=0),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('title', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_daily_reset', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id'),
        sa.CheckConstraint("character_class IN ('warrior', 'mage', 'rogue', 'healer')", name='valid_class'),
        sa.CheckConstraint('health_current >= 0 AND health_current <= health_max', name='health_valid'),
        sa.CheckConstraint('mana_current >= 0 AND mana_current <= mana_max', name='mana_valid'),
        sa.CheckConstraint('energy_current >= 0 AND energy_current <= energy_max', name='energy_valid'),
        sa.CheckConstraint('level >= 1', name='level_valid'),
        sa.CheckConstraint('experience >= 0', name='experience_valid'),
        sa.CheckConstraint('gold >= 0', name='gold_valid'),
        sa.CheckConstraint('gems >= 0', name='gems_valid'),
    )
    op.create_index('idx_characters_user', 'characters', ['user_id'])

    # Create task type enum
    task_type = postgresql.ENUM('daily', 'todo', 'habit', name='tasktype')
    task_type.create(op.get_bind())

    # Create task difficulty enum
    task_difficulty = postgresql.ENUM('trivial', 'easy', 'medium', 'hard', name='taskdifficulty')
    task_difficulty.create(op.get_bind())

    # Create ritual time enum
    ritual_time = postgresql.ENUM('morning', 'afternoon', 'evening', name='ritualtime')
    ritual_time.create(op.get_bind())

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('task_type', sa.Enum('daily', 'todo', 'habit', name='tasktype'), nullable=False),
        sa.Column('difficulty', sa.Enum('trivial', 'easy', 'medium', 'hard', name='taskdifficulty'), nullable=False),
        sa.Column('experience_reward', sa.Integer(), nullable=False),
        sa.Column('gold_reward', sa.Integer(), nullable=False, default=0),
        sa.Column('mana_reward', sa.Integer(), nullable=False, default=0),
        sa.Column('energy_reward', sa.Integer(), nullable=False, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('repeat_days', postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column('ritual_time', sa.Enum('morning', 'afternoon', 'evening', name='ritualtime'), nullable=True),
        sa.Column('is_positive', sa.Boolean(), nullable=True, default=True),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('dice_weight', sa.Integer(), nullable=False, default=1),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=False, default=[]),
        sa.Column('notes', postgresql.JSONB(astext_type=sa.Text()), nullable=False, default={}),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_tasks_character', 'tasks', ['character_id'])
    op.create_index('idx_tasks_type', 'tasks', ['task_type'])
    op.create_index('idx_tasks_active', 'tasks', ['is_active'], postgresql_where=sa.text('is_active = true'))

    # Create task_completions table
    op.create_table(
        'task_completions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('experience_gained', sa.Integer(), nullable=False),
        sa.Column('gold_gained', sa.Integer(), nullable=False, default=0),
        sa.Column('mana_gained', sa.Integer(), nullable=False, default=0),
        sa.Column('energy_gained', sa.Integer(), nullable=False, default=0),
        sa.Column('streak_at_completion', sa.Integer(), nullable=True),
        sa.Column('level_at_completion', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_task_completions_task', 'task_completions', ['task_id'])
    op.create_index('idx_task_completions_date', 'task_completions', ['completed_at'])

    # Create daily_stats table
    op.create_table(
        'daily_stats',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('tasks_completed', sa.Integer(), nullable=False, default=0),
        sa.Column('rituals_completed', sa.Integer(), nullable=False, default=0),
        sa.Column('abilities_used', sa.Integer(), nullable=False, default=0),
        sa.Column('experience_gained', sa.Integer(), nullable=False, default=0),
        sa.Column('gold_earned', sa.Integer(), nullable=False, default=0),
        sa.Column('health_lost', sa.Integer(), nullable=False, default=0),
        sa.Column('health_restored', sa.Integer(), nullable=False, default=0),
        sa.Column('active_time_minutes', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('character_id', 'date', name='unique_character_date'),
    )
    op.create_index('idx_daily_stats_character_date', 'daily_stats', ['character_id', 'date'])

    # Create XP calculation function
    op.execute("""
        CREATE OR REPLACE FUNCTION calculate_exp_to_next(current_level INTEGER)
        RETURNS INTEGER AS $$
        BEGIN
            RETURN FLOOR(100 * POWER(1.1, current_level - 1));
        END;
        $$ LANGUAGE plpgsql IMMUTABLE;
    """)

    # Create auto level-up trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION check_level_up()
        RETURNS TRIGGER AS $$
        BEGIN
            WHILE NEW.experience >= NEW.experience_to_next LOOP
                NEW.experience := NEW.experience - NEW.experience_to_next;
                NEW.level := NEW.level + 1;
                NEW.experience_to_next := calculate_exp_to_next(NEW.level);

                -- Increase max stats on level up
                NEW.health_max := NEW.health_max + 5;
                NEW.mana_max := NEW.mana_max + 5;
                NEW.health_current := NEW.health_max;  -- Full restore on level up
                NEW.mana_current := NEW.mana_max;
            END LOOP;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create level-up trigger
    op.execute("""
        CREATE TRIGGER trigger_level_up
        BEFORE UPDATE OF experience ON characters
        FOR EACH ROW
        EXECUTE FUNCTION check_level_up();
    """)

    # Create daily stats update trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION update_daily_stats()
        RETURNS TRIGGER AS $$
        BEGIN
            INSERT INTO daily_stats (id, character_id, date, tasks_completed, experience_gained, gold_earned, created_at)
            VALUES (
                gen_random_uuid(),
                NEW.character_id,
                CURRENT_DATE,
                1,
                NEW.experience_gained,
                NEW.gold_gained,
                NOW()
            )
            ON CONFLICT (character_id, date)
            DO UPDATE SET
                tasks_completed = daily_stats.tasks_completed + 1,
                experience_gained = daily_stats.experience_gained + NEW.experience_gained,
                gold_earned = daily_stats.gold_earned + NEW.gold_gained;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create daily stats trigger
    op.execute("""
        CREATE TRIGGER trigger_update_daily_stats
        AFTER INSERT ON task_completions
        FOR EACH ROW
        EXECUTE FUNCTION update_daily_stats();
    """)


def downgrade() -> None:
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS trigger_update_daily_stats ON task_completions")
    op.execute("DROP TRIGGER IF EXISTS trigger_level_up ON characters")

    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS update_daily_stats()")
    op.execute("DROP FUNCTION IF EXISTS check_level_up()")
    op.execute("DROP FUNCTION IF EXISTS calculate_exp_to_next(INTEGER)")

    # Drop tables
    op.drop_table('daily_stats')
    op.drop_table('task_completions')
    op.drop_table('tasks')
    op.drop_table('characters')
    op.drop_table('users')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS ritualtime")
    op.execute("DROP TYPE IF EXISTS taskdifficulty")
    op.execute("DROP TYPE IF EXISTS tasktype")
