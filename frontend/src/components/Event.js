import React from "react";
import './Event.css';

function Event({ name, date, time, tag, abbreviations }) {
    let classNameStyling = "event-box";
    const hasFootballTag = tag === "Football" || tag === "Women Football"

    if (hasFootballTag) {
        classNameStyling += ` event-box-${tag.toLowerCase().replace(' ', '-')}`;
    }

    return (
        <div className={classNameStyling}>
            {hasFootballTag && <div className="event-tag">{tag}</div>}
            <div className="event-content">
                <h2 className="event-name">{name}</h2>
                {abbreviations && <p className="event-abbreviations">{abbreviations.join(' vs ')}</p>}
                <p className="event-date">{date}</p>
                <p className="event-time">{time}</p>
            </div>
        </div>
    );
}

export default Event;
