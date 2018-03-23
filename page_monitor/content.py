from typing import List

from requests_html import HTMLSession, HTMLResponse, Element


def get_content(url: str, css_selector: str, first_only: bool = False,
                render: bool = False) -> List[Element]:
    session = HTMLSession()
    response: HTMLResponse = session.get(url)

    if render:
        response.html.render()

    html = response.html
    content = html.find(css_selector, first=first_only, clean=True)

    if not isinstance(content, list):
        content = [content]

    return content
