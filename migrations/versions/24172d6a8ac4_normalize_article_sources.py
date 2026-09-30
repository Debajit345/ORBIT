"""normalize article sources

Revision ID: 24172d6a8ac4
Revises: 6f9370578bb9
Create Date: 2026-09-30 13:28:57.434418

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "24172d6a8ac4"
down_revision: Union[str, Sequence[str], None] = "6f9370578bb9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 1. Add source_id temporarily as nullable.
    op.add_column(
        "articles",
        sa.Column(
            "source_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    # 2. Populate source_id using the existing source name.
    op.execute(
        """
        UPDATE articles
        SET source_id = sources.id
        FROM sources
        WHERE articles.source = sources.name
        """
    )

    # 3. Make sure every existing article was successfully linked.
    connection = op.get_bind()

    unmatched_count = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM articles
            WHERE source_id IS NULL
            """
        )
    ).scalar_one()

    if unmatched_count != 0:
        raise RuntimeError(
            f"{unmatched_count} article(s) could not be linked "
            "to a source."
        )

    # 4. source_id can now safely become NOT NULL.
    op.alter_column(
        "articles",
        "source_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    # 5. Replace the old unique constraint.
    op.drop_constraint(
        "uq_article_source_url",
        "articles",
        type_="unique",
    )

    op.create_unique_constraint(
        "uq_article_source_url",
        "articles",
        ["source_id", "url"],
    )

    # 6. Create the foreign key.
    op.create_foreign_key(
        "fk_articles_source_id_sources",
        "articles",
        "sources",
        ["source_id"],
        ["id"],
    )

    # 7. Remove the old string-based source column.
    op.drop_column(
        "articles",
        "source",
    )


def downgrade() -> None:
    """Downgrade schema."""

    # 1. Restore the old source column.
    op.add_column(
        "articles",
        sa.Column(
            "source",
            sa.String(length=255),
            nullable=True,
        ),
    )

    # 2. Restore source names from the Source table.
    op.execute(
        """
        UPDATE articles
        SET source = sources.name
        FROM sources
        WHERE articles.source_id = sources.id
        """
    )

    # 3. Make the restored column non-null.
    op.alter_column(
        "articles",
        "source",
        existing_type=sa.String(length=255),
        nullable=False,
    )

    # 4. Remove the new foreign key.
    op.drop_constraint(
        "fk_articles_source_id_sources",
        "articles",
        type_="foreignkey",
    )

    # 5. Remove the new unique constraint.
    op.drop_constraint(
        "uq_article_source_url",
        "articles",
        type_="unique",
    )

    # 6. Restore the old unique constraint.
    op.create_unique_constraint(
        "uq_article_source_url",
        "articles",
        ["source", "url"],
    )

    # 7. Remove source_id.
    op.drop_column(
        "articles",
        "source_id",
    )