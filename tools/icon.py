"""App icon in the 'rendered' style: close crop, volume from gradients,
character breaking the frame. Deliberately unlike the flat in-app Roo -
icons get looked at 12mm wide on a home screen, so the flat full-body
version reads as a smudge at that size."""

INK   = "#2A2233"
BAR   = "#332A46"

def icon_svg():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0.35" y2="1">
    <stop offset="0" stop-color="#FF8A4C"/><stop offset="0.55" stop-color="#FF6A3D"/>
    <stop offset="1" stop-color="#E8451F"/>
  </linearGradient>
  <radialGradient id="glow" cx="0.5" cy="0.36" r="0.62">
    <stop offset="0" stop-color="#FFC98F" stop-opacity="0.55"/>
    <stop offset="1" stop-color="#FFC98F" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="fur" x1="0.18" y1="0" x2="0.8" y2="1">
    <stop offset="0" stop-color="#9AA5D6"/><stop offset="0.5" stop-color="#7C88C0"/>
    <stop offset="1" stop-color="#5F6BA6"/>
  </linearGradient>
  <linearGradient id="furDark" x1="0.2" y1="0" x2="0.8" y2="1">
    <stop offset="0" stop-color="#7783BC"/><stop offset="1" stop-color="#525E98"/>
  </linearGradient>
  <linearGradient id="cream" x1="0.3" y1="0" x2="0.7" y2="1">
    <stop offset="0" stop-color="#FFFBF2"/><stop offset="1" stop-color="#FFE6C8"/>
  </linearGradient>
  <linearGradient id="band" x1="0" y1="0" x2="0.4" y2="1">
    <stop offset="0" stop-color="#FF8F5E"/><stop offset="1" stop-color="#E8451F"/>
  </linearGradient>
  <linearGradient id="steel" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#4C4166"/><stop offset="0.45" stop-color="#332A46"/>
    <stop offset="1" stop-color="#241E33"/>
  </linearGradient>
  <radialGradient id="eye" cx="0.35" cy="0.3" r="0.8">
    <stop offset="0" stop-color="#4A4060"/><stop offset="1" stop-color="{INK}"/>
  </radialGradient>
</defs>

<rect width="200" height="200" fill="url(#bg)"/>
<ellipse cx="100" cy="62" rx="126" ry="110" fill="url(#glow)"/>

<g transform="rotate(-3 100 100)">
  <!-- ears run off the top edge -->
  <path d="M58 52c-7-24-11-50-7-64 3-11 14-10 19 1 7 15 11 38 12 57z" fill="url(#furDark)"/>
  <path d="M61 45c-5-19-7-38-4-49 2-7 9-6 11 1 4 10 7 27 8 42z" fill="#FFC2AC"/>
  <path d="M142 52c7-24 11-50 7-64-3-11-14-10-19 1-7 15-11 38-12 57z" fill="url(#furDark)"/>
  <path d="M139 45c5-19 7-38 4-49-2-7-9-6-11 1-4 10-7 27-8 42z" fill="#FFC2AC"/>

  <!-- shoulders, mostly hidden behind the head -->
  <path d="M100 118c-38 0-60 26-62 60-1 10 0 18 1 24h122c1-6 2-14 1-24-2-34-24-60-62-60z" fill="url(#furDark)"/>

  <!-- arms down to the bar -->
  <path d="M62 126 57 148" stroke="url(#furDark)" stroke-width="30" stroke-linecap="round" fill="none"/>
  <path d="M138 126 143 148" stroke="url(#furDark)" stroke-width="30" stroke-linecap="round" fill="none"/>

  <!-- head: the whole icon, basically -->
  <ellipse cx="100" cy="80" rx="66" ry="59" fill="url(#fur)"/>
  <path d="M40 52a66 59 0 0 1 36-30c-17 9-29 24-33 39z" fill="#B7C0E8" opacity=".75"/>
  <path d="M42 50A66 59 0 0 1 60 29h80a66 59 0 0 1 18 21c-26 7-90 7-116 0z" fill="url(#cream)"/>
  <path d="M45.5 45A66 59 0 0 1 52 36h96a66 59 0 0 1 6.5 9c-24 5-84 5-109 0z" fill="url(#band)"/>

  <!-- muzzle -->
  <ellipse cx="100" cy="106" rx="40" ry="29" fill="url(#cream)"/>
  <ellipse cx="100" cy="89" rx="12.5" ry="9" fill="#2A2233"/>
  <ellipse cx="95.5" cy="86" rx="4" ry="2.6" fill="#6B6080" opacity=".85"/>
  <path d="M100 98v7" stroke="#2A2233" stroke-width="4.6" stroke-linecap="round"/>
  <path d="M100 105q-12 12-21 2" stroke="#2A2233" stroke-width="4.6" fill="none" stroke-linecap="round"/>
  <path d="M100 105q12 12 21 2" stroke="#2A2233" stroke-width="4.6" fill="none" stroke-linecap="round"/>

  <!-- eyes carry the whole thing at 40px -->
  <circle cx="69" cy="68" r="14.5" fill="url(#eye)"/>
  <circle cx="74" cy="62" r="5.6" fill="#fff"/>
  <circle cx="64.5" cy="74" r="2.6" fill="#fff" opacity=".6"/>
  <circle cx="131" cy="68" r="14.5" fill="url(#eye)"/>
  <circle cx="136" cy="62" r="5.6" fill="#fff"/>
  <circle cx="126.5" cy="74" r="2.6" fill="#fff" opacity=".6"/>
  <ellipse cx="46" cy="96" rx="13" ry="7.5" fill="#E8451F" opacity=".32"/>
  <ellipse cx="154" cy="96" rx="13" ry="7.5" fill="#E8451F" opacity=".32"/>

  <!-- barbell -->
  <rect x="-18" y="147" width="236" height="17" rx="8.5" fill="url(#steel)"/>
  <rect x="-18" y="149.5" width="236" height="4.5" rx="2.2" fill="#6B5C8C" opacity=".5"/>
  <rect x="-6" y="122" width="27" height="67" rx="12" fill="url(#steel)"/>
  <rect x="179" y="122" width="27" height="67" rx="12" fill="url(#steel)"/>
  <rect x="1" y="131" width="8" height="49" rx="4" fill="#7A6BA0" opacity=".5"/>
  <rect x="186" y="131" width="8" height="49" rx="4" fill="#7A6BA0" opacity=".5"/>

  <!-- paws over the bar -->
  <circle cx="57" cy="152" r="20" fill="url(#fur)"/>
  <path d="M40 146a20 20 0 0 1 14-13" stroke="#C3CBEC" stroke-width="5" stroke-linecap="round" fill="none" opacity=".7"/>
  <circle cx="143" cy="152" r="20" fill="url(#fur)"/>
  <path d="M126 146a20 20 0 0 1 14-13" stroke="#C3CBEC" stroke-width="5" stroke-linecap="round" fill="none" opacity=".7"/>
</g>

<!-- sweat -->
<path d="M178 34c5 7 8 11 8 15a8 8 0 0 1-16 0c0-4 3-8 8-15z" fill="#FFF6EC" opacity=".92"/>
<path d="M22 44c4 5 6 8 6 11a6 6 0 0 1-12 0c0-3 2-6 6-11z" fill="#FFF6EC" opacity=".85"/>
</svg>'''
