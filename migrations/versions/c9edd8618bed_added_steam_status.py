"""added steam status

Revision ID: c9edd8618bed
Revises: 2a650d3f816d
Create Date: 2021-11-01 21:02:52.273416

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9edd8618bed'
down_revision = '2a650d3f816d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('steam_status', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'steam_status')
    # ### end Alembic commands ###
