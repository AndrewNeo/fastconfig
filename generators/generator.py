import os

import yaml
from jinja2 import Environment, FileSystemLoader


class Generator(object):

    def __init__(self, config_file, output_dir):
        self.config_file = config_file
        self.output_dir = output_dir
        self.jinja = Environment(loader=FileSystemLoader("templates"))


    def generate(self):
        self.parse()
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.generate_templates(self.jinja)


    def parse(self):
        f = open(self.config_file, "r")
        self.structure = yaml.load(f.read())
        f.close()


    def generate_templates(self, jinja):
        pass

    @staticmethod
    def listize(item):
        if isinstance(item, list):
            return item

        return [item]
