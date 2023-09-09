import datetime

""" Funcion que entrega la fecha y hora actual en formato GMT """


def get_current_datetime() -> str:

    # fecha actual en GMT
    current_datetime = datetime.datetime.utcnow()

    # formateamos como el ejemplo: "Mon, 04 Sep 2023 15:10:15 GMT"
    formatted_datetime = current_datetime.strftime('%a, %d %b %Y %H:%M:%S GMT')

    return formatted_datetime

# ===============================================
