window.addEventListener('scroll', function () {
    const footer = document.querySelector('footer');
    const pagination = document.querySelector('.pagination');

    if (!pagination) {
        const isBottom =
            window.innerHeight + window.scrollY >= document.body.offsetHeight;
        footer.style.opacity = isBottom ? '1' : '0';
        return;
    }

    const paginationRect = pagination.getBoundingClientRect();
    const isPaginationVisible =
        paginationRect.top < window.innerHeight && paginationRect.bottom >= 0;

    if (isPaginationVisible) {
        footer.style.opacity = '0';
        footer.style.pointerEvents = 'none';
    } else {
        const isBottom =
            window.innerHeight + window.scrollY >= document.body.offsetHeight;
        footer.style.opacity = isBottom ? '1' : '0';
        footer.style.pointerEvents = 'auto';
    }
});
