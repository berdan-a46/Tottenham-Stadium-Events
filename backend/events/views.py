from django.http import HttpResponse
import json
import heapq
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from scripts.rugby import rugby
from scripts.ticketMasterTottenham import ticketMasterTottenham
from scripts.tottenhamFootballMen import tottenhamFootballMen
from scripts.rugbyAndTMEvents import rugbyAndTMEvents
from scripts.allEvents import allEvents

def parseDate(event):
    date = event[2]  
    time = event[3] 
    dateTime = f"{date} {time}"
    return datetime.strptime(dateTime, "%A %d %B %Y %H:%M")

def oneSelenium(event):
    eventDictionary = {}
    eventDictionary["tottenhamFootballMen"], eventDictionary["rugby"], eventDictionary["ticketMasterTottenham"] = allEvents()
     
    minHeap = []
    result = []

    #Push first event of each event type into the heap to start it off
    for eventType, eventList in eventDictionary.items():
        if eventList:
            firstEvent = eventList[0]
            firstEventDate = parseDate(firstEvent)
            heapq.heappush(minHeap, (firstEventDate, firstEvent, 0, eventList))

    while minHeap:
        currentDate, currentEvent, index, eventList = heapq.heappop(minHeap)
        result.append(currentEvent)

        
        if index + 1 < len(eventList):
            nextEvent = eventList[index + 1]
            nextEventDate = parseDate(nextEvent)
            heapq.heappush(minHeap, (nextEventDate, nextEvent, index + 1, eventList))
    
    return HttpResponse(json.dumps(result))

def index(request):
    eventDictionary = {}
    eventDictionary["rugby"], eventDictionary["ticketMasterTottenham"] = rugbyAndTMEvents()
    eventDictionary["tottenhamFootballMen"] = tottenhamFootballMen()
     
    minHeap = []
    result = []

    #Push first event of each event type into the heap to start it off
    for eventType, eventList in eventDictionary.items():
        if eventList:
            firstEvent = eventList[0]
            firstEventDate = parseDate(firstEvent)
            heapq.heappush(minHeap, (firstEventDate, firstEvent, 0, eventList))

    while minHeap:
        currentDate, currentEvent, index, eventList = heapq.heappop(minHeap)
        result.append(currentEvent)

        
        if index + 1 < len(eventList):
            nextEvent = eventList[index + 1]
            nextEventDate = parseDate(nextEvent)
            heapq.heappush(minHeap, (nextEventDate, nextEvent, index + 1, eventList))
    
    return HttpResponse(json.dumps(result))


def concurrent(request):
    eventDictionary = {}
    events = [
        ("rugby", rugby),
        ("ticketMasterTottenham", ticketMasterTottenham),
        ("tottenhamFootballMen", tottenhamFootballMen),
    ]

    # Run the scripts above concurrently
    with ThreadPoolExecutor() as executor:
        results = []

        for eventName, func in events:
            print("submit thread")
            thread = executor.submit(func)
            results.append((eventName, thread))

        for eventName, thread in results:
            try:
                eventDictionary[eventName] = thread.result()
            except Exception as e:
                print(f"Error processing {eventName}: {e}")
    
    minHeap = []
    result = []

    #Push first event of each event type into the heap to start it off
    for eventType, eventList in eventDictionary.items():
        if eventList:
            firstEvent = eventList[0]
            firstEventDate = parseDate(firstEvent)
            heapq.heappush(minHeap, (firstEventDate, firstEvent, 0, eventList))
    
    while minHeap:
        currentDate, currentEvent, index, eventList = heapq.heappop(minHeap)
        result.append(currentEvent)
        
        if index + 1 < len(eventList):
            nextEvent = eventList[index + 1]
            nextEventDate = parseDate(nextEvent)
            heapq.heappush(minHeap, (nextEventDate, nextEvent, index + 1, eventList))
    
    return HttpResponse(json.dumps(result))


