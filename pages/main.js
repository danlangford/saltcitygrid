document.addEventListener("DOMContentLoaded", () => {
    loadEvents("abr_data.json", "abr-past-events", "abr-upcoming-events", formatABREvent);
    loadEvents("cobra_tournaments.json", "cobra-past-events", "cobra-upcoming-events", formatCobraTournament);
});

document.addEventListener("DOMContentLoaded", () => {
    const glitchTitle = document.querySelector(".glitch");

    // Detect if on mobile
    function isMobile() {
        return /Mobi|Android/i.test(navigator.userAgent);
    }

    if (isMobile()) {
        glitchTitle.addEventListener("click", () => {
            glitchTitle.classList.add("glitch-active");

            // Remove glitch after a short time
            setTimeout(() => {
                glitchTitle.classList.remove("glitch-active");
            }, 1000);
        });
    }
});

async function loadEvents(jsonFile, pastContainerId, upcomingContainerId, formatter) {
    try {
        const response = await fetch(jsonFile);
        if (!response.ok) throw new Error("Failed to load " + jsonFile);
        const events = await response.json();

        const pastContainer = document.getElementById(pastContainerId);
        const upcomingContainer = document.getElementById(upcomingContainerId);

        // Clear previous content
        pastContainer.innerHTML = "";
        upcomingContainer.innerHTML = "";

        // Get today's date for filtering
        const today = new Date().toISOString().split("T")[0];

        const pastEvents = [];
        const upcomingEvents = [];

        events.forEach(event => {
            if (event.normalized_date < today) {
                pastEvents.push(event);
            } else {
                upcomingEvents.push(event);
            }
        });

        // Sort past events (most recent first)
        pastEvents.sort((a, b) => b.normalized_date.localeCompare(a.normalized_date));

        // Sort upcoming events (soonest first)
        upcomingEvents.sort((a, b) => a.normalized_date.localeCompare(b.normalized_date));


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

    } catch (error) {
        console.error("Error loading events:", error);
    }
}

function formatABREvent(event) {
    // someday support some iconography in the event that shows its recurring
    return createEventElement(event, event.url, event.title, event.normalized_date, event.creator_name, event.store + " " + event.address);
}

function formatCobraTournament(event) {
    return createEventElement(event, event.url, event.title, event.normalized_date, event.tournament_organizer, event.player_count + " players");
}

function createEventElement(event, url, title, date, organizer, info) {
    const template = document.getElementById("event-template");
    const eventElement = template.content.cloneNode(true);

    eventElement.querySelector(".event-title").href = url;
    eventElement.querySelector(".event-title").textContent = title;
    eventElement.querySelector(".event-date").textContent = date;
    eventElement.querySelector(".event-organizer").textContent = organizer;
    eventElement.querySelector(".event-info").textContent = info;

    return eventElement;
}


