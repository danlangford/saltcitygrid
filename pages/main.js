document.addEventListener("DOMContentLoaded", () => {
    loadEvents("merged_events.json", "past-events", "upcoming-events", createEventElement);
});

document.addEventListener("DOMContentLoaded", () => {
    const glitchElems = document.querySelectorAll(".glitch");
    glitchElems.forEach(glitchElem => {
        glitchElem.addEventListener("click", () => {
            glitchElem.classList.add("glitch-active");
            // Remove glitch after a short time
            setTimeout(() => {
                glitchElem.classList.remove("glitch-active");
            }, 1000);
        });
    })
});

async function loadEvents(jsonFile, pastContainerId, upcomingContainerId, renderer) {
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
            if (event.date < today) {
                pastEvents.push(event);
            } else {
                upcomingEvents.push(event);
            }
        });

        // Sort past events (most recent first)
        pastEvents.sort((a, b) => b.date.localeCompare(a.date));

        // Sort upcoming events (soonest first)
        upcomingEvents.sort((a, b) => a.date.localeCompare(b.date));


        // Display past events
        if (pastEvents.length > 0) {
            pastEvents.forEach(event => pastContainer.appendChild(renderer(event)));
        } else {
            pastContainer.innerHTML = "<p>No past events found.</p>";
        }

        // Display upcoming events
        if (upcomingEvents.length > 0) {
            upcomingEvents.forEach(event => upcomingContainer.appendChild(renderer(event)));
        } else {
            upcomingContainer.innerHTML = "<p>No upcoming events found.</p>";
        }

    } catch (error) {
        console.error("Error loading events:", error);
    }
}


function createEventElement(event) {
    const template = document.getElementById("event-template");
    const eventElement = template.content.cloneNode(true);

    eventElement.querySelector(".event-title").textContent = event.title;
    eventElement.querySelector(".event-date").textContent = event.date;
    eventElement.querySelector(".event-location").textContent = [...new Set(event.locations)].join(" | ");
    eventElement.querySelector(".event-info").textContent = [...new Set(event.details)].join(" | ");

    // loop through sources creating a link for each
    const sourcesElement = eventElement.querySelector(".event-links");
    for (const source of event.sources) {
        const link = document.createElement("a");
        link.href = source.link;
        link.innerText = source.source + " ";
        link.target = "_blank";
        sourcesElement.append(link);
    }

    return eventElement;
}


