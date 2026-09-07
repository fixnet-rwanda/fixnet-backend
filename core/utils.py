import re

PHONE_REGEX = re.compile(r"(\+?250\s?[0-9]{3}\s?[0-9]{3}\s?[0-9]{3}|07[2389][0-9]{7})")
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
URL_REGEX = re.compile(r"(https?://\S+|www\.\S+)")


def mask_contact_info(text: str) -> tuple[str, bool]:
    """
    CHAT-02: Masks phone numbers, emails, and external URLs in messages
    before a booking deposit is paid.
    Returns (masked_text, is_masked).
    """
    masked = False

    def phone_repl(match):
        nonlocal masked
        masked = True
        return "[Contact hidden until deposit paid]"

    def email_repl(match):
        nonlocal masked
        masked = True
        return "[Email hidden until deposit paid]"

    def url_repl(match):
        nonlocal masked
        masked = True
        return "[Link hidden until deposit paid]"

    result = PHONE_REGEX.sub(phone_repl, text)
    result = EMAIL_REGEX.sub(email_repl, result)
    result = URL_REGEX.sub(url_repl, result)

    return result, masked
