# Muscle Map Kit

A standalone, dependency-free muscle-map component: front and back body diagrams where every muscle is an individually addressable, individually colourable SVG path.

Nothing in this kit is wired to any application. It renders bodies and colours muscles — that is all it does. What you feed it and what you do with a click is entirely up to the code you write around it.

## What's inside

```
muscle-map-kit/
├── README.md
├── LICENSE                   MIT (from the upstream package)
├── preview.jpg               what the demo looks like
├── demo/
│   └── demo.html             open this in a browser — works from file://
├── js/
│   ├── muscle-map-data.js    all geometry as plain data (~130 KB)
│   └── muscle-map.js         the renderer (~8 KB, no dependencies)
├── svg/
│   ├── male-front.svg        static SVGs, one <path> per muscle,
│   ├── male-back.svg         each tagged id / data-slug / data-side
│   ├── female-front.svg
│   └── female-back.svg
└── data/
    ├── male-front.json       raw path strings grouped by muscle slug
    ├── male-back.json
    ├── female-front.json
    ├── female-back.json
    ├── outlines.json         the body outline stroke for each view
    ├── viewboxes.json        the SVG viewBox each view needs
    └── slugs.json            every muscle name used
```

Four independent ways in, depending on what suits you:

- **`demo/demo.html`** — see it work, poke at it.
- **`js/`** — drop both files in, call the API below.
- **`svg/`** — paste the SVG straight into a page and style it with CSS (`[data-slug="chest"] { fill: red }`).
- **`data/`** — ignore everything else and build your own renderer on the raw path strings.

## Quick start

```html
<script src="js/muscle-map-data.js"></script>
<script src="js/muscle-map.js"></script>

<div id="front" style="width:200px;height:400px"></div>

<script>
  var map = new MuscleMap(document.getElementById("front"), {
    gender: "male",
    side:   "front"
  });

  map.setActivation({ chest: 100, triceps: 100, deltoids: 50 });
  map.on("select", function (slug) { console.log("clicked", slug); });
</script>
```

Activation values are `0`–`100`. They are interpolated across the colour ramp, so `50` lands halfway between two stops rather than snapping to one.

## Options

| Option | Default | Meaning |
| --- | --- | --- |
| `gender` | `"male"` | `"male"` or `"female"` |
| `side` | `"front"` | `"front"` or `"back"` |
| `stops` | `["#9ca3af","#fbbf24","#f59e0b","#ef4444"]` | Colour ramp, low → high. Any length. |
| `inactive` | `"#9ca3af"` | Fill for muscles at 0 |
| `outline` | `"#dfdfdf"` | Body outline stroke; `null` to hide |
| `stroke` | `"none"` | Per-muscle stroke colour |
| `strokeWidth` | `0` | Per-muscle stroke width |
| `hidden` | `[]` | Slugs to omit entirely, e.g. `["hair","head"]` |
| `disabled` | `[]` | Slugs shown greyed and non-clickable |
| `interactive` | `true` | Whether clicks and hovers fire events |
| `fixedFills` | `{ hair: "#4b5563", head: "#8b93a1" }` | Slugs painted a fixed colour, excluded from the activation ramp |

`fixedFills` exists because hair and head are not muscles. Left on the normal ramp they take the inactive grey and disappear into the body, which looks wrong. The defaults give a dark hair cap over a lighter face — the usual look. Pass `fixedFills: {}` to switch it off, or `setFixed("hair", "#111827")` to change one at runtime.

## Methods

| Call | Does |
| --- | --- |
| `setActivation(obj)` | Replace all values, e.g. `{ chest: 100 }` |
| `setMuscle(slug, pct)` | Change one muscle |
| `clear()` | Reset everything to 0 |
| `setSide("back")` | Flip view |
| `setGender("female")` | Swap model |
| `setStops([...])` | Change the colour ramp |
| `setFixed(slug, color)` | Pin a slug to a colour; `null` unpins it |
| `on("select", fn)` | Click handler, receives the slug |
| `on("hover", fn)` | Hover handler, receives the slug |
| `toSVGString()` | Current SVG markup as a string |
| `MuscleMap.slugs()` | Every available muscle name |
| `MuscleMap.ramp(stops, pct)` | The colour function on its own |

`setActivation` and `setMuscle` recolour existing nodes rather than rebuilding the DOM, so they are cheap to call often. `setSide` and `setGender` do rebuild.

## Muscle slugs

Not every muscle exists in every view — you cannot see someone's chest from behind. Passing a slug that is absent from the current view is harmless; it is simply ignored.

**Male, front:** chest, obliques, abs, biceps, triceps, neck, trapezius, deltoids, adductors, quadriceps, knees, tibialis, calves, forearm, hands, ankles, feet, head, hair

**Male, back:** neck, trapezius, deltoids, upper-back, triceps, lower-back, forearm, gluteal, adductors, hamstring, calves, ankles, feet, hands, head, hair

**Female, front:** neck, trapezius, hair, deltoids, head, chest, biceps, triceps, obliques, abs, forearm, hands, adductors, quadriceps, knees, tibialis, calves, ankles, feet

**Female, back:** hair, neck, trapezius, deltoids, upper-back, lower-back, triceps, forearm, hands, gluteal, adductors, hamstring, calves, feet

Most muscles are split into `left` and `right` paths; a few are a single `common` path. The renderer colours both sides together. If you ever want them independent, the split is preserved in `data/*.json` and in the `data-side` attribute on every path.

## Notes and caveats

- Everything runs offline. There is no network call, no build step and no package manager involved. Opening `demo/demo.html` from your filesystem works.
- `muscle-map-data.js` and `muscle-map.js` are plain scripts and also export via `module.exports`, so a bundler can consume them too.
- The geometry was extracted from [`react-muscle-highlighter`](https://github.com/soroojshehryar/react-muscle-highlighter) v1.2.0, MIT licensed, which itself descends from [`react-native-body-highlighter`](https://github.com/HichamELBSI/react-native-body-highlighter). The code is MIT; the *artwork's* original author is not credited anywhere upstream. Fine for personal use — worth checking if this ever ships commercially.
- `LICENSE` is the upstream MIT licence and covers the geometry. The renderer and demo in this kit are yours to do whatever you like with.
