import math
import os
import time
import textwrap
from PIL import Image, ImageFont, ImageDraw

# (1182, 1280)
from func.translit import translit

names = {"trol": "Тролейбус", "tram": "Трамвай"}
black = '#000000'
white = '#ffffff'
text_color = black
letters = {"a": "А", "b": "Б"}


# day_row 545

# row 53
# col 41

def render(data: dict):

    font = ImageFont.truetype(os.path.join('parsing', 'fonts', 'Arial-BoldMT.ttf'), size=40)
    subtitle_font = ImageFont.truetype(os.path.join('parsing', 'fonts', 'Arial-BoldMT.ttf'), size=40)
    title_font = ImageFont.truetype(os.path.join('parsing', 'fonts', 'Arial-BoldMT.ttf'), size=60)
    stops = {}
    for day in data["data"]:
        day_data = data["data"][day]
        if day_data["stops"] != {}:
            for stop in day_data["stops"]:
                if stops.get(stop, None) is None:
                    stops.update({stop: day})
                else:
                    stops.update({stop: -1})
    if stops == {} and data["data"][0]['text'] == data["data"][1]['text']:
        text = data["data"][0]['text'].strip()
        text_image = Image.new("RGB", (600, 600), white)
        draw_for_text = ImageDraw.Draw(text_image)
        w, h = draw_for_text.textsize(text, font=title_font)
        if w > 800:
            text = textwrap.wrap(text, width=20)
            text = '\n'.join(text)
            w, h = draw_for_text.textsize(text, font=title_font)
            print(w, h)
        draw_for_text.multiline_text((50, (600 - h) / 2), text,
                                     font=font,
                                     fill=black,
                                     align="center")
        text_image.save(os.path.join("parsing", "photos", f"{data['num_way']}{data['transport']}.png"), 'PNG')
        return
    for stop in stops:
        image = Image.open(os.path.join("parsing", 'original.jpg'))
        draw = ImageDraw.Draw(image)
        draw.text((1000, 200),
                  f'{names.get(data["transport"])} {letters.get(data["num_way"], None) if letters.get(data["num_way"], None) else data["num_way"]}',
                  font=title_font, fill=black)
        draw.text((380, 366), stop.split('_')[0], font=subtitle_font, fill=text_color)
        draw.text((1398, 366), stop.split('_')[1], font=subtitle_font, fill=text_color)
        for day in data["data"]:
            text = data["data"][day]['text']
            if text:
                text = text.strip()
                width, height = (981, 1200)
                text_image = Image.new("RGB", (width, height), white)
                draw_for_text = ImageDraw.Draw(text_image)
                w, h = draw_for_text.textsize(text, font=title_font)
                if w > width:
                    text = textwrap.wrap(text, width=20)
                    text = '\n'.join(text)
                    w, h = draw_for_text.textsize(text, font=title_font)
                draw_for_text.multiline_text(((width - w) / 2, 200), text, font=title_font, fill=black,
                                             align="center")
                image.paste(text_image, (177 + 1085 * day, 570))
                continue
            if day != stops.get(stop) and stops.get(stop) != -1:
                continue
            for row_num, minutes in enumerate(data['data'][day]['stops'][stop]['time'].values()):
                if len(minutes) > 13:
                    draw.text((298 + 985 * day, 631 + row_num * 58), "кожні 5 хвилин", font=font, fill=text_color)
                    continue
                for num, minute in enumerate(minutes):
                    draw.text((298 + 985 * day + 65 * num, 631 + row_num * 58), minute, font=font, fill=text_color)
        direction = stop.split('_')[1].replace('"', "'").replace("/", "слеш").replace(
            "\\", "bsl")
        stop = stop.split('_')[0].replace('"', "'").replace("/", "слеш")
        name = f"{stop}_{direction}"
        if os.path.exists(os.path.join("parsing", "photos", f"{data['num_way']}{data['transport']}_{name}.png")):
            im = Image.open(os.path.join("parsing", "photos", f"{data['num_way']}{data['transport']}_{name}.png"))
            if im.histogram() == image.histogram():
                pass
            else:
                im.close()
                os.remove(os.path.join("parsing", "photos", f"{data['num_way']}{data['transport']}_{name}.png"))
            im.close()
        image.save(os.path.join("parsing", "photos", f"{data['num_way']}{data['transport']}_{name}.png"), "PNG")
        #image.show()
        image.close()
        # image.show()
    b = time.time()
    # print(f"{b - a}сек")


if __name__ == '__main__':
    render({'transport': 'tram', 'num_way': '1', 'data': {0: {'stops': {'ЗАЛІЗНИЧНИЙ ВОКЗАЛ_': {'time': {'5:00': ['05', '10', '15', '20', '25'], '6:00': ['05', '10', '15', '20', '25']}}}, 'text': None}, 1: {'stops': {'ЗАЛІЗНИЧНИЙ ВОКЗАЛ_': {'time': {'5:00': ['05', '10', '15', '20', '25'], ' 6:00': ['05', '10', '15', '20', '25']}}}, 'text': None}}})
