import os
import requests
from datetime import date
import json


def tripadvisor_search(search_query=None, category=None):
    tripadvisor_api_key = os.environ.get("TRIPADVISOR_API_KEY")

    # searchQuery = text to use for searching based on the NAME of the location,
    # so e.g. "Malaga", but category could be "hotels", or "attractions", or "restaurants"

    # "hotels", "attractions", "restaurants", and "geos" are the valid options for the category parameter
    categories = ["hotels", "attractions", "restaurants"]
    # I'm excluding 'geos', because I actually don't know what that is. The tripadvisor API docs don't explain it.

    if category not in categories:
        raise ValueError(
            "Invalid category provided. Please provide one of the following: hotels, attractions, restaurants")

    url = (f'https://api.content.tripadvisor.com/api/v1/location/search'
           f'?key={tripadvisor_api_key}'
           f'&searchQuery={search_query}'
           f'&category={category}&language=en')  # language can be spanish too, but just use english for now

    try:
        response = requests.get(url, headers={
            "accept": "application/json"
        })

        if response.status_code == 200:
            res = json.dumps(response.json(), indent=4)
            res_json = json.loads(res)['data']

            locations = res_json

            concatenated_location_info = []

            # Sample location info:
            '''
            "location_id": "650588",
            "name": "Barcelo Malaga",
            "address_obj": {
                "street1": "Estacion Vialia Maria Zam Heroe de Sostoa 2",
                "city": "Malaga",
                "state": "Province of Malaga",
                "country": "Spain",
                "postalcode": "29002",
                "address_string": "Estacion Vialia Maria Zam Heroe de Sostoa 2, 29002 Malaga Spain"
            }
            '''

            for location in locations:
                location_id = location["location_id"]
                name = location["name"]
                city = location["address_obj"]["city"]
                country = location["address_obj"]["country"]

                info = f"""
                    LocationID: {location_id},
                    Name: {name},
                    City: {city},
                    Country: {country},                    
                """

                concatenated_location_info.append(info)

            return concatenated_location_info

        else:
            return []  # No locations found

    except requests.RequestException as e:
        print("Error occurred during Tripadvisor API call: ", e)


