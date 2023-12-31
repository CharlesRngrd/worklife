"""update employee table

Revision ID: 9b69732bce67
Revises: 27bf2aa3b8c7
Create Date: 2023-09-09 14:18:34.342661

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b69732bce67'
down_revision = '27bf2aa3b8c7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('employee', 'first_name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('employee', 'last_name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('employee', 'last_name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('employee', 'first_name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###
