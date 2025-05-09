"""create resource table

Revision ID: 3c64a144a5bd
Revises: 9761bc1b5ba2
Create Date: 2024-12-01 14:06:38.204714

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3c64a144a5bd"
down_revision: Union[str, None] = "9761bc1b5ba2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "resource",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("location", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column(
            "room_type",
            sa.Enum("AUDITORIUM", "BOX", "CONFERENCE_ROOM", "DESK", "MEETING_ROOM", "OPEN_SPACE", name="roomtype"),
            nullable=False,
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_resource_name"), "resource", ["name"], unique=True)
    op.create_check_constraint("capaticy_positive", "resource", "capacity >= 0")

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("capaticy_positive", "resource", type_="check")
    op.drop_index(op.f("ix_resource_name"), table_name="resource")
    op.drop_table("resource")
    op.execute("DROP TYPE roomtype;")
    # ### end Alembic commands ###
