from parsing.create_image import render
from parsing.parse import electric_transport_parse

electric_transport_parse()
#render({'transport': 'trol', 'num_way': '1', 'data': {0: {'stops': {"123_": {"time": {"5:00": ['1', '2','3','4','5','6','7','1', '2','3','4','5','6','7']}}}, 'text': None}, 1: {'stops': {}, 'text': None}}})
