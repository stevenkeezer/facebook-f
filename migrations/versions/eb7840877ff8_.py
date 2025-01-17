"""empty message

Revision ID: eb7840877ff8
Revises: 6165f97c6c30
Create Date: 2019-11-18 15:58:03.286163

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb7840877ff8'
down_revision = '6165f97c6c30'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False))
    op.drop_column('users', 'admin')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('admin', sa.BOOLEAN(), nullable=True))
    op.drop_column('users', 'is_admin')
    # ### end Alembic commands ###
