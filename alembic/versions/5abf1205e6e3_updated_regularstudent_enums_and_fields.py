"""Updated RegularStudent enums and fields

Revision ID: 5abf1205e6e3
Revises: 135534ab5699
Create Date: 2025-06-18 16:56:32.989702

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5abf1205e6e3'
down_revision: Union[str, None] = '135534ab5699'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create the new ENUM type
    marital_status_enum = sa.Enum('single', 'married', 'widowed', 'divorced', name='maritalstatusenum')
    marital_status_enum.create(op.get_bind(), checkfirst=True)

    # Alter the column to use the new ENUM type
    op.execute("""
        ALTER TABLE regular_students 
        ALTER COLUMN marital_status 
        TYPE maritalstatusenum 
        USING marital_status::text::maritalstatusenum
    """)

    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # Revert the ENUM to VARCHAR
    op.execute("""
        ALTER TABLE regular_students 
        ALTER COLUMN marital_status 
        TYPE VARCHAR 
        USING marital_status::text
    """)

    # Drop the ENUM type if exists
    op.execute("DROP TYPE IF EXISTS maritalstatusenum")

    # ### end Alembic commands ###
