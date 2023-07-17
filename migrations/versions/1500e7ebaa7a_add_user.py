"""add user

Revision ID: 1500e7ebaa7a
Revises: c17f02e1874b
Create Date: 2023-07-15 00:36:34.356055

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1500e7ebaa7a'
down_revision = 'c17f02e1874b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=True),
    sa.Column('email', sa.String(length=150), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('refresh_token', sa.String(length=255), nullable=True),
    sa.Column('avatar', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    # ### end Alembic commands ###
