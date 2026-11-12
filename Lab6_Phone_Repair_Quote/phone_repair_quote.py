PART_COST = {"screen": 4000, "battery": 1500, "camera": 2500, "charging_port": 800}


def repair_quote(part, brand_tier, under_warranty, express):
    if part not in PART_COST:
        raise ValueError("unknown part")
    if brand_tier not in ("budget", "flagship"):
        raise ValueError("unknown brand tier")
    cost = PART_COST[part]
    if brand_tier == "flagship":
        cost = cost * 2
    if part == "screen":
        labour = 600
    else:
        labour = 300
    if under_warranty and part != "screen":
        cost = 0
    total = cost + labour
    if express:
        total += 500
    return total


def repair_days(part, parts_in_stock, technicians_free):
    if technicians_free == 0:
        days = 3
    else:
        days = 1
    if not parts_in_stock:
        if part == "screen" or part == "camera":
            days += 5
        else:
            days += 2
    return days


def trade_in_value(original_price, age_months, screen_cracked):
    if original_price <= 0 or age_months < 0:
        raise ValueError("invalid input")
    if age_months > 48:
        return 0
    if age_months <= 12:
        value = original_price * 60 // 100
    elif age_months <= 24:
        value = original_price * 40 // 100
    else:
        value = original_price * 20 // 100
    if screen_cracked:
        value = value // 2
    return value
