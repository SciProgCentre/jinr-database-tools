import json
import sys
from pathlib import Path
from string import Template
from typing import Union

from importlib.resources import read_text, as_file, files

HTML_TEMPLATE = read_text("sdp.resources", "schema_doc_template.html")
PARAGRAPH = "<p>{}</p>\n"


def render_from_file_to_file(json_file: Union[Path, str], html_file: Union[Path, str]):
    json_file = Path(json_file)
    html_file = Path(html_file)
    with html_file.open("w") as fout:
        fout.write(render_from_file(json_file))


def render_from_file(json_file: Path):
    with open(json_file) as fin:
        scheme = json.load(fin)
    return render_html(scheme)


def render_html(scheme: Union[dict, str]):
    if isinstance(scheme, str):
        scheme = json.loads(scheme)
    body = "<h1>{}</h1>\n".format(scheme["title"])
    render = choose_type_render(scheme["type"])
    body += render(scheme)
    return Template(HTML_TEMPLATE).safe_substitute({"body": body})


def choose_type_render(type_):
    if type_ == "object":
        return render_object
    elif type_ == "array":
        return render_array
    elif type_ in ['string', "integer", "boolean"]:
        return render_primitive
    else:
        return lambda x: ""


def render_object(obj):
    result = ""
    for name, properties in obj["properties"].items():
        render = choose_type_render(properties["type"])
        result += "<dt>{}</dt><dd>{}</dd>\n".format(name, render(properties))
    return "<dl>{}</dl>\n".format(result)


def render_array(obj):
    result = PARAGRAPH.format(obj["description"])
    items = obj["items"]
    items_render = choose_type_render(items["type"])
    result += PARAGRAPH.format(items_render(items))
    return result


def render_primitive(obj):
    return PARAGRAPH.format(obj["description"])


if __name__ == '__main__':
    with as_file(files("sdp.resources").joinpath("schema.json")) as json_path:
        render_from_file_to_file(json_path, "schema.html")
