def add_article(word):
    """Adds 'a' or 'an' prefix to a word based on its starting letter."""
    if not word:
        return ""
    if word.lower().startswith(('a', 'e', 'i', 'o', 'u')):
        return f"an {word}"
    return f"a {word}"
