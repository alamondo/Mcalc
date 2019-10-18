"""money update

Revision ID: b39037fe1f89
Revises: 2618540ddca9
Create Date: 2019-10-18 22:51:17.731079

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b39037fe1f89'
down_revision = '2618540ddca9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('income2',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('value', sa.Float(), nullable=True),
    sa.Column('note', sa.String(length=150), nullable=True),
    sa.Column('category', sa.String(length=150), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_income2_timestamp'), 'income2', ['timestamp'], unique=False)
    op.add_column('income', sa.Column('category', sa.String(length=150), nullable=True))
    op.add_column('spending', sa.Column('category', sa.String(length=150), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('spending', 'category')
    op.drop_column('income', 'category')
    op.drop_index(op.f('ix_income2_timestamp'), table_name='income2')
    op.drop_table('income2')
    # ### end Alembic commands ###
