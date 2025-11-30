import phonenumbers

def to_e164(raw, region="US"):
    try:
        p = phonenumbers.parse(raw, region)
        if phonenumbers.is_possible_number(p) and phonenumbers.is_valid_number(p):
            return phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        return None
    return None