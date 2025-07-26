document.getElementById('genre-form').addEventListener('submit', function (event) {
    event.preventDefault();
    const genreInput = document.getElementById('genres').value;
    const genres = genreInput.split(',').map(g => g.trim());

    fetch('/recommend', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ genres: genres }),
    })
    .then(response => response.json())
    .then(data => {
        const resultDiv = document.getElementById('movie-details');
        
        if (data.error) {
            resultDiv.innerHTML = `<p>Error: ${data.error}</p>`;
        } else {
            // Debugging: Log movie details
            console.log('Movie Data:', data);
            console.log('Poster URL:', data.poster_url);

            // Set movie details
            document.getElementById('movie-name').textContent = `${data.title} (${data.release_year})`;
            document.getElementById('movie-year').textContent = `Release Year: ${data.release_year}`;
            document.getElementById('movie-rating').textContent = `Rating: ${data.rating}`;

            const posterImg = document.getElementById('poster');
            
            // Clear the previous image
            posterImg.src = '';  

            // Add a fallback image if the poster doesn't load
            const fallbackImage = 'https://via.placeholder.com/500x750/ff0000/ffffff?text=No+Image+Available';

            // Set the new image source with cache busting
            const uniquePosterUrl = `${data.poster_url}?${new Date().getTime()}`;
            posterImg.src = uniquePosterUrl;

            // Wait for the image to load and then display the rest of the movie details
            posterImg.onload = function() {
                console.log('Image loaded successfully');

                // Remove the 'hidden' class to display the movie details
                resultDiv.classList.remove('hidden');
                
                // Ensure visibility and opacity
                resultDiv.style.visibility = 'visible'; // Ensure the div is visible
                resultDiv.style.opacity = '1'; // Ensure full opacity
            };

            // If image fails to load, use the fallback image
            posterImg.onerror = function() {
                console.log('Image failed to load. Using fallback image.');
                posterImg.src = fallbackImage;  // Show fallback image
                
                // Remove the 'hidden' class to display the movie details
                resultDiv.classList.remove('hidden');
                resultDiv.style.visibility = 'visible'; // Ensure the div is visible
                resultDiv.style.opacity = '1'; // Ensure full opacity
            };
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});