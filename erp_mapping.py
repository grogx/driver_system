# =========================
# ERP FIELD MAPPING
# =========================

MAP_DRIVERS = {
    "id": "id",
    "name": "full_name",
    "phone": "phone",
    "med_expiry": "med_expiry"  # Python → Python ключ
}

def to_1c_driver(d):
    return {
        "id": d.get("id"),
        "name": d.get("name"),
        "phone": d.get("phone"),
        "med_expiry": d.get("med_expiry")
    }


def from_1c_driver(d):
    return {
        "id": d.get("id"),
        "name": d.get("name"),
        "phone": d.get("phone"),
        "med_expiry": d.get("med_expiry")
    }