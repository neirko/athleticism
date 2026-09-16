"""Adds Reps-in-Reserve / RPE as a tracking field category, plus the
hover-and-hold explanation popover. Imported by build.py."""

CSS = r"""
/* ------------------------------------------------ effort fields (RIR/RPE) */
[data-info]{-webkit-touch-callout:none;-webkit-user-select:none;user-select:none;}
.field-info{display:inline-flex;align-items:center;gap:4px;background:none;border:none;padding:0;
  font:inherit;color:inherit;letter-spacing:inherit;cursor:help;border-radius:6px;}
.field-info .fi-dot{display:inline-flex;align-items:center;justify-content:center;width:13px;height:13px;
  border-radius:50%;border:1.5px solid currentColor;font-size:9px;font-weight:800;line-height:1;
  opacity:.65;transition:opacity .14s ease;font-family:var(--font-ui);}
.field-info:hover,.field-info[aria-describedby]{color:var(--accent);}
.field-info:hover .fi-dot,.field-info[aria-describedby] .fi-dot{opacity:1;}
.chip .field-info{cursor:help;}

.field-pop{position:fixed;z-index:60;width:min(272px,calc(100vw - 24px));background:var(--surface);
  border:2px solid var(--border);border-radius:18px;padding:14px 16px;box-shadow:var(--shadow-md);
  text-align:left;pointer-events:none;opacity:0;transform:translateY(-5px) scale(.97);
  transform-origin:top center;transition:opacity .14s ease,transform .14s cubic-bezier(.34,1.4,.64,1);}
.field-pop.in{opacity:1;transform:none;}
.field-pop.flip{transform-origin:bottom center;}
.field-pop::after{content:"";position:absolute;left:var(--arrow-x,50%);top:-8px;width:13px;height:13px;
  margin-left:-7px;background:var(--surface);border-left:2px solid var(--border);border-top:2px solid var(--border);
  transform:rotate(45deg);border-radius:3px 0 0 0;}
.field-pop.flip::after{top:auto;bottom:-8px;border-left:none;border-top:none;
  border-right:2px solid var(--border);border-bottom:2px solid var(--border);border-radius:0 0 3px 0;}
.fi-title{font-family:var(--font-display);font-size:16.5px;font-weight:700;color:var(--text);margin-bottom:3px;}
.fi-body{font-size:12.5px;font-weight:600;color:var(--text-dim);line-height:1.5;}
.fi-scale{display:grid;gap:5px;margin-top:11px;padding-top:11px;border-top:2px solid var(--border);}
.fi-scale-row{display:flex;align-items:baseline;gap:9px;font-size:12.5px;font-weight:600;color:var(--text-dim);line-height:1.35;}
.fi-key{flex:0 0 46px;text-align:center;font-size:11.5px;font-weight:800;color:var(--accent-deep);
  background:var(--accent-soft);border-radius:8px;padding:3px 0;}
.fi-foot{font-size:11.5px;font-weight:700;color:var(--text-faint);margin-top:10px;}
"""

# ---------------------------------------------------------------- JS pieces

INFO_DATA = r"""
/* Effort fields. RIR and RPE record the same thing on inverted scales, so the
   explanation has to travel with the column - you read it mid-set, months after
   you set the exercise up. FIELD_INFO feeds both the popover and the input hints. */
var FIELD_INFO = {
  rir: {
    title: 'Reps in Reserve',
    body: 'How many more reps you could have done before form broke down. Log it right after the set, while it is still fresh.',
    scale: [['0','Nothing left - true failure'],['1','One more rep, maybe'],['2','Two solid reps left'],
            ['3-4','Comfortable, still productive'],['5+','Warm-up or technique work']],
    foot: 'Lower means harder.'
  },
  rpe: {
    title: 'Rate of Perceived Exertion',
    body: 'How hard the set felt on the lifting scale. It is the mirror of reps in reserve: RPE = 10 minus RIR.',
    scale: [['10','No reps left at all'],['9','One rep left'],['8','Two reps left'],
            ['7','Three reps left'],['\u2264 6','Easy - warm-up territory']],
    foot: 'Higher means harder. Half points are fine (8.5).'
  }
};
function isEffortType(t){ return t==='rir' || t==='rpe'; }
function clampEffort(type, n){
  if (type==='rir') return Math.max(0, Math.min(10, Math.round(n)));
  if (type==='rpe') return Math.max(1, Math.min(10, Math.round(n*2)/2));
  return n;
}
function effortPlaceholder(type){
  if (type==='rir') return '0-5';
  if (type==='rpe') return '6-10';
  return '\u2014';
}
function fieldHeaderCell(f, unit){
  var label = esc(f.label)+fieldUnitSuffix(f, unit);
  if (!FIELD_INFO[f.type]) return '<th>'+label+'</th>';
  return '<th><span class="field-info" data-info="'+f.type+'" role="button" tabindex="0" '+
    'aria-label="'+esc(FIELD_INFO[f.type].title)+' - what is this?">'+label+
    '<span class="fi-dot" aria-hidden="true">i</span></span></th>';
}
"""

