parsing_transport_status = False


class status:

    @property
    def get_parsing_status(self):
        return parsing_transport_status

    @staticmethod
    def set_parsing_status(parse_status: bool):
        global parsing_transport_status
        parsing_transport_status = parse_status
