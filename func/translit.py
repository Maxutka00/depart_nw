
def translit(string: str, back: bool = False) -> str:
    """
    Транслитерация строки c украинского на английский
    """
    d = {'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ж': '#1', 'З': 'Z', 'И': 'Y', 'Й': 'J', 'К': 'K',
        'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H',
        'Ц': 'C', 'Ч': '=1', 'Ш': '@!', 'Ю': '+1', 'Я': '!1', 'І': 'I',
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ж': '#',
        'з': 'z', 'и': 'y', 'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
        'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c',
        'ч': '=', 'ш': '@', 'ю': '+',
        'я': '!', 'і': 'i',
    }
    if back:
        d = {v: k for k, v in d.items()}
    for i in d:
        string = string.replace(i, d.get(i))
    return string


if __name__ == '__main__':
    print(translit('=1', back=True))
