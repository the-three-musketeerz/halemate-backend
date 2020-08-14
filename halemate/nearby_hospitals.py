from googleplaces import GooglePlaces, types, lang
from halemate_backend.settings import GOOGLE_MAPS_API_KEY 
import json 
  
  
def searchNearbyHospitals(lat, lng, radius = 5000, limit_search_count = 10):
    """ Perform a nearby search using the Google Places API.
    keyword arguments:
    radius              -- The radius (in meters) around the location/lat_lng to
                           restrict the search to. The maximum is 50000 meters.
                           (default 5000)
    
    limit_search_count  -- searchCount of Result (default 10)
    """
    # Initialising the GooglePlaces constructor 
    google_places = GooglePlaces(GOOGLE_MAPS_API_KEY) 
    
    query_result = google_places.nearby_search( 
            lat_lng ={'lat': lat, 'lng': lng}, 
            radius = radius, 
            types =[types.TYPE_HOSPITAL]) 
    
    nearby_hospitals = []

    for place in query_result.places[:limit_search_count]: 
        hospital = dict()
        place.get_details()
        hospital['hospitalName'] = place.name
        hospital['address'] = place.formatted_address
        hospital['phoneNumber'] = place.local_phone_number 
        nearby_hospitals.append(hospital)

    if(len(nearby_hospitals) == 0):
        nearby_hospitals = searchNearbyHospitals(lat = lat, lng = lng, radius = radius+5000)

    return nearby_hospitals