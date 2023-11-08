from mistune import (
    create_markdown as mistune_create_markdown, escape, HTMLRenderer
)

from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.token import Error
from pygments.styles.default import DefaultStyle


class DefaultStyleExtended(DefaultStyle):
    """
        A class that extends the default Pygments style.
        Removes the red color from the Error token.
    """
    
    styles = DefaultStyle.styles.copy()
    styles.update({ Error: '#000' })

class HighlightRenderer(HTMLRenderer):
    """
        A custom renderer that highlights code blocks.
    """
    
    def block_code(self, code, info=None):
        """
            Renders a code block with syntax highlighting.
        """
        
        if not info:
            # Wrapping it in a code block:
            return '<pre><code>' + escape(code) + '</code></pre>'
        
        lexer = get_lexer_by_name(info, stripall=True)
        formatter = HtmlFormatter(style=DefaultStyleExtended, full=True)
        
        highlighted_code: str = highlight(code, lexer, formatter)
        
        # TODO: Abstract away the CSS classes into a modular system.
        return f'<div class="code-border no-underline-heading">{highlighted_code}</div>'
    
def create_markdown(fragment: str, remove_newlines: bool = False) -> str:
    """
        Creates a Markdown parser with syntax highlighting.
    """
    
    markdown: str = mistune_create_markdown(renderer=HighlightRenderer())(fragment)
    
    return markdown.replace("\n", "") if remove_newlines else markdown