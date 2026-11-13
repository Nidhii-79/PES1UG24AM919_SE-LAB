# Lab 7 - Name: Nidhi | SRN: PES1UG24AM919

def mask_imei(imei):
    """
    Removes dashes and spaces, then hides all but the last four digits.
    Returns '' for None / non-string input. Values of four characters or
    fewer are fully masked so nothing short is ever shown in the clear.
    """
    if not isinstance(imei, str):
        return ''
    imei = imei.replace('-', '').replace(' ', '')
    if len(imei) <= 4:
        return '*' * len(imei)
    return '*' * (len(imei) - 4) + imei[-4:]


def parse_parts_order(text):
    """
    Parses 'screen x1; battery x2' into a {part: quantity} dictionary.
    Malformed items (no 'x', empty part, non-numeric or non-positive
    quantity) are skipped instead of crashing. None / non-string -> {}.
    """
    order = {}
    if not isinstance(text, str):
        return order
    for item in text.split(';'):
        if 'x' not in item:
            continue
        # split on the LAST 'x' so part names containing 'x' (e.g. 'mixer') work
        part, qty = item.rsplit('x', 1)
        part = part.strip()
        qty = qty.strip()
        if not part or not qty.isascii() or not qty.isdigit():
            continue
        quantity = int(qty)
        if quantity <= 0:
            continue
        order[part] = quantity
    return order


def parse_model(text):
    """
    Splits 'Brand Model name' into a (brand, model) tuple.
    One word -> (brand, ''); empty / None / non-string -> ('', '').
    """
    if not isinstance(text, str):
        return '', ''
    parts = text.strip().split(None, 1)   # any whitespace, at most one split
    if not parts:
        return '', ''
    brand = parts[0].title()
    model = parts[1].strip() if len(parts) > 1 else ''
    return brand, model


def main():
    print("==== Running mask_imei ====")
    value = input("Enter an IMEI number (e.g. 35-209900-176148-1): ")
    print("Masked IMEI:", mask_imei(value))

    print("\n==== Running parse_parts_order ====")
    value = input("Enter parts and quantities as PART xQTY separated by ; (e.g. screen x1; battery x2): ")
    print("Parts order:", parse_parts_order(value))

    print("\n==== Running parse_model ====")
    value = input("Enter the phone brand and model (e.g. Samsung Galaxy S23): ")
    print("Brand and model:", parse_model(value))

if __name__ == "__main__":
    main()
