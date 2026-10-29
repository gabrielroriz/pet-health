"""Create users, pets, hospitals, veterinarians and appointments

Revision ID: 0001
Revises:
Create Date: 2026-10-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Lets one GiST index combine "=" on UUIDs with "&&" on time ranges.
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")

    # One row per user; logging in with the same email finds the same row.
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )
    # Each pet belongs to one user, and its species must be a known value.
    op.create_table(
        "pets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("species", sa.String(length=20), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("breed", sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_pets")),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], name=op.f("fk_pets_owner_id_users")),
        sa.CheckConstraint(
            "species IN ('dog', 'cat', 'bird', 'rabbit', 'other')", name=op.f("ck_pets_species")
        ),
    )
    op.create_index(op.f("ix_pets_owner_id"), "pets", ["owner_id"])

    # Networks group hospitals; their names are unique.
    op.create_table(
        "hospital_networks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_hospital_networks")),
        sa.UniqueConstraint("name", name=op.f("uq_hospital_networks_name")),
    )
    # A nullable network_id: a hospital belongs to at most one network.
    op.create_table(
        "hospitals",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("network_id", sa.Uuid(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_hospitals")),
        sa.ForeignKeyConstraint(
            ["network_id"],
            ["hospital_networks.id"],
            name=op.f("fk_hospitals_network_id_hospital_networks"),
        ),
    )
    op.create_index(op.f("ix_hospitals_network_id"), "hospitals", ["network_id"])

    # agenda_version is double-booking layer 2 (optimistic lock): every booking bumps it.
    op.create_table(
        "veterinarians",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("agenda_version", sa.Integer(), server_default="0", nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_veterinarians")),
    )
    # Which veterinarians work at which hospitals (many-to-many).
    op.create_table(
        "hospital_veterinarians",
        sa.Column("hospital_id", sa.Uuid(), nullable=False),
        sa.Column("veterinarian_id", sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint(
            "hospital_id", "veterinarian_id", name=op.f("pk_hospital_veterinarians")
        ),
        sa.ForeignKeyConstraint(
            ["hospital_id"],
            ["hospitals.id"],
            name=op.f("fk_hospital_veterinarians_hospital_id_hospitals"),
        ),
        sa.ForeignKeyConstraint(
            ["veterinarian_id"],
            ["veterinarians.id"],
            name=op.f("fk_hospital_veterinarians_veterinarian_id_veterinarians"),
        ),
    )
    op.create_index(
        op.f("ix_hospital_veterinarians_veterinarian_id"),
        "hospital_veterinarians",
        ["veterinarian_id"],
    )

    # Who booked, for which pet, at which hospital, with whom, and when.
    op.create_table(
        "appointments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("pet_id", sa.Uuid(), nullable=False),
        sa.Column("hospital_id", sa.Uuid(), nullable=False),
        sa.Column("veterinarian_id", sa.Uuid(), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_appointments")),
        sa.ForeignKeyConstraint(
            ["owner_id"], ["users.id"], name=op.f("fk_appointments_owner_id_users")
        ),
        sa.ForeignKeyConstraint(["pet_id"], ["pets.id"], name=op.f("fk_appointments_pet_id_pets")),
        # The veterinarian must work at the hospital of the appointment.
        sa.ForeignKeyConstraint(
            ["hospital_id", "veterinarian_id"],
            ["hospital_veterinarians.hospital_id", "hospital_veterinarians.veterinarian_id"],
            name=op.f("fk_appointments_hospital_id_hospital_veterinarians"),
        ),
        sa.CheckConstraint("ends_at > starts_at", name=op.f("ck_appointments_ends_after_start")),
        sa.CheckConstraint(
            "status IN ('scheduled', 'cancelled')", name=op.f("ck_appointments_status")
        ),
    )
    op.create_index(op.f("ix_appointments_owner_id"), "appointments", ["owner_id"])

    # Double-booking layer 3: the database itself refuses overlaps, whatever the code does.
    # No two scheduled appointments may overlap for the same veterinarian or the same
    # pet. tstzrange defaults to '[)' bounds, so back-to-back appointments are allowed.
    op.execute(
        """
        ALTER TABLE appointments
        ADD CONSTRAINT ex_appointments_veterinarian_overlap
        EXCLUDE USING gist (veterinarian_id WITH =, tstzrange(starts_at, ends_at) WITH &&)
        WHERE (status = 'scheduled')
        """
    )
    op.execute(
        """
        ALTER TABLE appointments
        ADD CONSTRAINT ex_appointments_pet_overlap
        EXCLUDE USING gist (pet_id WITH =, tstzrange(starts_at, ends_at) WITH &&)
        WHERE (status = 'scheduled')
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop in reverse order so no foreign key points at a missing table.
    op.drop_table("appointments")
    op.drop_table("hospital_veterinarians")
    op.drop_table("veterinarians")
    op.drop_table("hospitals")
    op.drop_table("hospital_networks")
    op.drop_table("pets")
    op.drop_table("users")
    op.execute("DROP EXTENSION IF EXISTS btree_gist")
