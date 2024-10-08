import os
import requests
from datetime import date
import json
from dateutil import parser


def get_flights(flyFrom, flyTo, dateFrom=None, dateTo=None):
    kiwi_api_key = os.environ.get("KIWI_API_KEY")

    # always set the dateFrom and dateTo to None if not provided


    # If no dateFrom is provided, use today's date as the starting point
    if not dateFrom:
        dateFrom = date.today()
        # tequila api expects dd/mm/yyyy
        dateFromFormatted = dateFrom.strftime("%d/%m/%Y")

    if not dateTo:
        # Let's just say the user wants to fly within the next year
        dateTo = date.today().replace(year=date.today().year + 1)

    if dateTo:
        dateTo_object = parser.parse(dateTo)
        dateToFormatted = dateTo_object.strftime("%d/%m/%Y")

    if dateFrom:
        dateFrom_object = parser.parse(dateTo)
        dateFromFormatted = dateFrom_object.strftime("%d/%m/%Y")

    # apiKey to be passed in headers
    url = f'https://api.tequila.kiwi.com/v2/search?flyFrom={flyFrom}&to={flyTo}&dateFrom={dateFromFormatted}&dateTo={dateToFormatted}'

    try:
        response = requests.get(url, headers={
            "apiKey": kiwi_api_key
        })

        if response.status_code == 200:
            res = json.dumps(response.json(), indent=4)
            res_json = json.loads(res)['data']

            flights = res_json

            concatenated_flights_info = []

            for flight in flights:
                cityFrom = flight["cityFrom"]
                cityTo = flight["cityTo"]
                depart_at = flight["local_departure"]
                arrive_at = flight["local_arrival"]
                price_per_person = flight["price"]
                available_seats = flight["availability"]["seats"]

                info = f"""
                    From: {cityFrom},
                    To: {cityTo},
                    Depart at: {depart_at},
                    Arrive at: {arrive_at},
                    Price per person: {price_per_person},
                    Available sets: {available_seats}
                """

                concatenated_flights_info.append(info)

            return concatenated_flights_info

        else:
            return []  # No flights found

    except requests.RequestException as e:
        print("Error occurred during API call: ", e)
