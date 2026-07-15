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
      var pulseTl = gsap.timeline({ repeat: -1, repeatDelay: 2.2, delay: 3 })
        .set(pulse, { scale: 1 })
        .to(pulse, {
          motionPath: { path: stroke, align: stroke, alignOrigin: [0.5, 0.5] },
          duration: 3.2,
          ease: 'power1.inOut'
        })
        .to(pulse, { scale: 0, duration: 0.25 }, '-=0.25');

      /* task nodes flash amber as the pulse passes — work getting done.
         times approximate the eased pulse position at each node's x */
      var taskTimes = [1.8, 2.0, 2.2, 2.45];
      heroFlow.querySelectorAll('.flow-task').forEach(function (task, i) {
        pulseTl.to(task, {
          fill: '#E0973F',
          attr: { r: 7.5 },
          duration: 0.16,
          yoyo: true,
          repeat: 1,
          ease: 'power1.in'
        }, taskTimes[i]);
      });

      pulseTl.timeScale(1.35);
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

  /* ============================================================
     Workflow diagrams — each [data-anim] svg gets a looping
     timeline that only plays while it's on screen. Everything is
     hidden/reset inside the timeline itself, so without JS the
     diagrams render complete and static.
     ============================================================ */

  function loopWhenVisible(el, tl) {
    tl.timeScale(1.35).pause();
    ScrollTrigger.create({
      trigger: el,
      start: 'top 94%',
      onEnter: function () { tl.play(); },
      onEnterBack: function () { tl.play(); },
      onLeave: function () { tl.pause(); },
      onLeaveBack: function () { tl.pause(); }
    });
  }

  /* set a drawn path back to fully undrawn (function-based so one
     .set() call handles paths of different lengths) */
  var undrawn = { strokeDashoffset: function (i, t) { return t.getTotalLength(); } };

  var wfBuilders = {

    /* whatsapp messages -> endflo -> tasks + meetings */
    inbox: function (el) {
      var s = gsap.utils.selector(el);
      var flow = s('.ix-flow')[0];
      var bubbles = s('.ix-bubble');
      var tasks = s('.ix-task');
      var checks = s('.ix-check');
      var meet = s('.ix-meet');
      var meetDot = s('.ix-meet-dot')[0];
      var dot = s('.ix-dot')[0];
      checks.forEach(prepDraw);

      var tl = gsap.timeline({ repeat: -1, repeatDelay: 1.8 });
      tl.set(bubbles, { scale: 0, autoAlpha: 1, transformOrigin: '20% 80%' }, 0)
        .set(tasks.concat(meet), { autoAlpha: 0, x: -12 }, 0)
        .set(checks, undrawn, 0)
        .set(meetDot, { scale: 0, transformOrigin: 'center' }, 0)
        .set(dot, { scale: 0, x: 0, y: 0, transformOrigin: 'center' }, 0);

      function ride() {
        tl.set(dot, { x: 0, y: 0, scale: 1 })
          .to(dot, {
            motionPath: { path: flow, align: flow, alignOrigin: [0.5, 0.5] },
            duration: 0.9,
            ease: 'power1.inOut'
          })
          .set(dot, { scale: 0 });
      }

      tl.to(bubbles[0], { scale: 1, duration: 0.45, ease: 'back.out(1.7)' }, 0.3);
      ride();
      tl.to(tasks[0], { autoAlpha: 1, x: 0, duration: 0.4 }, '-=0.15')
        .to(checks[0], { strokeDashoffset: 0, duration: 0.3 });

      tl.to(bubbles[1], { scale: 1, duration: 0.45, ease: 'back.out(1.7)' }, '+=0.25');
      ride();
      tl.to(tasks[1], { autoAlpha: 1, x: 0, duration: 0.4 }, '-=0.15')
        .to(checks[1], { strokeDashoffset: 0, duration: 0.3 });

      tl.to(bubbles[2], { scale: 1, duration: 0.45, ease: 'back.out(1.7)' }, '+=0.25');
      ride();
      tl.to(meet, { autoAlpha: 1, x: 0, duration: 0.4 }, '-=0.15')
        .to(meetDot, { scale: 1, duration: 0.35, ease: 'back.out(2.5)' });

      tl.to(bubbles.concat(tasks).concat(meet), { autoAlpha: 0, duration: 0.5 }, '+=1.6');
      return tl;
    },

    /* order closes -> invoice writes itself -> reminder -> paid */
    invoice: function (el) {
      var s = gsap.utils.selector(el);
      var doc = s('.iv-doc')[0];
      var docLines = s('.iv-tl');
      var bell = s('.iv-bell')[0];
      var check = s('.iv-check')[0];
      var dot = s('.iv-dot')[0];
      docLines.forEach(prepDraw);
      prepDraw(check);

      var tl = gsap.timeline({ repeat: -1, repeatDelay: 1.6 });
      tl.set(doc, { scale: 0, transformOrigin: 'center' }, 0)
        .set(docLines, undrawn, 0)
        .set(check, undrawn, 0)
        .set(dot, { attr: { cx: 60 }, autoAlpha: 1 }, 0);

      tl.to(dot, { attr: { cx: 242 }, duration: 0.7, ease: 'power1.inOut' }, 0.3)
        .to(doc, { scale: 1, duration: 0.4, ease: 'back.out(1.6)' }, '-=0.15')
        .to(docLines, { strokeDashoffset: 0, duration: 0.25, stagger: 0.12 })
        .to(dot, { attr: { cx: 432 }, duration: 0.6, ease: 'power1.inOut' }, '+=0.2')
        .to(bell, { rotation: 13, svgOrigin: '432 24', duration: 0.09, yoyo: true, repeat: 5 }, '-=0.1')
        .to(dot, { attr: { cx: 590 }, duration: 0.6, ease: 'power1.inOut' }, '+=0.2')
        .to(check, { strokeDashoffset: 0, duration: 0.35 }, '-=0.1')
        .to(dot, { attr: { cx: 664 }, autoAlpha: 0, duration: 0.5 });
      return tl;
    },

    /* two systems sync both ways; the report builds itself */
    sync: function (el) {
      var s = gsap.utils.selector(el);
      var d1 = s('.ds-dot1')[0];
      var d2 = s('.ds-dot2')[0];
      var bars = s('.ds-bar');

      var tl = gsap.timeline({ repeat: -1, repeatDelay: 1.2 });
      tl.set(bars, { scaleY: 0, autoAlpha: 1, transformOrigin: '50% 100%' }, 0)
        .set(d1, { attr: { cx: 176 }, autoAlpha: 0 }, 0)
        .set(d2, { attr: { cx: 584 }, autoAlpha: 0 }, 0);

      tl.to(d1, { autoAlpha: 1, duration: 0.15 }, 0.2)
        .to(d1, { attr: { cx: 584 }, duration: 1.3, ease: 'power1.inOut' }, 0.2)
        .to(d1, { autoAlpha: 0, duration: 0.15 }, '-=0.15')
        .to(d2, { autoAlpha: 1, duration: 0.15 }, 0.5)
        .to(d2, { attr: { cx: 176 }, duration: 1.3, ease: 'power1.inOut' }, 0.5)
        .to(d2, { autoAlpha: 0, duration: 0.15 }, '-=0.15')
        .to(bars, { scaleY: 1, duration: 0.4, stagger: 0.14, ease: 'back.out(1.4)' }, '-=0.3')
        .to(bars, { autoAlpha: 0, duration: 0.4 }, '+=1.6');
      return tl;
    },

    /* welcome sequence goes out on schedule; team gets nudged */
    onboard: function (el) {
      var s = gsap.utils.selector(el);
      var msgs = s('.ob-msg');
      var bell = s('.ob-bell')[0];
      var dot = s('.ob-dot')[0];

      var tl = gsap.timeline({ repeat: -1, repeatDelay: 1.6 });
      tl.set(msgs, { scale: 0, autoAlpha: 1, transformOrigin: '50% 100%' }, 0)
        .set(dot, { attr: { cx: 60 }, autoAlpha: 1 }, 0);

      tl.to(dot, { attr: { cx: 230 }, duration: 0.55, ease: 'power1.inOut' }, 0.3)
        .to(msgs[0], { scale: 1, duration: 0.4, ease: 'back.out(1.7)' })
        .to(dot, { attr: { cx: 400 }, duration: 0.55, ease: 'power1.inOut' }, '+=0.15')
        .to(msgs[1], { scale: 1, duration: 0.4, ease: 'back.out(1.7)' })
        .to(dot, { attr: { cx: 570 }, duration: 0.55, ease: 'power1.inOut' }, '+=0.15')
        .to(msgs[2], { scale: 1, duration: 0.4, ease: 'back.out(1.7)' })
        .to(dot, { attr: { cx: 680 }, duration: 0.45, ease: 'power1.inOut' }, '+=0.15')
        .to(bell, { rotation: 13, svgOrigin: '680 42', duration: 0.09, yoyo: true, repeat: 5 }, '-=0.1')
        .to(dot, { autoAlpha: 0, duration: 0.3 })
        .to(msgs, { autoAlpha: 0, duration: 0.5 }, '+=1.4');
      return tl;
    },

    /* live count syncs to every channel; alert fires before zero */
    stock: function (el) {
      var s = gsap.utils.selector(el);
      var countEl = s('.st-count')[0];
      var alert = s('.st-alert')[0];
      var branches = s('path.wf-line');
      var d1 = s('.st-dot1')[0];
      var d2 = s('.st-dot2')[0];
      var counter = { v: 128 };

      function pushOut(at) {
        [d1, d2].forEach(function (d, i) {
          tl.set(d, { x: 0, y: 0, autoAlpha: 1 }, at)
            .to(d, {
              motionPath: { path: branches[i], align: branches[i], alignOrigin: [0.5, 0.5] },
              duration: 0.7,
              ease: 'power1.inOut'
            }, at)
            .to(d, { autoAlpha: 0, duration: 0.15 }, at + 0.55);
        });
      }

      var tl = gsap.timeline({ repeat: -1, repeatDelay: 1.4 });
      tl.set(counter, { v: 128 }, 0)
        .set(alert, { autoAlpha: 0 }, 0)
        .set([d1, d2], { autoAlpha: 0 }, 0)
        .to(counter, {
          v: 96,
          duration: 2.2,
          ease: 'none',
          snap: { v: 1 },
          onUpdate: function () { countEl.textContent = Math.round(counter.v); }
        }, 0.3);
      pushOut(0.5);
      pushOut(1.7);
      tl.to(alert, { autoAlpha: 1, duration: 0.18, yoyo: true, repeat: 4 }, 2.7)
        .set(alert, { autoAlpha: 1 }, 3.7)
        .to(counter, {
          v: 128,
          duration: 0.45,
          ease: 'power2.out',
          snap: { v: 1 },
          onUpdate: function () { countEl.textContent = Math.round(counter.v); }
        }, 4.6);
      pushOut(4.7);
      tl.to(alert, { autoAlpha: 0, duration: 0.3 }, 5.1);
      return tl;
    },

    /* request routes through approvers and lands in the log */
    approve: function (el) {
      var s = gsap.utils.selector(el);
      var badges = s('.ap-badge');
      var logLines = s('.ap-log .wf-text');
      var dot = s('.ap-dot')[0];
      logLines.forEach(prepDraw);

      var tl = gsap.timeline({ repeat: -1, repeatDelay: 1.6 });
      tl.set(badges, { scale: 0, transformOrigin: 'center' }, 0)
        .set(logLines, undrawn, 0)
        .set(dot, { attr: { cx: 166 }, autoAlpha: 1 }, 0);

      tl.to(dot, { attr: { cx: 318 }, duration: 0.55, ease: 'power1.inOut' }, 0.3)
        .set(dot, { autoAlpha: 0 })
        .to(badges[0], { scale: 1, duration: 0.4, ease: 'back.out(2)' })
        .set(dot, { attr: { cx: 364 }, autoAlpha: 1 }, '+=0.2')
        .to(dot, { attr: { cx: 496 }, duration: 0.5, ease: 'power1.inOut' })
        .set(dot, { autoAlpha: 0 })
        .to(badges[1], { scale: 1, duration: 0.4, ease: 'back.out(2)' })
        .set(dot, { attr: { cx: 542 }, autoAlpha: 1 }, '+=0.2')
        .to(dot, { attr: { cx: 646 }, duration: 0.45, ease: 'power1.inOut' })
        .set(dot, { autoAlpha: 0 })
        .to(logLines, { strokeDashoffset: 0, duration: 0.25, stagger: 0.12 });
      return tl;
    },

    /* task card rides from to-do -> in progress -> done, then checks off */
    pm: function (el) {
      var s = gsap.utils.selector(el);
      var card = s('.pm-card')[0];
      var check = s('.pm-check')[0];
      var tick = s('.pm-tick')[0];
      var dot = s('.pm-dot')[0];
      prepDraw(tick);

      var tl = gsap.timeline({ repeat: -1, repeatDelay: 1.6 });
      tl.set(card, { x: 0, autoAlpha: 1 }, 0)
        .set(check, { scale: 0, transformOrigin: 'center' }, 0)
        .set(tick, undrawn, 0)
        .set(dot, { attr: { cx: 160 }, autoAlpha: 1 }, 0);

      tl.to(dot, { attr: { cx: 310 }, duration: 0.5, ease: 'power1.inOut' }, 0.3)
        .set(dot, { autoAlpha: 0 })
        .to(card, { x: 290, duration: 0.4, ease: 'power1.inOut' }, '-=0.15')
        .set(dot, { attr: { cx: 450 }, autoAlpha: 1 }, '+=0.3')
        .to(dot, { attr: { cx: 600 }, duration: 0.5, ease: 'power1.inOut' })
        .set(dot, { autoAlpha: 0 })
        .to(card, { x: 580, autoAlpha: 0, duration: 0.35, ease: 'power1.inOut' }, '-=0.15')
        .to(check, { scale: 1, duration: 0.4, ease: 'back.out(2)' })
        .to(tick, { strokeDashoffset: 0, duration: 0.3 });
      return tl;
    },

    /* discovery call: conversation bubbles + a 30-minute clock */
    'hw-call': function (el) {
      var s = gsap.utils.selector(el);
      var bubs = s('.hc-bub');
      var hand = s('.hc-hand')[0];

      var tl = gsap.timeline({ repeat: -1, repeatDelay: 1.4 });
      tl.set(bubs, { scale: 0, autoAlpha: 1, transformOrigin: '20% 80%' }, 0)
        .set(hand, { rotation: 0, svgOrigin: '192 42' }, 0)
        .to(hand, { rotation: 180, duration: 3.4, ease: 'none' }, 0)
        .to(bubs[0], { scale: 1, duration: 0.4, ease: 'back.out(1.7)' }, 0.3)
        .to(bubs[1], { scale: 1, duration: 0.4, ease: 'back.out(1.7)' }, 1.2)
        .to(bubs[2], { scale: 1, duration: 0.4, ease: 'back.out(1.7)' }, 2.1)
        .to(bubs, { autoAlpha: 0, duration: 0.45 }, 3.4);
      return tl;
    },

    /* process mapping: scattered steps get joined into one flow */
    'hw-map': function (el) {
      var s = gsap.utils.selector(el);
      var path = s('.hm-path')[0];
      var nodes = s('.hm-node');
      var dot = s('.hm-dot')[0];
      prepDraw(path);

      var tl = gsap.timeline({ repeat: -1, repeatDelay: 1.4 });
      tl.set(nodes, { scale: 0, autoAlpha: 1, transformOrigin: 'center' }, 0)
        .set(path, undrawn, 0)
        .set(path, { autoAlpha: 1 }, 0)
        .set(dot, { scale: 0, x: 0, y: 0, transformOrigin: 'center' }, 0);

      tl.to(nodes, { scale: 1, duration: 0.35, stagger: 0.18, ease: 'back.out(2)' }, 0.3)
        .to(path, { strokeDashoffset: 0, duration: 0.9, ease: 'power1.inOut' }, '-=0.2')
        .set(dot, { scale: 1 })
        .to(dot, {
          motionPath: { path: path, align: path, alignOrigin: [0.5, 0.5] },
          duration: 1.1,
          ease: 'power1.inOut'
        })
        .set(dot, { scale: 0 })
        .to(nodes.concat(path), { autoAlpha: 0, duration: 0.45 }, '+=1.2');
      return tl;
    },

    /* build & test: pieces assemble, then a test run passes */
    'hw-build': function (el) {
      var s = gsap.utils.selector(el);
      var blocks = s('.hb-block');
      var check = s('.hb-check')[0];
      var dot = s('.hb-dot')[0];
      prepDraw(check);

      var tl = gsap.timeline({ repeat: -1, repeatDelay: 1.4 });
      tl.set(blocks, { y: -18, autoAlpha: 0 }, 0)
        .set(check, undrawn, 0)
        .set(check, { autoAlpha: 1 }, 0)
        .set(dot, { attr: { cx: 20 }, autoAlpha: 0 }, 0);

      tl.to(blocks, { y: 0, autoAlpha: 1, duration: 0.45, stagger: 0.16, ease: 'back.out(1.6)' }, 0.3)
        .to(dot, { autoAlpha: 1, duration: 0.15 }, '+=0.2')
        .to(dot, { attr: { cx: 220 }, duration: 0.9, ease: 'power1.inOut' }, '<')
        .to(dot, { autoAlpha: 0, duration: 0.15 }, '-=0.15')
        .to(check, { strokeDashoffset: 0, duration: 0.35 })
        .to(blocks.concat(check), { autoAlpha: 0, duration: 0.45 }, '+=1.4');
      return tl;
    },

    /* go live: dashed plan becomes a solid line with traffic on it */
    'hw-live': function (el) {
      var s = gsap.utils.selector(el);
      var solid = s('.hl-solid')[0];
      var pill = s('.hl-pill')[0];
      var beacon = s('.hl-beacon')[0];
      var dot = s('.hl-dot')[0];
      prepDraw(solid);

      var tl = gsap.timeline({ repeat: -1, repeatDelay: 1.2 });
      tl.set(pill, { scale: 0, autoAlpha: 1, transformOrigin: 'center' }, 0)
        .set(solid, undrawn, 0)
        .set(solid, { autoAlpha: 1 }, 0)
        .set(dot, { attr: { cx: 16 }, autoAlpha: 0 }, 0);

      tl.to(solid, { strokeDashoffset: 0, duration: 0.9, ease: 'power2.inOut' }, 0.3)
        .to(pill, { scale: 1, duration: 0.45, ease: 'back.out(1.8)' }, '-=0.2')
        .to(beacon, { scale: 1.7, transformOrigin: 'center', duration: 0.35, yoyo: true, repeat: 5, ease: 'power1.inOut' });
      [0, 1].forEach(function (i) {
        tl.set(dot, { attr: { cx: 16 }, autoAlpha: 1 }, 1.7 + i * 1.2)
          .to(dot, { attr: { cx: 224 }, duration: 1, ease: 'power1.inOut' }, 1.7 + i * 1.2)
          .to(dot, { autoAlpha: 0, duration: 0.15 }, 2.55 + i * 1.2);
      });
      tl.to([solid, pill], { autoAlpha: 0, duration: 0.45 }, '+=0.8');
      return tl;
    },

    /* ongoing support: a steady heartbeat, quietly watched */
    'hw-support': function (el) {
      var s = gsap.utils.selector(el);
      var beat = s('.hs-beat')[0];
      var pupil = s('.hs-pupil')[0];
      var dot = s('.hs-dot')[0];
      prepDraw(beat);

      var tl = gsap.timeline({ repeat: -1, repeatDelay: 1 });
      tl.set(beat, undrawn, 0)
        .set(beat, { autoAlpha: 1 }, 0)
        .set(dot, { scale: 0, x: 0, y: 0, transformOrigin: 'center' }, 0);

      tl.to(beat, { strokeDashoffset: 0, duration: 1.1, ease: 'power1.inOut' }, 0.2)
        .set(dot, { scale: 1 }, 0.2)
        .to(dot, {
          motionPath: { path: beat, align: beat, alignOrigin: [0.5, 0.5] },
          duration: 1.3,
          ease: 'power1.inOut'
        }, 0.3)
        .set(dot, { scale: 0 })
        .to(pupil, { x: -5, duration: 0.4, ease: 'power1.inOut' }, 0.5)
        .to(pupil, { x: 5, duration: 0.5, ease: 'power1.inOut' }, 1.1)
        .to(pupil, { x: 0, duration: 0.4, ease: 'power1.inOut' }, 1.8)
        .to(beat, { autoAlpha: 0, duration: 0.4 }, '+=1.2');
      return tl;
    }
  };

  document.querySelectorAll('[data-anim]').forEach(function (el) {
    var build = wfBuilders[el.getAttribute('data-anim')];
    if (build) loopWhenVisible(el, build(el));
  });

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
