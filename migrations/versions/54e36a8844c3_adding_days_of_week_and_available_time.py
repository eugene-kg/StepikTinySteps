"""Adding days_of_week and available time

Revision ID: 54e36a8844c3
Revises: 444665008725
Create Date: 2020-02-23 00:46:53.239285

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '54e36a8844c3'
down_revision = '444665008725'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dic_available_time',
    sa.Column('time_key', sa.String(length=10), nullable=False),
    sa.Column('rus_name', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('time_key')
    )
    op.create_table('dic_days_of_week',
    sa.Column('weekday_key', sa.String(length=3), nullable=False),
    sa.Column('rus_name', sa.String(length=50), nullable=True),
    sa.Column('rus_short_name', sa.String(length=2), nullable=True),
    sa.PrimaryKeyConstraint('weekday_key')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('dic_days_of_week')
    op.drop_table('dic_available_time')
    # ### end Alembic commands ###
