from mistune import (
    create_markdown as mistune_create_markdown, HTMLRenderer
)

from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.token import Error
from pygments.styles.default import DefaultStyle

from textwrap import wrap

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
            # return '<pre><code>' + escape(code) + '</code></pre>'
            info = "solidity"
        
        lexer = get_lexer_by_name(info, stripall=True)
        formatter = HtmlFormatter(style=DefaultStyleExtended, full=True)
            
        code = code.split("\n")
        for index in range(len(code)):
            code[index] = split_line_if_too_long(code[index])
        
        code = "\n".join(code)
        
        highlighted_code: str = highlight(code, lexer, formatter)
        
        # TODO: Abstract away the CSS classes into a modular system.
        return f'<div class="code-border no-underline-heading">{highlighted_code}</div>'
    
def create_html_from_markdown(fragment: str, remove_newlines: bool = False) -> str:
    """
        Creates a Markdown fragment with syntax-highlighted code blocks.
    """

    markdown: str = mistune_create_markdown(renderer=HighlightRenderer())(fragment)
    
    return markdown.replace("\n", "") if remove_newlines else markdown

def split_line_if_too_long(line: str, recursion_index: int = 0) -> str:
    if len(line) <= 80 or recursion_index > 10: return line
    
    recursion_index += 1
    
    indentation: int = len(line) - len(line.lstrip())
    
    def new_line(index0: int, index1: int, indentation: int, prefix: str = "") -> str:
        return line[:index0 + 1] + "\n" + " " * indentation + prefix + line[index1:]

    last_line_index = 80
    _line = ""

    for symbol in ["+", "-"]:
        if not line.startswith(symbol): continue
        
        _indentation = " " * (indentation + 1)  
        if not "(" in line:
            for index in range(last_line_index, 0, -1):
                if line[index] != " ": continue
                _line = new_line(index, index, 0, f"{symbol}" + _indentation)

        for index in range(last_line_index):
            if line[index] != "(": continue
            _line = new_line(index - 1, index, 0, f"{symbol}" + _indentation)
        
        if len(_line.split("\n")) > 80:
            _line = _line.split("\n")[0] + split_line_if_too_long(_line, recursion_index)
        
        return _line
    
    if "//" in line:
        
        if not "(" in line and not " " in line:
            _line = wrap(line, width=80, placeholder="...")                   
            
        if not "(" in line:
            for index in range(last_line_index, 0, -1):
                if line[index] != " ": continue
                _line = new_line(index, index, indentation, "//")
                break

        for index in range(last_line_index):
            if line[index] != "(": continue
            _line = new_line(index - 1, index, indentation, "//")

        if len(line.split("\n")) > 80:
            _line = line.split("\n")[0] + split_line_if_too_long(line, recursion_index)
        
        _line = _line if _line.count("//") == 1 else _line.replace("//   ", "")
        return _line
        
    if not "(" in line and not " " in line:
        _line = wrap(line, width=80, placeholder="...")
    
    if not "(" in line:
        for index in range(last_line_index, 0, -1):
            if line[index] != " ": continue
            _line = new_line(index, index, indentation + 2)
    
    for index in range(last_line_index):
        if line[index] != "(": continue
        _line = new_line(index - 1, index, indentation + 2)

    line_ = _line.split("\n")
    
    if len(line_[-1]) > 80:
        if "," in _line and "(" in _line:
            arguments = _line.split("(")[1].split(")")[0].replace(" ", "").split(",")
            fragments_after_arguments = _line.split(")")[1]

            for index in range(len(arguments)):
                arguments[index] = (indentation + 2) * " " + arguments[index]
                arguments[index] = arguments[index] + "," if len(arguments) - 1 > index else arguments[index]
            _line = line_[0] + "(" + " " * (indentation + 2) + "\n" + (("\n").join(arguments) + "\n") + " " * indentation + ")" + fragments_after_arguments\
        
    return _line