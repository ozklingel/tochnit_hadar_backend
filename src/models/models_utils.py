from datetime import datetime

def get_foreign_key_source(table, col=""):
    return f"{table}.{col}"


def to_iso(d):
    if d:
        return datetime(d.year, d.month, d.day).isoformat()
    else:
        return None