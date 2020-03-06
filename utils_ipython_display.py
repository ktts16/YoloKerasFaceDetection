from IPython.display import Markdown, display
from IPython.core.display import display, HTML

def printmd(string, color=None):
    colorstr = "<span style='color:{}'>{}</span>".format(color, string)
    display(Markdown(colorstr))


def md_bold(string):
    return "**" + string + "**"


def show_hyperlink(url, text=None):
    if text is None:
        text = url
    display(HTML("<a href='" + url + "' target='_blank'>" + text + "</a>"))