POPOVER = r"""
/* ---- field explanation popover -----------------------------------------
   Hover on a mouse, tap or press-and-hold on touch. Built as a real element
   rather than title= so it works on iOS, matches the design, and can carry
   the whole scale rather than one line of text. */
var infoPop = { el:null, anchor:null, holdT:null };
function fieldInfoHTML(key){
  var d = FIELD_INFO[key];
  return '<div class="fi-title">'+esc(d.title)+'</div>'+
    '<div class="fi-body">'+esc(d.body)+'</div>'+
    '<div class="fi-scale">'+d.scale.map(function(s){
      return '<div class="fi-scale-row"><span class="fi-key">'+esc(s[0])+'</span><span>'+esc(s[1])+'</span></div>';
    }).join('')+'</div>'+
    (d.foot?('<div class="fi-foot">'+esc(d.foot)+'</div>'):'');
}
function positionFieldInfo(){
  var el = infoPop.el, a = infoPop.anchor;
  if (!el || !a || !a.isConnected) return;
  var r = a.getBoundingClientRect(), m = 12;
  var w = el.offsetWidth, h = el.offsetHeight;
  var left = Math.max(m, Math.min(r.left + r.width/2 - w/2, window.innerWidth - w - m));
  var top = r.bottom + 10;
  var flip = (top + h > window.innerHeight - m) && (r.top - h - 10 >= m);
  if (flip) top = r.top - h - 10;
  top = Math.max(m, Math.min(top, window.innerHeight - h - m));
  el.style.left = left+'px';
  el.style.top = top+'px';
  el.classList.toggle('flip', flip);
  el.style.setProperty('--arrow-x', Math.max(16, Math.min(r.left + r.width/2 - left, w-16))+'px');
}
function hideFieldInfo(){
  clearTimeout(infoPop.holdT);
  if (infoPop.anchor) infoPop.anchor.removeAttribute('aria-describedby');
  if (infoPop.el && infoPop.el.parentNode) infoPop.el.parentNode.removeChild(infoPop.el);
  infoPop.el = null; infoPop.anchor = null;
}
function showFieldInfo(anchor){
  var key = anchor.getAttribute('data-info');
  if (!FIELD_INFO[key]) return;
  if (infoPop.anchor === anchor) return;
  hideFieldInfo();
  var el = document.createElement('div');
  el.className = 'field-pop';
  el.id = 'field-pop';
  el.setAttribute('role','tooltip');
  el.innerHTML = fieldInfoHTML(key);
  document.body.appendChild(el);
  infoPop.el = el; infoPop.anchor = anchor;
  anchor.setAttribute('aria-describedby','field-pop');
  positionFieldInfo();
  requestAnimationFrame(function(){ if (infoPop.el===el) el.classList.add('in'); });
}
function infoAnchorFrom(e){
  var t = e.target;
  return (t && t.closest) ? t.closest('[data-info]') : null;
}
document.addEventListener('pointerover', function(e){
  if (e.pointerType && e.pointerType!=='mouse') return;
  var a = infoAnchorFrom(e);
  if (a) showFieldInfo(a);
});
document.addEventListener('pointerout', function(e){
  if (e.pointerType && e.pointerType!=='mouse') return;
  var a = infoAnchorFrom(e);
  if (a && a===infoPop.anchor && !a.contains(e.relatedTarget)) hideFieldInfo();
});
document.addEventListener('pointerdown', function(e){
  var a = infoAnchorFrom(e);
  if (!a){ hideFieldInfo(); return; }
  if (e.pointerType==='mouse') return;
  clearTimeout(infoPop.holdT);
  infoPop.holdT = setTimeout(function(){ showFieldInfo(a); }, 380);
}, true);
['pointerup','pointercancel','pointerleave'].forEach(function(evt){
  document.addEventListener(evt, function(){ clearTimeout(infoPop.holdT); }, true);
});
/* Capture phase: a tap on the label must not fall through to the app's own
   click handling, and a tap anywhere else closes the popover. */
document.addEventListener('click', function(e){
  var a = infoAnchorFrom(e);
  if (!a) return;
  e.preventDefault(); e.stopPropagation();
  if (infoPop.anchor===a) hideFieldInfo(); else showFieldInfo(a);
}, true);
document.addEventListener('keydown', function(e){
  if (e.key==='Escape' && infoPop.el){ hideFieldInfo(); return; }
  var a = infoAnchorFrom(e);
  if (a && (e.key==='Enter' || e.key===' ')){
    e.preventDefault();
    if (infoPop.anchor===a) hideFieldInfo(); else showFieldInfo(a);
  }
});
document.addEventListener('focusout', function(e){
  if (e.target && e.target===infoPop.anchor) hideFieldInfo();
});
window.addEventListener('scroll', function(){ if (infoPop.el) hideFieldInfo(); }, true);
window.addEventListener('resize', function(){ if (infoPop.el) positionFieldInfo(); });
"""


