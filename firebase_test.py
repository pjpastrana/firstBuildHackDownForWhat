from firebase import firebase
import datetime

FIREDB = firebase.FirebaseApplication('https://torrid-heat-7640.firebaseio.com', None)

upc = "123456789"
weight = "300"
quadrant = "2"
timestamp = datetime.datetime.utcnow()
print timestamp
FIREDB.put('/locationStatus/q'+quadrant, 'upc' , upc)
FIREDB.post('/eventLog/', {'upc':upc, 'weight':weight, 'timestamp':timestamp})
