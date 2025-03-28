"""add role to user

Revision ID: 9761bc1b5ba2
Revises: 786083ed462c
Create Date: 2024-11-29 22:16:26.674655

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.models.user_model import Role

# revision identifiers, used by Alembic.
revision: str = "9761bc1b5ba2"
down_revision: Union[str, None] = "786083ed462c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    role = sa.Enum(Role, name="role")
    role.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "user", sa.Column("role", sa.Enum("USER", "ADMIN", name="role"), server_default="USER", nullable=False)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user", "role")
    op.execute("DROP TYPE role;")
    # ### end Alembic commands ###
