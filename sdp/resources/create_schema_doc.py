from json_schema_for_humans.generate import generate_from_filename
from json_schema_for_humans.generation_configuration import GenerationConfiguration


if __name__ == '__main__':
    config = GenerationConfiguration(copy_css=False, template_name="md")
    generate_from_filename("schema.json", "schema_doc.md", config=config)
