// script.js
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('tspForm');
    const locationsContainer = document.getElementById('locationsContainer');
    const routeList = document.getElementById('routeList');
    const distanceParagraph = document.getElementById('distance');
    const googleMapsLink = document.getElementById('googleMapsLink');
    
    // Add another location input field
    document.getElementById('addLocationBtn').addEventListener('click', () => {
        const input = document.createElement('input');
        input.type = 'text';
        input.name = 'locations';
        input.placeholder = `Enter location ${locationsContainer.children.length + 1}`;
        locationsContainer.appendChild(input);
    });

    // Handle form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        const locations = formData.getAll('locations');

        // Send the locations to the API
        try {
            const response = await fetch('/tsp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ locations })
            });

            if (!response.ok) {
                throw new Error('Failed to calculate the route.');
            }

            const result = await response.json();
            displayResult(result);
        } catch (error) {
            alert(error.message);
        }
    });

    // Display the result
    function displayResult(result) {
        routeList.innerHTML = '';
        result.best_path.forEach(location => {
            const li = document.createElement('li');
            li.textContent = location;
            routeList.appendChild(li);
        });

        distanceParagraph.textContent = `Total Distance: ${result.minimum_distance_km.toFixed(2)} km`;
        googleMapsLink.href = result.google_maps_url;
        googleMapsLink.style.display = 'block';
    }
});
