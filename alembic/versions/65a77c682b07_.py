"""empty message

Revision ID: 65a77c682b07
Revises: bc350dbb9fcb
Create Date: 2022-11-23 12:35:41.205619

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '65a77c682b07'
down_revision = 'bc350dbb9fcb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('subscription_statistics', sa.Column('gross_subs_lifetime', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('subscription_statistics', 'gross_subs_lifetime')
    # ### end Alembic commands ###
