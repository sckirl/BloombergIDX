import json
from .database import SessionLocal
from .models import Entity
from .logger import logger

def seed_entities():
    db = SessionLocal()
    entities = [
        {
            "canonical_name": "Jahja Setiaatmadja",
            "name_variants": json.dumps(["Jahja Setiaatmadja", "Setiaatmadja, Jahja"]),
            "entity_type": "PERSON",
            "pep_flag": True,
            "related_entities": json.dumps(["BCA", "BBCA"]),
            "notes": "President Director of PT Bank Central Asia Tbk."
        },
        {
            "canonical_name": "Patrick Sugito Walujo",
            "name_variants": json.dumps(["Patrick Walujo", "Patrick Sugito Walujo"]),
            "entity_type": "PERSON",
            "pep_flag": True,
            "related_entities": json.dumps(["GOTO", "Northstar Group"]),
            "notes": "CEO of GoTo."
        },
        {
            "canonical_name": "Northstar Group",
            "entity_type": "CORP",
            "pep_flag": False,
            "related_entities": json.dumps(["Patrick Sugito Walujo", "GOTO"]),
            "notes": "Private equity firm."
        }
    ]

    try:
        for ent_data in entities:
            existing = db.query(Entity).filter(Entity.canonical_name == ent_data["canonical_name"]).first()
            if not existing:
                entity = Entity(**ent_data)
                db.add(entity)
                logger.info(f"Seeded Entity: {ent_data['canonical_name']}")
        db.commit()
    except Exception as e:
        logger.error(f"Error seeding entities: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_entities()
