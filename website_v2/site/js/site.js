/* ============================================================
   Endflo — site behaviour
   GSAP ScrollTrigger drives the "flow" visual language:
   lines draw themselves as you scroll, tangled strokes settle
   into straight ones, and content flows up into view.
   ============================================================ */

(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- lucide icons ---------- */
  if (window.lucide) {
    lucide.createIcons();
  }

  /* ---------- header state + mobile nav ---------- */
  var header = document.querySelector('.site-header');
  var onScroll = function () {
    header.classList.toggle('scrolled', window.scrollY > 24);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  var navToggle = document.querySelector('.nav-toggle');
  var mainNav = document.querySelector('.main-nav');
  if (navToggle && mainNav) {
    navToggle.addEventListener('click', function () {
      var open = mainNav.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  /* ---------- faq accordion (no gsap needed) ---------- */
  document.querySelectorAll('.faq-item').forEach(function (item) {
    var q = item.querySelector('.faq-q');
    var a = item.querySelector('.faq-a');
    q.addEventListener('click', function () {
      var isOpen = item.classList.contains('open');
      // close siblings so only one answer flows open at a time
      document.querySelectorAll('.faq-item.open').forEach(function (other) {
        other.classList.remove('open');
        other.querySelector('.faq-a').style.maxHeight = '0px';
        other.querySelector('.faq-q').setAttribute('aria-expanded', 'false');
      });
      if (!isOpen) {
        item.classList.add('open');
        a.style.maxHeight = a.scrollHeight + 'px';
        q.setAttribute('aria-expanded', 'true');
      }
    });
  });

  /* ---------- gsap ---------- */
  if (!window.gsap || reduceMotion) return; // content is fully visible without JS/motion

  gsap.registerPlugin(ScrollTrigger, MotionPathPlugin);
  gsap.defaults({ ease: 'power2.out' });

  /* scroll progress bar */
  var progress = document.querySelector('.scroll-progress');
  if (progress) {
    gsap.to(progress, {
      scaleX: 1,
      ease: 'none',
      scrollTrigger: { start: 0, end: 'max', scrub: 0.3 }
    });
  }

  /* generic rise-in reveals */
  gsap.utils.toArray('[data-reveal]').forEach(function (el) {
    gsap.from(el, {
      y: 36,
      autoAlpha: 0,
      duration: 0.9,
      scrollTrigger: { trigger: el, start: 'top 86%' }
    });
  });

  /* staggered groups (cards, list items) */
  gsap.utils.toArray('[data-reveal-group]').forEach(function (group) {
    gsap.from(group.children, {
      y: 32,
      autoAlpha: 0,
      duration: 0.8,
      stagger: 0.12,
      scrollTrigger: { trigger: group, start: 'top 84%' }
    });
  });

  /* ---------- helper: prep a path for draw-on animation ---------- */
  function prepDraw(path) {
    var len = path.getTotalLength();
    path.style.strokeDasharray = len;
    path.style.strokeDashoffset = len;
    return len;
  }

  /* ---------- hero: the flow line draws itself on load ---------- */
  var heroFlow = document.querySelector('.hero-flow');
  if (heroFlow) {
    var stroke = heroFlow.querySelector('.flow-stroke');
    var node = heroFlow.querySelector('.flow-node');
    var head = heroFlow.querySelector('.flow-head');
    var pulse = heroFlow.querySelector('.flow-pulse');
    prepDraw(stroke);

    var tl = gsap.timeline({ delay: 0.25 });
    tl.from('.hero .kicker', { y: 20, autoAlpha: 0, duration: 0.6 })
      .from('.hero h1', { y: 34, autoAlpha: 0, duration: 0.8 }, '-=0.35')
      .from('.hero .sub', { y: 26, autoAlpha: 0, duration: 0.7 }, '-=0.5')
      /* animate the wrapper, not .btn — buttons carry CSS transitions on
         opacity/transform which race GSAP's from() end-state capture */
      .from('.hero-cta', { y: 20, autoAlpha: 0, duration: 0.6 }, '-=0.45')
      .from(node, { scale: 0, transformOrigin: 'center', duration: 0.4, ease: 'back.out(2)' }, '-=0.2')
      .to(stroke, { strokeDashoffset: 0, duration: 1.6, ease: 'power2.inOut' }, '<0.1')
      .from(head, { scale: 0, transformOrigin: 'center left', duration: 0.35, ease: 'back.out(2)' }, '-=0.15')
      .from('.tools-strip', { autoAlpha: 0, duration: 0.8 }, '-=0.2');

    /* headline underlines: scribble under "mess", clean arrow under "flows" */
    document.querySelectorAll('.hero h1 svg.underline path').forEach(function (p) {
      var l = prepDraw(p);
      tl.to(p, { strokeDashoffset: 0, duration: 0.7, ease: 'power1.inOut' }, 1.1);
    });

    /* a quiet pulse travels the line forever — data flowing end to end */
    if (pulse && stroke) {
      gsap.set(pulse, { opacity: 1, scale: 0 });
      gsap.timeline({ repeat: -1, repeatDelay: 2.2, delay: 3 })
        .set(pulse, { scale: 1 })
        .to(pulse, {
          motionPath: { path: stroke, align: stroke, alignOrigin: [0.5, 0.5] },
          duration: 3.2,
          ease: 'power1.inOut'
        })
        .to(pulse, { scale: 0, duration: 0.25 }, '-=0.25');
    }
  }

  /* ---------- flow connectors: draw with scroll (scrub) ---------- */
  gsap.utils.toArray('.flow-connector').forEach(function (fc) {
    var path = fc.querySelector('path.draw');
    if (!path) return;
    prepDraw(path);
    var tl = gsap.timeline({
      scrollTrigger: {
        trigger: fc,
        start: 'top 88%',
        end: 'bottom 45%',
        scrub: 0.6
      }
    });
    tl.to(path, { strokeDashoffset: 0, ease: 'none' });
    var head = fc.querySelector('.head');
    if (head) {
      gsap.set(head, { scale: 0, transformOrigin: 'center' });
      tl.to(head, { scale: 1, duration: 0.15 }, '>-0.1');
    }
  });

  /* ---------- index: pinned "how it works" steps ---------- */
  var stepsFlow = document.querySelector('.steps-flow');
  if (stepsFlow) {
    var cards = gsap.utils.toArray('.step-card');

    ScrollTrigger.matchMedia({
      /* desktop: pin the section and flow through the three steps */
      '(min-width: 961px)': function () {
        var fill = stepsFlow.querySelector('.steps-line .fill');
        gsap.set(cards, { autoAlpha: 0.25, y: 24 });

        var tl = gsap.timeline({
          scrollTrigger: {
            trigger: stepsFlow,
            start: 'top 18%',
            end: '+=1400',
            pin: true,
            scrub: 0.5
          }
        });

        cards.forEach(function (card, i) {
          tl.to(fill, { scaleX: (i + 1) / cards.length, duration: 1, ease: 'none' }, i)
            .to(card, { autoAlpha: 1, y: 0, duration: 0.5 }, i + 0.3)
            .call(function () { card.classList.add('active'); }, null, i + 0.55);
        });
      },
      /* mobile: simple sequential reveals, no pinning */
      '(max-width: 960px)': function () {
        cards.forEach(function (card) {
          gsap.from(card, {
            autoAlpha: 0,
            y: 30,
            duration: 0.7,
            scrollTrigger: {
              trigger: card,
              start: 'top 85%',
              onEnter: function () { card.classList.add('active'); }
            }
          });
        });
      }
    });
  }

  /* ---------- how-it-works page: vertical timeline rail ---------- */
  var timeline = document.querySelector('.timeline');
  if (timeline) {
    var railFill = timeline.querySelector('.rail-fill');
    gsap.to(railFill, {
      scaleY: 1,
      ease: 'none',
      scrollTrigger: {
        trigger: timeline,
        start: 'top 62%',
        end: 'bottom 62%',
        scrub: 0.4
      }
    });
    gsap.utils.toArray('.tl-step').forEach(function (step) {
      gsap.from(step, {
        autoAlpha: 0,
        x: -28,
        duration: 0.7,
        scrollTrigger: {
          trigger: step,
          start: 'top 72%',
          onEnter: function () { step.classList.add('active'); },
          onLeaveBack: function () { step.classList.remove('active'); }
        }
      });
    });
  }

  /* ---------- closing cta: straight line + arrow, then button ---------- */
  var closingFlow = document.querySelector('.closing-flow');
  if (closingFlow) {
    var cPath = closingFlow.querySelector('.flow-stroke');
    var cHead = closingFlow.querySelector('.head');
    prepDraw(cPath);
    gsap.set(cHead, { scale: 0, transformOrigin: 'center' });
    gsap.timeline({
      scrollTrigger: { trigger: closingFlow, start: 'top 80%' }
    })
      .to(cPath, { strokeDashoffset: 0, duration: 1, ease: 'power2.inOut' })
      .to(cHead, { scale: 1, duration: 0.3, ease: 'back.out(2)' }, '-=0.1');
  }
})();
