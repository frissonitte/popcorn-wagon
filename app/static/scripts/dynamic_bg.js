function updateBackgroundOptions() {
    let backgroundOptions = document.getElementById("backgroundOptions");
    backgroundOptions.innerHTML = "";

    let selectedMovies = Array.from(document.querySelectorAll("#selectedMovies li"))
        .map(li => {
            return {
                id: li.dataset.movieId,
                title: li.textContent.split("❌")[0].trim(), 
                backdrop_url: li.dataset.backdropUrl || li.dataset.posterUrl || "{{ url_for('static', filename='images/No-Image-Placeholder.svg') }}"
            };
        });

    selectedMovies.forEach(movie => {
        let option = document.createElement("div");
        option.classList.add("background-option");
        option.dataset.posterUrl = movie.backdrop_url;
        option.innerHTML = `
            <img src="${movie.backdrop_url}" alt="${movie.title}" class="background-poster">
            <div class="selected-overlay">Selected</div>
            <button type="button" onclick="selectBackground('${movie.backdrop_url}')">Select as Background</button>
        `;
        backgroundOptions.appendChild(option);
    });
}

function selectBackground(posterUrl) {
    if (!posterUrl || posterUrl === "null") {
        posterUrl = "{{ url_for('static', filename='images/No-Image-Placeholder.svg') }}";
    }

    console.log("Selected background:", posterUrl);
    document.getElementById("background_image").value = posterUrl;

    let backgroundOptions = document.querySelectorAll(".background-option");

    backgroundOptions.forEach(option => {
        if (option.dataset.posterUrl === posterUrl) {
            option.classList.add("selected");
        } else {
            option.classList.remove("selected");
        }
    });
}
