/* ============================================================
   Endflo — spine prototype behaviour (index-spine.html only)
   Each section's spine segment draws itself as you scroll, so
   the line untangles in step with the story. Runs after site.js,
   which still handles reveals, the hero, and the inbox diagram.
   ============================================================ */

(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!window.gsap || reduceMotion) return; // line renders complete and static

  gsap.registerPlugin(ScrollTrigger);

  document.querySelectorAll('.spine-sec').forEach(function (sec) {
    var path = sec.querySelector('.sp-draw');
    if (!path) return;
    var len = path.getTotalLength();
    path.style.strokeDasharray = len;
    path.style.strokeDashoffset = len;
    gsap.to(path, {
      strokeDashoffset: 0,
      ease: 'none',
      scrollTrigger: {
        trigger: sec,
        start: 'top 78%',
        end: 'bottom 62%',
        scrub: 0.5
      }
    });
  });
})();
