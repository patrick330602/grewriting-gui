def is_connected():
    import requests
    connection = None
    try:
        r = requests.get("https://www.ets.org")
        r.raise_for_status()
        connection = True
    except:
        connection = False
    finally:
        return connection