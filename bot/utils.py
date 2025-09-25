def escape_md(text: str) -> str:
    """
    Экранирует спецсимволы для MarkdownV2 Telegram.
    """
    for c in r"\_*[]()~`>#+-=|{}.!":
        text = text.replace(c, '\\' + c)
    return text