def apply(src):
    def rep(old, new, n=1, why=""):
        nonlocal src
        assert src.count(old) == n, "expected %d of %r, found %d (%s)" % (n, old[:70], src.count(old), why)
        src = src.replace(old, new)

    # 1. register the two new types
    rep("var FIELD_TYPE_NAMES = {weight:'Weight', assisted:'Assisted', reps:'Reps', "
        "timer:'Target Time', time:'Measured Time', number:'Number', text:'Text'};",
        "var FIELD_TYPE_NAMES = {weight:'Weight', assisted:'Assisted', reps:'Reps', "
        "timer:'Target Time', time:'Measured Time', rir:'Reps in Reserve', rpe:'RPE', "
        "number:'Number', text:'Text'};")

    # 2. helpers + popover, dropped in next to the other field utilities
    rep("function isTimeType(t){ return t==='time' || t==='timer'; }",
        "function isTimeType(t){ return t==='time' || t==='timer'; }\n" + INFO_DATA.strip())

    # 3. shared header cell, used by all three set tables
    rep("var headerCols = '<th></th>' + fields.map(function(f){ return '<th>'+esc(f.label)+fieldUnitSuffix(f, unit)+'</th>'; }).join('') + '<th>Rest</th><th></th>';",
        "var headerCols = '<th></th>' + fields.map(function(f){ return fieldHeaderCell(f, unit); }).join('') + '<th>Rest</th><th></th>';")
    rep("""  var headerCols = '<th></th>' + wex.fields.map(function(f){
    return '<th>'+esc(f.label)+fieldUnitSuffix(f, unit)+'</th>';
  }).join('') + '<th>Rest</th><th></th><th></th>';""",
        """  var headerCols = '<th></th>' + wex.fields.map(function(f){
    return fieldHeaderCell(f, unit);
  }).join('') + '<th>Rest</th><th></th><th></th>';""")
    rep("""    var headerCols = '<th></th>' + wex.fields.map(function(f){
      return '<th>'+esc(f.label)+fieldUnitSuffix(f, unit)+'</th>';
    }).join('');""",
        """    var headerCols = '<th></th>' + wex.fields.map(function(f){
      return fieldHeaderCell(f, unit);
    }).join('');""")

    # 4. scale-aware input hints, live workout + plan editor
    rep("""      cells += '<td><input class="num-input" data-commit="set-num" data-type="'+f.type+'" data-wex="'+wexIdx+'" data-set="'+idx+'" data-field="'+f.id+'" inputmode="decimal" value="'+esc(currentDisplay)+'" placeholder="'+esc(placeholderDisplay||'\\u2014')+'"></td>';""",
        """      cells += '<td><input class="num-input" data-commit="set-num" data-type="'+f.type+'" data-wex="'+wexIdx+'" data-set="'+idx+'" data-field="'+f.id+'" inputmode="'+(f.type==='rir'?'numeric':'decimal')+'" value="'+esc(currentDisplay)+'" placeholder="'+esc(placeholderDisplay||effortPlaceholder(f.type))+'"></td>';""")
    rep("""      cells += '<td><input class="num-input" data-plan-commit="set-num" data-type="'+f.type+'" data-idx="'+idx+'" data-set="'+sIdx+'" data-field="'+f.id+'" inputmode="decimal" value="'+esc(currentDisplay)+'" placeholder="\\u2014"></td>';""",
        """      cells += '<td><input class="num-input" data-plan-commit="set-num" data-type="'+f.type+'" data-idx="'+idx+'" data-set="'+sIdx+'" data-field="'+f.id+'" inputmode="'+(f.type==='rir'?'numeric':'decimal')+'" value="'+esc(currentDisplay)+'" placeholder="'+esc(effortPlaceholder(f.type))+'"></td>';""")

    # 5. clamp to the scale on commit (both the plan editor and the live workout)
    rep("""        else if (field.type==='reps') set.values[field.id] = Math.round(n);
        else set.values[field.id] = n;""",
        """        else if (field.type==='reps') set.values[field.id] = Math.round(n);
        else if (isEffortType(field.type)) set.values[field.id] = clampEffort(field.type, n);
        else set.values[field.id] = n;""")
    rep("""          else if (field.type==='reps') set.values[field.id] = Math.round(n);
          else set.values[field.id] = n;""",
        """          else if (field.type==='reps') set.values[field.id] = Math.round(n);
          else if (isEffortType(field.type)) set.values[field.id] = clampEffort(field.type, n);
          else set.values[field.id] = n;""")

    # 6. preset buttons in the exercise editor
    rep("""      '<button class="btn btn-tag" data-action="ex-add-preset" data-type="time" '+(hasType('time')?'disabled':'')+' title="A duration you measure and record during the workout, e.g. a max hang">'+icon('plus')+' Time (measured)</button>'+""",
        """      '<button class="btn btn-tag" data-action="ex-add-preset" data-type="time" '+(hasType('time')?'disabled':'')+' title="A duration you measure and record during the workout, e.g. a max hang">'+icon('plus')+' Time (measured)</button>'+
      '<button class="btn btn-tag" data-action="ex-add-preset" data-type="rir" '+(hasType('rir')?'disabled':'')+' title="Reps in Reserve - how many reps you had left in the tank">'+icon('plus')+' RIR</button>'+
      '<button class="btn btn-tag" data-action="ex-add-preset" data-type="rpe" '+(hasType('rpe')?'disabled':'')+' title="Rate of Perceived Exertion - how hard the set felt, 6 to 10">'+icon('plus')+' RPE</button>'+""")
    rep("""      var labels = {weight:'Weight', assisted:'Assisted', reps:'Reps', timer:'Target Time', time:'Time'};""",
        """      var labels = {weight:'Weight', assisted:'Assisted', reps:'Reps', timer:'Target Time', time:'Time', rir:'RIR', rpe:'RPE'};""")

    # 7. the chip in the editor explains itself too
    rep("""        return '<div class="chip"><span>'+esc(f.label)+(f.unit?(' ('+esc(f.unit)+')'):'')+'</span><button data-action="ex-remove-field" data-fieldid="'+f.id+'">'+icon('x')+'</button></div>';""",
        """        var chipLabel = esc(f.label)+(f.unit?(' ('+esc(f.unit)+')'):'');
        var chipInner = FIELD_INFO[f.type]
          ? '<span class="field-info" data-info="'+f.type+'" role="button" tabindex="0">'+chipLabel+'<span class="fi-dot" aria-hidden="true">i</span></span>'
          : '<span>'+chipLabel+'</span>';
        return '<div class="chip">'+chipInner+'<button data-action="ex-remove-field" data-fieldid="'+f.id+'">'+icon('x')+'</button></div>';""")

    # 8. never let a live popover end up inside an exported copy
    rep("""  var pwaBits = clone.querySelectorAll('link[rel="manifest"], [data-pwa]');""",
        """  var popovers = clone.querySelectorAll('.field-pop');
  for (var pi=0; pi<popovers.length; pi++){ popovers[pi].parentNode.removeChild(popovers[pi]); }
  var pwaBits = clone.querySelectorAll('link[rel="manifest"], [data-pwa]');""")

    # 9. wire up the popover at the end of the script
    rep("""if (pendingRestore) renderRestoreModal();""",
        POPOVER.strip() + """

if (pendingRestore) renderRestoreModal();""")

    return src
