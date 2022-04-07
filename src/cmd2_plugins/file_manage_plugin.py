import rich.progress
from cmd2 import Cmd2ArgumentParser, with_argparser

upload_parser = Cmd2ArgumentParser()
upload_parser.add_argument("source", required=True, help="localfile to upload to implant")
upload_parser.add_argument("destination", required=True, help="Destination to upload the file too")


class Plugin:
    @with_argparser(upload_parser)
    def do_upload(self, args):
        pass