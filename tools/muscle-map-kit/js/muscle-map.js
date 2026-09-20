/*
 * muscle-map.js — zero-dependency SVG muscle map renderer.
 *
 * Geometry extracted from react-muscle-highlighter v1.2.0 (MIT).
 * This file adds only rendering; it makes no assumptions about your app.
 *
 * Usage (browser, plain <script>):
 *
 *   <script src="muscle-map-data.js"></script>
 *   <script src="muscle-map.js"></script>
 *   <script>
 *     var map = new MuscleMap(document.getElementById("front"), {
 *       gender: "male",
 *       side:   "front"
 *     });
 *     map.setActivation({ chest: 100, abs: 100, deltoids: 50 });
 *     map.on("select", function (slug) { console.log(slug); });
 *   </script>
 *
 * Activation values are 0–100. Colours are interpolated across `stops`.
 */
(function (root, factory) {
  if (typeof module !== "undefined" && module.exports) module.exports = factory();
  else root.MuscleMap = factory();
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  var NS = "http://www.w3.org/2000/svg";

  var DEFAULTS = {
    gender: "male",          // "male" | "female"
    side: "front",           // "front" | "back"
    // colour ramp, low -> high. Interpolated, so any number of stops works.
    stops: ["#9ca3af", "#fbbf24", "#f59e0b", "#ef4444"],
    inactive: "#9ca3af",     // fill when activation is 0 or missing
    outline: "#dfdfdf",      // body outline stroke; null hides it
    stroke: "none",          // per-muscle stroke
    strokeWidth: 0,
    hidden: [],              // slugs to omit entirely, e.g. ["hair", "head"]
    disabled: [],            // slugs rendered greyed and non-interactive
    interactive: true,
    // Slugs painted a fixed colour, excluded from the activation ramp.
    // Hair and head are not muscles — without this they vanish into the body.
    fixedFills: { hair: "#4b5563", head: "#8b93a1" }
  };

  function getData() {
    var d = (typeof MuscleMapData !== "undefined" && MuscleMapData) ||
            (typeof globalThis !== "undefined" && globalThis.MuscleMapData);
    if (!d) throw new Error("muscle-map: load muscle-map-data.js before muscle-map.js");
    return d;
  }

  function hexToRgb(h) {
    h = h.replace("#", "");
    if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
    return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
  }

  function rgbToHex(c) {
    return "#" + c.map(function (v) {
      var s = Math.max(0, Math.min(255, Math.round(v))).toString(16);
      return s.length === 1 ? "0" + s : s;
    }).join("");
  }

  /* Map 0–100 onto the colour ramp. */
  function ramp(stops, pct) {
    if (!(pct > 0)) return stops[0];
    if (pct >= 100) return stops[stops.length - 1];
    var seg = (stops.length - 1) * (pct / 100);
    var i = Math.floor(seg);
    var t = seg - i;
    var a = hexToRgb(stops[i]);
    var b = hexToRgb(stops[Math.min(i + 1, stops.length - 1)]);
    return rgbToHex([
      a[0] + (b[0] - a[0]) * t,
      a[1] + (b[1] - a[1]) * t,
      a[2] + (b[2] - a[2]) * t
    ]);
  }

  function MuscleMap(container, options) {
    if (!(this instanceof MuscleMap)) return new MuscleMap(container, options);
    if (!container) throw new Error("muscle-map: container element is required");

    this.container = container;
    this.opts = {};
    for (var k in DEFAULTS) this.opts[k] = DEFAULTS[k];
    for (var o in (options || {})) this.opts[o] = options[o];

    this.activation = {};
    this.listeners = { select: [], hover: [] };
    this.paths = {};   // slug -> [<path>]

    this.render();
  }

  MuscleMap.prototype.key = function () {
    return this.opts.gender + "-" + this.opts.side;
  };

  MuscleMap.prototype.render = function () {
    var DATA = getData();
    var key = this.key();
    var parts = DATA.bodies[key];
    if (!parts) throw new Error("muscle-map: no geometry for '" + key + "'");

    var self = this;
    this.paths = {};
    this.container.innerHTML = "";

    var svg = document.createElementNS(NS, "svg");
    svg.setAttribute("viewBox", DATA.viewBoxes[key]);
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", key.replace("-", " ") + " muscle map");
    svg.style.display = "block";
    svg.style.width = "100%";
    svg.style.height = "100%";

    if (this.opts.outline && DATA.outlines[key]) {
      var og = document.createElementNS(NS, "g");
      og.setAttribute("fill", "none");
      og.setAttribute("stroke", this.opts.outline);
      og.setAttribute("stroke-width", "2");
      og.setAttribute("stroke-linecap", "butt");
      var op = document.createElementNS(NS, "path");
      op.setAttribute("vector-effect", "non-scaling-stroke");
      op.setAttribute("d", DATA.outlines[key]);
      og.appendChild(op);
      svg.appendChild(og);
    }

    var body = document.createElementNS(NS, "g");
    body.setAttribute("class", "mm-body");

    parts.forEach(function (part) {
      if (self.opts.hidden.indexOf(part.slug) !== -1) return;
      var isDisabled = self.opts.disabled.indexOf(part.slug) !== -1;

      ["common", "left", "right"].forEach(function (side) {
        (part.path[side] || []).forEach(function (d) {
          var p = document.createElementNS(NS, "path");
          p.setAttribute("d", d);
          p.setAttribute("data-slug", part.slug);
          p.setAttribute("data-side", side);
          p.setAttribute("fill", self.opts.inactive);
          if (self.opts.stroke && self.opts.stroke !== "none") {
            p.setAttribute("stroke", self.opts.stroke);
            p.setAttribute("stroke-width", self.opts.strokeWidth);
          }
          if (self.opts.interactive && !isDisabled) {
            p.style.cursor = "pointer";
            p.addEventListener("click", function () { self.emit("select", part.slug); });
            p.addEventListener("mouseenter", function () { self.emit("hover", part.slug); });
          }
          if (isDisabled) p.style.opacity = "0.6";

          (self.paths[part.slug] || (self.paths[part.slug] = [])).push(p);
          body.appendChild(p);
        });
      });
    });

    svg.appendChild(body);
    this.container.appendChild(svg);
    this.svg = svg;
    this.paint();
    return this;
  };

  /* Recolour without rebuilding the DOM. */
  MuscleMap.prototype.paint = function () {
    var self = this;
    var fixed = this.opts.fixedFills || {};
    Object.keys(this.paths).forEach(function (slug) {
      var fill;
      if (Object.prototype.hasOwnProperty.call(fixed, slug)) {
        fill = fixed[slug];
      } else if (self.opts.disabled.indexOf(slug) !== -1) {
        fill = "#EBEBE4";
      } else {
        fill = ramp(self.opts.stops, self.activation[slug] || 0);
      }
      self.paths[slug].forEach(function (p) { p.setAttribute("fill", fill); });
    });
    return this;
  };

  /* Repaint one slug with a fixed colour, e.g. setFixed("hair", "#111"). */
  MuscleMap.prototype.setFixed = function (slug, color) {
    this.opts.fixedFills = this.opts.fixedFills || {};
    if (color === null) delete this.opts.fixedFills[slug];
    else this.opts.fixedFills[slug] = color;
    return this.paint();
  };

  /* { chest: 100, deltoids: 50 } — values 0–100. Replaces previous state. */
  MuscleMap.prototype.setActivation = function (map) {
    this.activation = map || {};
    return this.paint();
  };

  MuscleMap.prototype.setMuscle = function (slug, pct) {
    this.activation[slug] = pct;
    return this.paint();
  };

  MuscleMap.prototype.clear = function () {
    this.activation = {};
    return this.paint();
  };

  MuscleMap.prototype.setSide = function (side) {
    this.opts.side = side;
    return this.render();
  };

  MuscleMap.prototype.setGender = function (gender) {
    this.opts.gender = gender;
    return this.render();
  };

  MuscleMap.prototype.setStops = function (stops) {
    this.opts.stops = stops;
    return this.paint();
  };

  MuscleMap.prototype.on = function (event, fn) {
    if (this.listeners[event]) this.listeners[event].push(fn);
    return this;
  };

  MuscleMap.prototype.emit = function (event, arg) {
    (this.listeners[event] || []).forEach(function (fn) { fn(arg); });
  };

  /* Current SVG markup, e.g. to export or inline elsewhere. */
  MuscleMap.prototype.toSVGString = function () {
    return this.svg ? this.svg.outerHTML : "";
  };

  MuscleMap.slugs = function () { return getData().slugs.slice(); };
  MuscleMap.ramp = ramp;

  return MuscleMap;
});