def tripadvisor_location_details(location_id=None):
    tripadvisor_api_key = os.environ.get("TRIPADVISOR_API_KEY")

    url = (f"https://api.content.tripadvisor.com/api/v1/location/"
           f"{location_id}/details"
           f"?key={tripadvisor_api_key}"
           f"&language=en&currency=EUR")

    try:
        response = requests.get(url, headers={
            "accept": "application/json"
        })

        if response.status_code == 200:
            res = json.dumps(response.json(), indent=4)
            location = json.loads(res)

            concatenated_location_info = []

            # Sample location info:
            '''
            {
              "location_id": "650588",
              "name": "Barcelo Malaga",
              "description": "The Barceló Malaga hotel located next to the city railway station, just 10 minutes from the city center and the coastline is one of the few Spanish hotels recognized by the prestigious British Magazine Wallpaper as one of the 50 best business hotels in the world. It hosts the most amazing lobby of our country with its particular six meters high stainless steel slide connecting the first floor directly with La Santa María, a new concept of Gatro Bar with an outstanding cuisine to take a look at histrory by travelling through its stoves. On the 8th floor you will find the B-Heaven Relax & Ambience, with a skyline view, during the day you can enjoy the sun, the pool and a variety of snacks, salads, cocktails and refreshing drinks. Its 221 modern and comfortable rooms ensure a pleasant break, while the 1,500 m2 Convention Center seduces sectors committed to design to ensure the success of their events and meetings.",
              "web_url": "https://www.tripadvisor.com/Hotel_Review-g187438-d650588-Reviews-Barcelo_Malaga-Malaga_Costa_del_Sol_Province_of_Malaga_Andalucia.html?m=66827",
              "address_obj": {
                "street1": "Estacion Vialia Maria Zam Heroe de Sostoa 2",
                "city": "Malaga",
                "state": "Province of Malaga",
                "country": "Spain",
                "postalcode": "29002",
                "address_string": "Estacion Vialia Maria Zam Heroe de Sostoa 2, 29002 Malaga Spain"
              },
              "ranking_data": {
                "geo_location_id": "187438",
                "ranking_string": "#12 of 121 hotels in Malaga",
                "geo_location_name": "Malaga",
                "ranking_out_of": "121",
                "ranking": "12"
              },
              "rating": "4.5",
              "rating_image_url": "https://www.tripadvisor.com/img/cdsi/img2/ratings/traveler/4.5-66827-5.svg",
              "num_reviews": "5665",
              "review_rating_count": {
                "1": "75",
                "2": "95",
                "3": "334",
                "4": "1742",
                "5": "3422"
              },
              "subratings": {
                "0": {
                  "name": "rate_location",
                  "localized_name": "Location",
                  "rating_image_url": "https://static.tacdn.com/img2/ratings/traveler/ss4.5.svg",
                  "value": "4.5"
                },
                "1": {
                  "name": "rate_sleep",
                  "localized_name": "Sleep Quality",
                  "rating_image_url": "https://static.tacdn.com/img2/ratings/traveler/ss4.5.svg",
                  "value": "4.5"
                },
              },
              "photo_count": "1992",
              "see_all_photos": "https://www.tripadvisor.com/Hotel_Review-g187438-d650588-m66827-Reviews-Barcelo_Malaga-Malaga_Costa_del_Sol_Province_of_Malaga_Andalucia.html#photos",
              "price_level": "$$$",
              "amenities": [
                "Free Internet",
                "Wifi",
                "Free Wifi",
                "Suites",
                "Public Wifi",
                "Air conditioning",
              ],
              "parent_brand": "Barcelo Hotels & Resorts",
              "brand": "Barcelo Hotels & Resorts",
              "category": {
                "name": "hotel",
                "localized_name": "Hotel"
              },
              "subcategory": [
                {
                  "name": "hotel",
                  "localized_name": "Hotel"
                }
              ],
              "styles": [
                "Business",
                "Modern"
              ],
              "neighborhood_info": [],
              "trip_types": [
                {
                  "name": "business",
                  "localized_name": "Business",
                  "value": "671"
                },
                {
                  "name": "couples",
                  "localized_name": "Couples",
                  "value": "2568"
                },
                {
                  "name": "solo",
                  "localized_name": "Solo travel",
                  "value": "285"
                },
                {
                  "name": "family",
                  "localized_name": "Family",
                  "value": "912"
                },
                {
                  "name": "friends",
                  "localized_name": "Friends getaway",
                  "value": "645"
                }
              ],
              "awards": [
                {
                  "award_type": "Travelers Choice",
                  "year": "2024",
                  "images": {
                    "tiny": "https://static.tacdn.com/img2/travelers_choice/widgets/tchotel_2024_L.png",
                    "small": "https://static.tacdn.com/img2/travelers_choice/widgets/tchotel_2024_L.png",
                    "large": "https://static.tacdn.com/img2/travelers_choice/widgets/tchotel_2024_L.png"
                  },
                  "categories": [],
                  "display_name": "Travelers Choice"
                },
                {
                  "award_type": "Travelers Choice",
                  "year": "2023",
                  "images": {
                    "tiny": "https://static.tacdn.com/img2/travelers_choice/widgets/tchotel_2023_L.png",
                    "small": "https://static.tacdn.com/img2/travelers_choice/widgets/tchotel_2023_L.png",
                    "large": "https://static.tacdn.com/img2/travelers_choice/widgets/tchotel_2023_L.png"
                  },
                  "categories": [],
                  "display_name": "Travelers Choice"
                }
              ]
            }
            '''

            location_id = location["location_id"]
            name = location["name"]
            description = location["description"]
            web_url = location["web_url"]

            # E.g #12 out of 121 hotels in Malaga
            ranking_string = location["ranking_data"]["ranking_string"]

            # in stars, e.g. 4.5
            rating = location["rating"]
            num_reviews = location["num_reviews"]

            '''        
            this is an object containing ratings for specific attributes, e.g 'rate_location'                    
            so each object would have:
            name(e.g rate_sleep)
            rating_value (e.g 4.5)
            '''

            subratings = location["subratings"]
            subrating_info = []

            for detail in subratings:
                subrating_name = subratings[detail]["localized_name"]
                subrating_value = subratings[detail]["value"]

                subrating_info.append(f"{subrating_name}: {subrating_value}")

                # Given in dollar signs, e.g. $$$, max is $$$$
            # So $ is the cheapest, $$$$ is the most expensive
            price_level = location["price_level"]

            # Array containing e.g. ["Free Internet", "Wifi", "Free Wifi", "Suites", "Public Wifi",
            # "Air conditioning"]
            amenities = location["amenities"]  # array

            # This is an array of objects Each object has: name -> e.g business, solo, couples, friends value ->
            # e.g 671, 285, 2568, 645 -> this is the number of recommendations given for each type,
            # so if the highest number is for 'couples', then this location is most recommended for couples
            trip_types = location["trip_types"]

            trip_type_info = []

            for trip_type in trip_types:
                # if trip type is string, split it by colon
                if isinstance(trip_type, str):
                    trip_type_list = trip_type.split(":")

                    trip_type_name = trip_type_list[0]
                    trip_type_value = trip_type_list[1]
                elif isinstance(trip_type, dict):
                    trip_type_name = trip_type["name"]
                    trip_type_value = trip_type["value"]
                else:
                    trip_type_name = "Unknown"
                    trip_type_value = "Unknown"

                concat_trip_type = f"{trip_type_name}: {trip_type_value}"
                trip_type_info.append(concat_trip_type)

            # For subratings
            subrating_info_str = ', '.join(subrating_info)

            # For amenities
            amenities_str = ', '.join(amenities)

            # For trip_types
            trip_type_info_str = ', '.join(trip_type_info)

            # cuisine and features are specific to restaurants

            # "cuisine": [
            #     {
            #         "name": "mediterranean",
            #         "localized_name": "Mediterranean"
            #     },
            #     {
            #         "name": "european",
            #         "localized_name": "European"
            #     },
            #     {
            #         "name": "spanish",
            #         "localized_name": "Spanish"
            #     },
            #     {
            #         "name": "contemporary",
            #         "localized_name": "Contemporary"
            #     }
            # ],

            # "features": [
            #     "Accepts Credit Cards",
            #     "Gift Cards Available",
            #     "Highchairs Available",
            #     "Outdoor Seating",
            #     "Reservations",
            #     "Seating",
            #     "Serves Alcohol",
            #     "Table Service",
            #     "Wheelchair Accessible"
            # ],

            cuisine_info = []
            if location["cuisine"]:

                cuisine = location["cuisine"]

                for cuisine_type in cuisine:
                    cuisine_name = cuisine_type["name"]
                    cuisine_info.append(cuisine_name)

            cuisine_info_str = ', '.join(cuisine_info)

            features_info = []
            if location["features"]:

                features = location["features"]

                for feature in features:
                    feature_name = feature
                    features_info.append(feature_name)

            features_info_str = ', '.join(features_info)

            # We're dealing with a restaurant
            if len(cuisine_info) > 0:
                info = f"""
                    LocationID: {location_id},
                    Name: {name},
                    Description: {description},
                    Ranking: {ranking_string}
                    Rating: f"{rating} stars, based on {num_reviews} reviews"
                    Subratings: {subrating_info_str},
                    Amenities: {amenities_str},
                    Recommended for these types: {trip_type_info_str},
                    Web URL: {web_url}, 
                    Price level: {price_level}        
                    Cuisine: {cuisine_info_str},
                    Features: {features_info_str}           
                """
            else:
                info = f"""
                    LocationID: {location_id},
                    Name: {name},
                    Description: {description},
                    Ranking: {ranking_string}
                    Rating: f"{rating} stars, based on {num_reviews} reviews"
                    Subratings: {subrating_info_str},
                    Amenities: {amenities_str},
                    Recommended for these types: {trip_type_info_str},
                    Web URL: {web_url}, 
                    Price level: {price_level}                   
                """

            concatenated_location_info.append(info)

            return concatenated_location_info

        else:
            return []  # No locations found

    except requests.RequestException as e:
        print("Error occurred during Tripadvisor location details API call: ", e)
