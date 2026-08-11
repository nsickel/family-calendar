"""Provision a new family (and its members) in one transaction.

Usage:
    python -m scripts.create_family --name "Sickel Family" --username sickels \
        --member "svenja:Svenja:👩:#FF6B9D" \
        --member "nils:Nils:👨:#4ECDC4" \
        --member "emelie:Emelie:👧:#FF6B9D"

This is the only supported way to create a family — there is no public
self-service signup, by design (see infra/README.md and root CLAUDE.md).
"""
import argparse
import getpass
import sys

from sqlalchemy import select

from auth.hashing import hash_password
from db import engine, families_table, family_members_table


def parse_member(spec: str) -> dict:
    parts = spec.split(":")
    if len(parts) != 4:
        raise argparse.ArgumentTypeError(
            f"--member must be 'slug:name:emoji:color', got: {spec!r}"
        )
    slug, name, emoji, color = parts
    return {"slug": slug, "name": name, "emoji": emoji, "color": color}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--name", required=True, help="Display name for the family, e.g. 'Sickel Family'")
    parser.add_argument("--username", required=True, help="Login username (must be unique)")
    parser.add_argument("--password", help="Login password (omit to be prompted, recommended)")
    parser.add_argument(
        "--member",
        action="append",
        dest="members",
        type=parse_member,
        required=True,
        help="A family member as 'slug:name:emoji:color'. Repeat for each member.",
    )
    args = parser.parse_args()

    password = args.password
    if not password:
        password = getpass.getpass("Password: ")
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Passwords do not match.", file=sys.stderr)
            sys.exit(1)

    with engine.connect() as conn:
        existing = conn.execute(
            select(families_table.c.id).where(families_table.c.username == args.username)
        ).first()
    if existing is not None:
        print(f"Username {args.username!r} is already taken.", file=sys.stderr)
        sys.exit(1)

    password_hash = hash_password(password)

    with engine.begin() as conn:
        family_id = conn.execute(
            families_table.insert()
            .values(name=args.name, username=args.username, password_hash=password_hash)
            .returning(families_table.c.id)
        ).scalar_one()

        member_ids = conn.execute(
            family_members_table.insert()
            .values(
                [
                    {
                        "family_id": family_id,
                        "slug": m["slug"],
                        "name": m["name"],
                        "emoji": m["emoji"],
                        "color": m["color"],
                        "sort_order": i,
                    }
                    for i, m in enumerate(args.members)
                ]
            )
            .returning(family_members_table.c.id, family_members_table.c.slug)
        ).all()

    print(f"Created family {args.name!r} (id={family_id})")
    for member_id, slug in member_ids:
        print(f"  - {slug}: {member_id}")


if __name__ == "__main__":
    main()
