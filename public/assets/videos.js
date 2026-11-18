/* ============================================================
   LESSON VIDEOS — the only file you need to edit to add a video.

   Paste each lesson's YouTube link between the quotes.
   A full link works:  "https://www.youtube.com/watch?v=abc123XYZ_0"
   So does a short one: "https://youtu.be/abc123XYZ_0"
   Leave it as "" and the page shows "Video coming soon".

   One link here updates both the lesson page and the
   thumbnail on the landing page.
   ============================================================ */
var LESSON_VIDEOS = {
  1: "",
  2: "",
  3: "",
  4: "",
  5: "",
  6: "",
  7: ""
};

/* ---- nothing to edit below this line ---- */
(function () {
  function videoId(value) {
    if (!value) return "";
    value = String(value).trim();
    var m = value.match(/(?:v=|youtu\.be\/|embed\/|shorts\/|live\/)([A-Za-z0-9_-]{11})/);
    if (m) return m[1];
    return /^[A-Za-z0-9_-]{11}$/.test(value) ? value : "";
  }

  // Lesson page: swap the placeholder for the YouTube player.
  document.querySelectorAll(".video[data-lesson]").forEach(function (box) {
    var id = videoId(LESSON_VIDEOS[box.getAttribute("data-lesson")]);
    if (!id) return;
    var frame = document.createElement("iframe");
    frame.src = "https://www.youtube-nocookie.com/embed/" + id + "?rel=0";
    frame.title = "Lesson " + box.getAttribute("data-lesson") + " class video";
    frame.loading = "lazy";
    frame.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";
    frame.referrerPolicy = "strict-origin-when-cross-origin";
    frame.allowFullscreen = true;
    box.innerHTML = "";
    box.appendChild(frame);
    box.classList.add("has-video");
  });

  // Landing page: show the YouTube thumbnail on each lesson card.
  document.querySelectorAll(".thumb[data-lesson]").forEach(function (thumb) {
    var id = videoId(LESSON_VIDEOS[thumb.getAttribute("data-lesson")]);
    if (!id) return;
    thumb.style.backgroundImage = "url(https://i.ytimg.com/vi/" + id + "/hqdefault.jpg)";
    thumb.classList.add("has-video");
  });
})();
