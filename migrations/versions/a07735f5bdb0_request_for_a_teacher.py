"""request for a teacher

Revision ID: a07735f5bdb0
Revises: 6a2db399aa3a
Create Date: 2020-02-24 01:25:14.647980

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a07735f5bdb0'
down_revision = '6a2db399aa3a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('requests_for_teacher',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('goal', sa.String(length=20), nullable=False),
    sa.Column('time', sa.String(length=10), nullable=False),
    sa.Column('client_name', sa.String(length=100), nullable=False),
    sa.Column('client_phone', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['goal'], ['dic_goals.goal'], ),
    sa.ForeignKeyConstraint(['time'], ['dic_available_time.time_key'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('goal', 'time', 'client_name', 'client_phone', name='client_goal_uix')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('requests_for_teacher')
    # ### end Alembic commands ###
