let currentEventsJSON = "";

async function fetchEvents() {
    try {
        const response = await fetch('/api/events');
        const events = await response.json();
        const newEventsJSON = JSON.stringify(events);
        
        if (events.length > 0 && newEventsJSON !== currentEventsJSON) {
            renderEvents(events);
            updateLatestSnapshot(events[0]);
            currentEventsJSON = newEventsJSON;
        }
    } catch (error) {
        console.error("Error fetching events:", error);
    }
}

function renderEvents(events) {
    const container = document.getElementById('events-list');
    container.innerHTML = '';
    
    events.forEach((event, index) => {
        const card = document.createElement('div');
        // Add animation class to the newest item
        card.className = `event-card ${index === 0 ? 'animate-in' : ''}`;
        
        // Add click listener to show this specific snapshot
        card.addEventListener('click', () => updateLatestSnapshot(event));
        
        const badgeClass = event.event.toLowerCase();
        
        card.innerHTML = `
            <div class="event-info">
                <h3>${event.object.replace('_', ' ')}</h3>
                <p>${event.timestamp}</p>
            </div>
            <div class="badge ${badgeClass}">${event.event}</div>
        `;
        
        container.appendChild(card);
    });
}

function updateLatestSnapshot(event) {
    const img = document.getElementById('latest-snapshot');
    const timeLabel = document.getElementById('snapshot-time');
    
    if (event.snapshot && event.snapshot.trim() !== '') {
        img.src = `/snapshots/${event.snapshot}`;
        img.style.display = 'block';
        timeLabel.innerHTML = `<span><strong style="color:var(--event-${event.event.toLowerCase()})">${event.event}</strong>: ${event.object.replace('_', ' ').toUpperCase()}</span> <span>${event.timestamp}</span>`;
    }
}

// Fetch immediately and then poll every 1 second
fetchEvents();
setInterval(fetchEvents, 1000);
