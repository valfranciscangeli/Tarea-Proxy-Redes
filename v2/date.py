import datetime

def get_current_datetime():

    # fecha actual en GMT
    current_datetime = datetime.datetime.utcnow()

    # formateamos como el ejemplo: "Mon, 04 Sep 2023 15:10:15 GMT"
    formatted_datetime = current_datetime.strftime('%a, %d %b %Y %H:%M:%S GMT')

    return formatted_datetime

# ===============================================