from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    MetaData,
    String,
    Table,
    Uuid,
    column,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import ExcludeConstraint

# Gives every constraint and index a predictable name, matching the migrations.
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

# One row per user; the email is unique.
users = Table(
    "users",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("email", String(320), nullable=False, unique=True),
)

# Each pet belongs to one user; its species must be a Species value.
pets = Table(
    "pets",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("owner_id", Uuid, ForeignKey("users.id"), nullable=False, index=True),
    Column("name", String(100), nullable=False),
    Column("species", String(20), nullable=False),
    Column("birth_date", Date),
    Column("breed", String(100)),
    CheckConstraint("species IN ('dog', 'cat', 'bird', 'rabbit', 'other')", name="species"),
)

# Networks group hospitals; their names are unique.
hospital_networks = Table(
    "hospital_networks",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("name", String(200), nullable=False, unique=True),
)

# Hospitals, each optionally part of one network.
hospitals = Table(
    "hospitals",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("name", String(200), nullable=False),
    # A hospital belongs to at most one network.
    Column("network_id", Uuid, ForeignKey("hospital_networks.id"), index=True),
)

# Veterinarians, with the version that guards their agenda.
veterinarians = Table(
    "veterinarians",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("name", String(200), nullable=False),
    # Double-booking layer 2 (optimistic lock): every booking with this veterinarian bumps it.
    Column("agenda_version", Integer, nullable=False, server_default="0"),
)

# Which veterinarians work at which hospitals (many-to-many).
hospital_veterinarians = Table(
    "hospital_veterinarians",
    metadata,
    Column("hospital_id", Uuid, ForeignKey("hospitals.id"), primary_key=True),
    Column("veterinarian_id", Uuid, ForeignKey("veterinarians.id"), primary_key=True, index=True),
)


def _no_overlap(column_name: str, name: str) -> ExcludeConstraint:
    # Default tstzrange bounds are '[)', so one appointment may start exactly when
    # another ends. Cancelled appointments don't hold their slot.
    return ExcludeConstraint(
        (column(column_name), "="),
        (func.tstzrange(column("starts_at"), column("ends_at")), "&&"),
        name=name,
        using="gist",
        where=text("status = 'scheduled'"),
    )


# Who booked, for which pet, at which hospital, with whom, and when.
appointments = Table(
    "appointments",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("owner_id", Uuid, ForeignKey("users.id"), nullable=False, index=True),
    Column("pet_id", Uuid, ForeignKey("pets.id"), nullable=False),
    Column("hospital_id", Uuid, nullable=False),
    Column("veterinarian_id", Uuid, nullable=False),
    Column("starts_at", DateTime(timezone=True), nullable=False),
    # Stored rather than derived, so the exclusion constraints can build a time range.
    Column("ends_at", DateTime(timezone=True), nullable=False),
    Column("reason", String(500), nullable=False),
    Column("status", String(20), nullable=False),
    # The veterinarian must work at the hospital of the appointment.
    ForeignKeyConstraint(
        ["hospital_id", "veterinarian_id"],
        ["hospital_veterinarians.hospital_id", "hospital_veterinarians.veterinarian_id"],
    ),
    CheckConstraint("ends_at > starts_at", name="ends_after_start"),
    # Only scheduled appointments hold a slot; cancelled ones are history.
    CheckConstraint("status IN ('scheduled', 'cancelled')", name="status"),
    # Double-booking layer 3: no vet and no pet can have two overlapping scheduled appointments.
    _no_overlap("veterinarian_id", "ex_appointments_veterinarian_overlap"),
    _no_overlap("pet_id", "ex_appointments_pet_overlap"),
)
