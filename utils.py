import re

def clean_html(text: str) -> str:
    """
    Удаляет неподдерживаемые HTML-теги и форматирует списки.
    """
    # Заменяем <ul><li> списки на простые строки с буллетами
    text = re.sub(r'<ul>\s*', '', text)
    text = re.sub(r'</ul>', '', text)
    text = re.sub(r'<li>', '• ', text)
    text = re.sub(r'</li>', '\n', text)

    # Заменяем <p> на переносы строк
    text = text.replace('<p>', '').replace('</p>', '\n\n')

    # Удаляем другие неподдерживаемые теги
    text = re.sub(r'</?(h[1-6]|ol|div|span|br|table|tr|td|th|blockquote|hr)[^>]*>', '', text)

    return text.strip()
