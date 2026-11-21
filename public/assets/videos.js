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
  1: "https://youtu.be/o2Ux-Ez19JU",
  2: "https://youtu.be/zAsUVkCNA-g",
  3: "https://youtu.be/lXfoW1qPrQ0",
  4: "https://youtu.be/8P3ZXcOG_ho",
  5: "https://youtu.be/3oZk5i2ucGA",
  6: "https://youtu.be/n1dQkXmoBCk",
  7: "https://youtu.be/ZsWu211SsHs"
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

  function player(box, id, autoplay) {
    var frame = document.createElement("iframe");
    frame.src = "https://www.youtube-nocookie.com/embed/" + id + "?rel=0" + (autoplay ? "&autoplay=1" : "");
    frame.title = "Lesson " + box.getAttribute("data-lesson") + " class video";
    frame.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";
    frame.referrerPolicy = "strict-origin-when-cross-origin";
    frame.allowFullscreen = true;
    box.innerHTML = "";
    box.appendChild(frame);
    box.classList.add("playing");
  }

  // Lesson page: the thumbnail gets a play button; clicking it loads the YouTube player.
  // With no thumbnail, the player loads straight away.
  document.querySelectorAll(".video[data-lesson]").forEach(function (box) {
    var n = box.getAttribute("data-lesson");
    var id = videoId(LESSON_VIDEOS[n]);
    if (!id) return;
    box.classList.add("has-video");
    if (!box.querySelector(".video-poster")) { player(box, id, false); return; }
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "play";
    btn.setAttribute("aria-label", "Play the Lesson " + n + " video");
    btn.addEventListener("click", function () { player(box, id, true); });
    box.appendChild(btn);
  });

  // Landing page: lesson cards with a video get a play button over the thumbnail.
  document.querySelectorAll(".thumb[data-lesson]").forEach(function (thumb) {
    if (videoId(LESSON_VIDEOS[thumb.getAttribute("data-lesson")])) thumb.classList.add("has-video");
  });
})();
