"""empty message

Revision ID: 6c5b98761104
Revises: 20998baa3cbc
Create Date: 2022-04-12 16:29:16.151600

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6c5b98761104'
down_revision = '20998baa3cbc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('subscription_statistics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('gross_subs_year', sa.Integer(), nullable=True),
    sa.Column('gross_subs_month', sa.Integer(), nullable=True),
    sa.Column('new_subs_year', sa.Integer(), nullable=True),
    sa.Column('new_subs_month', sa.Integer(), nullable=True),
    sa.Column('canceled_subs_year', sa.Integer(), nullable=True),
    sa.Column('canceled_subs_month', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('subscription_statistics')
    # ### end Alembic commands ###
