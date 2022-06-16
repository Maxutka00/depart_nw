import db


def firs_letter(string: str):
    string = list(string)
    if not string[0].isdigit():
        string[0] = string[0].upper()

    return ''.join(string)


def get_text(num: str, transport_type):
    all_data = db.get_transport(num)
    text = []
    if not all_data:
        if not num:
            return
        for symbol in num:
            if not symbol.isdigit():
                num = num.replace(symbol, '')
        if int(num) < 177:
            txt = "Ви помилились, цей маршрут відсутній серед маршрутів міста.\nНапишіть правильний номер маршруту, будь ласка."
        elif int(num) > 177:
            txt = 'Даний маршрут не входить у маршрутну сітку міста Дніпро і, на жаль, ми не змогли отримати інформацію щодо його розкладу. Щоб дізнатись його розклад спробуйте зателефонувати на гарячу лінію ОДА за безкоштовним номером - 0800505600'
        else:
            return
        return f"{transport_type} {num}\n\n{txt}"
    text.append(f"<b>{transport_type} {num}</b>")
    for data in all_data:
        text.append('')
        if data[6] == 0:
            text.append("Тимчасово не обслуговується")
            return '\n'.join(text)
        way_place = data[1].split('\n')
        way_time = data[2].split('\n')
        if data[3]:
            delimiter = data[3]
            text.append(f"<b>{firs_letter(delimiter)}</b>")
        text.append("{}<b>Перший та останній рейси:</b>".format("\n" if data[3] else ""))
        for i in range(len(way_place)):
            text.append(f"<b>{way_place[i]}</b> - {way_time[i]}")
            if data[5]:
                text.append(firs_letter(data[5].split('\n')[i]))
            if i != len(way_place) - 1 and len(way_time[i]) >= 75:
                text.append('')
        if data[4]:
            text.append('\n<b>Інтервал руху:</b>')
            intervals = data[4].split(';')
            interval_time = ['7:00-9:00', '9:00-16:00', '16:00-19:00']
            for i in range(len(intervals)):
                interval = 'не известно' if intervals[i] == '' else intervals[0]
                text.append(f"{interval_time[i]} - {interval}хв")
        if data[4] and all_data.index(data) != len(all_data) - 1:
            text.append("———————————")
    text.append(
        "\nМожливі відхилення від інтервалів руху у зв'язку з браком палива.\nПо роботі бота писати t.me/ins_bot_chat")
    return '\n'.join(text)


if __name__ == "__main__":
    print(get_text('40', 'Автобус'))
