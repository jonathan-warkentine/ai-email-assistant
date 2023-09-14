def generate_string_output(friendly_slots):
    lines = []

    for date, slots in friendly_slots.items():
        lines.append(f"{date}:")
        for slot in slots:
            lines.append(f"  • {slot}")

    return "\n".join(lines)