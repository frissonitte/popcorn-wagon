document.addEventListener('DOMContentLoaded', function () {
    let listSelect = document.getElementById('listSelect');
    let addButton = document.getElementById('addButton');

    if (listSelect && addButton) {
        listSelect.addEventListener('change', function () {
            addButton.disabled = this.value === '';
        });
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const likeIcon = document.getElementById('like-icon');
    const dislikeIcon = document.getElementById('dislike-icon');

    function toggleLikeDislike(action) {
        const movieId = document.querySelector("input[name='movieId']").value;

        fetch('/add_to_liked', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `movieId=${movieId}&action=${action}`,
        })
            .then((response) => response.text())
            .then(() => {
                if (action === 'LIKE') {
                    if (likeIcon.classList.contains('active-like')) {
                        likeIcon.classList.remove('active-like');
                    } else {
                        likeIcon.classList.add('active-like');
                        dislikeIcon.classList.remove('active-dislike');
                    }
                } else if (action === 'DISLIKE') {
                    if (dislikeIcon.classList.contains('active-dislike')) {
                        dislikeIcon.classList.remove('active-dislike');
                    } else {
                        dislikeIcon.classList.add('active-dislike');
                        likeIcon.classList.remove('active-like');
                    }
                }
            })
            .catch((error) => console.error('Error:', error));
    }

    window.toggleLikeDislike = toggleLikeDislike;
});
