(function () {
  const deck = document.getElementById("deck");
  if (!deck) {
    return;
  }

  const slides = Array.from(deck.querySelectorAll(".slide"));
  let slideIndex = 0;
  let fragmentIndex = -1;

  function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
  }

  function getFragmentsForSlide(index) {
    return Array.from(slides[index].querySelectorAll("[data-fragment-order]")).sort((a, b) => {
      return Number(a.dataset.fragmentOrder) - Number(b.dataset.fragmentOrder);
    });
  }

  function syncHash() {
    window.location.hash = `#/${slideIndex}/${Math.max(fragmentIndex, -1)}`;
  }

  function showState() {
    slides.forEach((slide, idx) => {
      slide.classList.toggle("is-active", idx === slideIndex);
      slide.classList.toggle("is-before", idx < slideIndex);
      slide.classList.toggle("is-after", idx > slideIndex);
    });

    const fragments = getFragmentsForSlide(slideIndex);
    fragments.forEach((fragment, idx) => {
      fragment.classList.toggle("is-hidden", idx > fragmentIndex);
    });
  }

  function applyHash() {
    const hash = window.location.hash.replace(/^#/, "");
    const match = hash.match(/^\/(\d+)(?:\/(-?\d+))?$/);
    if (!match) {
      showState();
      return;
    }

    const nextSlide = clamp(Number(match[1]), 0, slides.length - 1);
    const fragments = getFragmentsForSlide(nextSlide);
    const requestedFragment = match[2] === undefined ? -1 : Number(match[2]);
    const nextFragment = clamp(requestedFragment, -1, fragments.length - 1);

    slideIndex = nextSlide;
    fragmentIndex = nextFragment;
    showState();
  }

  function next() {
    const fragments = getFragmentsForSlide(slideIndex);
    if (fragmentIndex < fragments.length - 1) {
      fragmentIndex += 1;
      showState();
      syncHash();
      return;
    }

    if (slideIndex < slides.length - 1) {
      slideIndex += 1;
      fragmentIndex = -1;
      showState();
      syncHash();
    }
  }

  function prev() {
    const fragments = getFragmentsForSlide(slideIndex);
    if (fragmentIndex >= 0 && fragments.length > 0) {
      fragmentIndex -= 1;
      showState();
      syncHash();
      return;
    }

    if (slideIndex > 0) {
      slideIndex -= 1;
      const previousFragments = getFragmentsForSlide(slideIndex);
      fragmentIndex = previousFragments.length - 1;
      showState();
      syncHash();
    }
  }

  document.addEventListener("keydown", (event) => {
    if (event.key === "ArrowRight" || event.key === " " || event.key === "PageDown") {
      event.preventDefault();
      next();
    } else if (event.key === "ArrowLeft" || event.key === "Backspace" || event.key === "PageUp") {
      event.preventDefault();
      prev();
    }
  });

  document.addEventListener("click", () => next());
  window.addEventListener("hashchange", applyHash);

  applyHash();
  syncHash();
  deck.focus();
})();

