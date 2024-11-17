import requests
from datetime import datetime
from scripts.rugby import rugby
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass
apiKey = os.getenv('API_KEY')

def isAlreadySameDateAndTime(eventArray, currentEvent):
    for event in eventArray:
         if event[1] == currentEvent['dates']['start']["localDate"] and event[2] == event['dates']['start']["localTime"]:
              return True
    return False

def formatEvents(events):
    formattedEvents = []
    for event in events:
        eventType, name, dateStr, timeStr = event
        dateObj = datetime.strptime(dateStr, "%Y-%m-%d")
        timeObj = datetime.strptime(timeStr, "%H:%M:%S")
        formattedDate = dateObj.strftime("%A %d %B %Y")
        formattedTime = timeObj.strftime("%H:%M")
        formattedEvents.append([eventType,name, formattedDate, formattedTime])
    
    return formattedEvents

def ticketMasterTottenham():
    rugbyEvents = rugby()

    print("Getting url")
    url = f'https://app.ticketmaster.com/discovery/v2/events.json?venueId=KovZ9177OxV&apikey={apiKey}'
    response = requests.get(url)
    data = response.json()
    acceptedEvents = []
    if '_embedded' in data:
        events = data['_embedded']['events']
        for event in events:
            if not isAlreadySameDateAndTime(acceptedEvents,event):
                acceptedEvents.append(["ticketMasterEvent",event["name"], event['dates']['start']["localDate"], event['dates']['start']["localTime"]])
    else:
        print("Failure retrieving")
        print(data)


    print("formatting events")
    formattedEvents = formatEvents(acceptedEvents)

    #Filter out rugby events from the accepted events
    for rugbyEvent in rugbyEvents:
        counter = 0
        while counter < len(formattedEvents):
            tokensForRugby = set(rugbyEvent[1].lower().replace("-", "").split())
            tokensForFormatted = set(formattedEvents[counter][1].lower().replace("-", "").split())
            overlap = tokensForRugby.intersection(tokensForFormatted)
            similarity = len(overlap) / max(len(tokensForRugby), len(tokensForFormatted))
            
            if similarity > 0.5:  
                formattedEvents.pop(counter)
            else:
                counter+=1

    #Filter out football events from the accepted events
    counter = 0
    tottenhamClubWords = ["tottenham","hotspur","hotspurs","spurs"]
    while counter < len(formattedEvents):
        checkForTottenham = [word for word in tottenhamClubWords if(word in formattedEvents[counter][1].lower())]
        if checkForTottenham:
            formattedEvents.pop(counter)
        else:
            counter +=1

    formattedEvents.sort(key=lambda x: datetime.strptime(f"{x[2]} {x[3]}", "%A %d %B %Y %H:%M"))
    print("FORMATTED EVENTS:",formattedEvents)
    return(formattedEvents)
