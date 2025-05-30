"""add profile fields to user model

Revision ID: d50ad74e34e9
Revises: 19813a48fc14
Create Date: 2025-04-25 03:34:39.407409

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd50ad74e34e9'
down_revision = '19813a48fc14'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('profile_picture', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('phone', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('department', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('student_id', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('year', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('faculty_id', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('office', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('office')
        batch_op.drop_column('faculty_id')
        batch_op.drop_column('year')
        batch_op.drop_column('student_id')
        batch_op.drop_column('department')
        batch_op.drop_column('phone')
        batch_op.drop_column('profile_picture')

    # ### end Alembic commands ###
