"""empty message

Revision ID: 6165f97c6c30
Revises: ab798780dbc8
Create Date: 2019-11-18 15:51:35.692812

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6165f97c6c30'
down_revision = 'ab798780dbc8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('admin', sa.Boolean(create_constraint=False), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'admin')
    # ### end Alembic commands ###