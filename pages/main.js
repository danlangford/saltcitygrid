document.addEventListener("DOMContentLoaded", () => {
    loadEvents("abr_data.json", "abr-past-events", "abr-upcoming-events", "abr-recurring-events", formatABREvent);
    loadEvents("cobra_tournaments.json", "cobra-past-events", "cobra-upcoming-events", null, formatCobraTournament);
});

async function loadEvents(jsonFile, pastContainerId, upcomingContainerId, recurringContainerId, formatter) {
    try {
        const response = await fetch(jsonFile);
        if (!response.ok) throw new Error("Failed to load " + jsonFile);
        const events = await response.json();

        const pastContainer = document.getElementById(pastContainerId);
        const upcomingContainer = document.getElementById(upcomingContainerId);
        const recurringContainer = recurringContainerId ? document.getElementById(recurringContainerId) : null;

        // Clear previous content
        pastContainer.innerHTML = "";
        upcomingContainer.innerHTML = "";
        if (recurringContainer) recurringContainer.innerHTML = "";

        // Get today's date for filtering
        const today = new Date().toISOString().split("T")[0];

        const pastEvents = [];
        const upcomingEvents = [];
        const recurringEvents = [];

        events.forEach(event => {
            if (event.normalized_date) {
                if (event.normalized_date < today) {
                    pastEvents.push(event);
                } else {
                    upcomingEvents.push(event);
                }
            } else if (event.recurring_day && recurringContainer) {
                recurringEvents.push(event);
            }
        });

        // Sort past events (most recent first)
        pastEvents.sort((a, b) => b.normalized_date.localeCompare(a.normalized_date));

        // Sort upcoming events (soonest first)
        upcomingEvents.sort((a, b) => a.normalized_date.localeCompare(b.normalized_date));

        // Sort recurring events alphabetically
        recurringEvents.sort((a, b) => a.recurring_day.localeCompare(b.recurring_day));

        // Display past events
        if (pastEvents.length > 0) {
            pastEvents.forEach(event => pastContainer.appendChild(formatter(event)));
        } else {
            pastContainer.innerHTML = "<p>No past events found.</p>";
        }

        // Display upcoming events
        if (upcomingEvents.length > 0) {
            upcomingEvents.forEach(event => upcomingContainer.appendChild(formatter(event)));
        } else {
            upcomingContainer.innerHTML = "<p>No upcoming events found.</p>";
        }

        // Display recurring events
        if (recurringContainer && recurringEvents.length > 0) {
            recurringEvents.forEach(event => recurringContainer.appendChild(formatter(event, true)));
        } else if (recurringContainer) {
            recurringContainer.innerHTML = "<p>No recurring meetups found.</p>";
        }
    } catch (error) {
        console.error("Error loading events:", error);
    }
}

function formatABREvent(event, isRecurring = false) {
    if (isRecurring) {
        return createRecurringEventElement(event, event.url, event.title, event.recurring_day, event.creator_name, event.players_count);
    }
    return createEventElement(event, event.url, event.title, event.normalized_date, event.creator_name, event.players_count);
}

function formatCobraTournament(event) {
    return createEventElement(event, event.url, event.title, event.normalized_date, event.tournament_organizer, event.player_count);
}

function createEventElement(event, url, title, date, organizer, players) {
    const template = document.getElementById("event-template");
    const eventElement = template.content.cloneNode(true);

    eventElement.querySelector(".event-title").href = url;
    eventElement.querySelector(".event-title").textContent = title;
    eventElement.querySelector(".event-date").textContent = date;
    eventElement.querySelector(".event-organizer").textContent = organizer;
    eventElement.querySelector(".event-players").textContent = players;

    return eventElement;
}

function createRecurringEventElement(event, url, title, recurringDay, organizer, players) {
    const template = document.getElementById("event-template");
    const eventElement = template.content.cloneNode(true);

    eventElement.querySelector(".event-title").href = url;
    eventElement.querySelector(".event-title").textContent = title;
    eventElement.querySelector(".event-date").textContent = `Every ${recurringDay}`;
    eventElement.querySelector(".event-organizer").textContent = organizer;
    eventElement.querySelector(".event-players").textContent = players;

    return eventElement;
}
