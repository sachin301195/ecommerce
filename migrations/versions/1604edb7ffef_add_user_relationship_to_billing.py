"""Add user relationship to Billing

Revision ID: 1604edb7ffef
Revises: 5db645305235
Create Date: 2025-02-16 17:42:58.310062

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1604edb7ffef'
down_revision = '5db645305235'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bill_details', schema=None) as batch_op:
        batch_op.alter_column('Bill_Details_ID',
               existing_type=sa.INTEGER(),
               nullable=False,
               autoincrement=True)

    with op.batch_alter_table('billing', schema=None) as batch_op:
        batch_op.alter_column('Billing_ID',
               existing_type=sa.INTEGER(),
               nullable=False,
               autoincrement=True)
        batch_op.create_foreign_key("fk_billing_user", 'user', ['Client_ID'], ['id'])
        batch_op.create_foreign_key("fk_billing_hst", 'hst', ['HST_ID'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('billing', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('Billing_ID',
               existing_type=sa.INTEGER(),
               nullable=True,
               autoincrement=True)

    with op.batch_alter_table('bill_details', schema=None) as batch_op:
        batch_op.alter_column('Bill_Details_ID',
               existing_type=sa.INTEGER(),
               nullable=True,
               autoincrement=True)

    # ### end Alembic commands ###
