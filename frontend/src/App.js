import './App.css';
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Event from './components/Event';

function App() {
  const [events, setEvents] = useState([]);
  const [lastTimeRefreshed, setLastTimeRefreshed] = useState(Date.now());
  const [loaded, setLoaded] = useState(false);
  const [isRefreshDisabled, setIsRefreshDisabled] = useState(true);
  const [error, setError] = useState(false)

  const REFRESH_DELAY = 60000;


  useEffect(() => {
    axios.get(`http://127.0.0.1:8000/events/`)
      .then(response => {
        setEvents(response.data);
        setLoaded(true);
      })
      .catch(error => {
        console.error("Error fetching events:", error);
        setError(error)
        setLoaded(true);
        setIsRefreshDisabled(false)
      });
  }, [lastTimeRefreshed]);

  useEffect(() => {
    const timer = setInterval(() => {
      if (loaded){
        const oneMinutePassed = Date.now() > lastTimeRefreshed + REFRESH_DELAY;
        setIsRefreshDisabled(!oneMinutePassed);
      }
    }, 1000);

    return () => clearInterval(timer);
  }, [lastTimeRefreshed,loaded]);

  function handleClick() {
    setIsRefreshDisabled(true);
    setLastTimeRefreshed(Date.now());
    setLoaded(false); 
  }

  const lastRefreshDate = new Date(lastTimeRefreshed);
  const nextRefreshDate = new Date(lastTimeRefreshed + REFRESH_DELAY);

  return (
    <>
    <div className='event-header'>
      <h2>Tottenham Hotspur Stadium Events</h2>
      <div className='refresh-container' style={{ textAlign: 'center' }}>
        <button 
          onClick={handleClick} 
          disabled={isRefreshDisabled}
          style={{
            backgroundColor: isRefreshDisabled ? '#ccc' : '#007bff',
            cursor: isRefreshDisabled ? 'not-allowed' : 'pointer',
          }}
        >
          Refresh
        </button>
        
        {loaded && !error &&<span>
          <p>Last Refreshed: {lastRefreshDate.toLocaleTimeString()}</p>
          <p>Next Possible Refresh: {nextRefreshDate.toLocaleTimeString()}</p>
        </span>}
      
        {!loaded && <div className="loading-bar"></div>}
        {error && <p className='error'>Error: {error}</p>}
      </div>

      <div className="event-container">
        {loaded && events.map((event, index) => (
          <div key={index} className="event-box-wrapper">
            <Event
              name={event[1]}
              abbreviations={event[0].includes("Football") ? [event[4][0], event[4][1]] : undefined}
              date={event[2]}
              time={event[3]}
              tag={event[0]}
            />
          </div>
        ))}
      </div>
    </div>
    </>
  );
}

export default App;
