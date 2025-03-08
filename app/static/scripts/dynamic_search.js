let searchTimeout;

function searchMovies() {
    clearTimeout(searchTimeout);

    searchTimeout = setTimeout(() => {
        let searchTerm = document.getElementById("search").value.trim();
        let resultsDiv = document.getElementById("searchResults");

        if (searchTerm.length < 2) {
            resultsDiv.style.display = "none";
            return;
        }

        resultsDiv.innerHTML = "<p class='dropdown-item'>Searching...</p>";
        resultsDiv.style.display = "block";

        fetch(`/search_movies_json?q=${encodeURIComponent(searchTerm)}`)
            .then(response => response.json())
            .then(data => {
                if (data.length === 0) {
                    resultsDiv.innerHTML = "<p class='dropdown-item'>No results found.</p>";
                    return;
                }

                resultsDiv.innerHTML = "";
                
                data.forEach(movie => {
                    let item = document.createElement("div");
                    item.classList.add("dropdown-item");
                    item.innerHTML = `
                        ${movie.poster_url ? `<img src="${movie.poster_url || '/static/images/No-Image-Placeholder.svg'}
                        " alt="${movie.title}" class="movie-poster">` : ''}
                        <strong>${movie.title}</strong> (${movie.year})
                    `;
                    item.onclick = () => addMovie(movie);
                    resultsDiv.appendChild(item);
                });
            })
            .catch(error => {
                console.error("Error:", error);
                resultsDiv.innerHTML = "<p class='dropdown-item'>An error occurred. Please try again.</p>";
            });
    }, 300);
}

function addMovie(movie) {
    let selectedList = document.getElementById("selectedMovies");
    let moviesInput = document.getElementById("moviesInput");

    if (Array.from(selectedList.children).some(li => li.dataset.movieId == movie.id)) {
        return;
    }

    let placeholder = selectedList.querySelector(".placeholder");
    if (placeholder) {
        selectedList.removeChild(placeholder);
    }

    let listItem = document.createElement("li");
    listItem.textContent = `${movie.title} (${movie.year})`;
    listItem.dataset.movieId = movie.id;
    listItem.dataset.posterUrl = movie.poster_url;

    let removeButton = document.createElement("button");
    removeButton.textContent = "❌";
    removeButton.onclick = function () {
        selectedList.removeChild(listItem);
        updateMoviesInput();
        updateBackgroundOptions();
        if (selectedList.children.length === 0) {
            selectedList.innerHTML = "<li class='placeholder'>No movies selected yet. Search and add movies above.</li>";
        }
    };

    listItem.appendChild(removeButton); 
    selectedList.appendChild(listItem);
    updateMoviesInput();
    updateBackgroundOptions(); 
    
    document.getElementById("searchResults").style.display = "none";
    document.getElementById("search").value = "";
}

function updateMoviesInput() {
    let selectedMovies = Array.from(document.querySelectorAll("#selectedMovies li"))
        .map(li => li.dataset.movieId);

    document.getElementById("moviesInput").value = selectedMovies.join(",");
}