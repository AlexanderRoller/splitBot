def format_response(title, lines, footer=None):
    message = f"**{title}**"
    for line in lines:
        message += f"\n- {line}"
    if footer:
        message += f"\n{footer}"
    return message


def format_error(action, detail):
    message = f"**{action} Error**"
    if detail:
        message += f"\n- {detail}"
    return message
