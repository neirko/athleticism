"""Step 1: the chart primitive, plus the minimum placement needed to look at it.

A chart builder with nowhere to render is untestable, so this also drops it into
the exercise detail page behind a collapsed section. The metric picker that was
step 2 comes along for the ride because a chart has to plot *something* - what's
deliberately still missing is the Graphs tab and its sparkline index.

Drawn by hand in SVG. No library: the file stays single-file and works offline.
Sized in real CSS pixels after layout rather than scaling a fixed viewBox, which
is what keeps 2px strokes and 11px axis type from turning to mush on a phone.
"""

CSS = r"""
/* ------------------------------------------------------------ progress chart */
.chart-card{border:2px solid var(--border);border-radius:var(--radius-lg);background:var(--surface);
  padding:16px 18px 12px;box-shadow:var(--ledge);}
.chart-top{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-bottom:6px;}
.chart-value{font-family:var(--font-display);font-size:29px;font-weight:800;line-height:1.05;color:var(--text);}
.chart-sub{font-size:13px;font-weight:700;color:var(--text-dim);margin-top:3px;display:flex;align-items:center;gap:7px;flex-wrap:wrap;}
.chart-delta{font-weight:800;border-radius:20px;padding:2px 9px;font-size:12px;background:var(--surface-2);color:var(--text-dim);}
.chart-delta.up{background:var(--good-soft);color:var(--good-deep);}
.chart-delta.down{background:#FCE4E5;color:#9C2830;}
.chart-metric{appearance:none;-webkit-appearance:none;background:var(--surface-2);border:2px solid var(--border);
  border-radius:20px;padding:8px 32px 8px 14px;font-size:13.5px;font-weight:800;color:var(--text);cursor:pointer;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%237A6F81' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
  background-repeat:no-repeat;background-position:right 10px center;background-size:15px;flex-shrink:0;}
.chart-metric:hover{border-color:var(--text-faint);}
.chart-plot{width:100%;min-height:150px;touch-action:pan-y;}
.chart-plot svg{display:block;width:100%;}
.chart-foot{font-size:12.5px;font-weight:700;color:var(--text-faint);margin-top:8px;line-height:1.5;}
.chart-empty{text-align:center;padding:22px 10px 26px;color:var(--text-dim);font-size:14px;font-weight:700;}
.chart-empty span{display:block;font-size:13px;font-weight:600;color:var(--text-faint);margin-top:5px;line-height:1.5;}
.chart-seed{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin:14px 0 4px;}
.chart-seed-pill{background:var(--accent-soft);border:2px solid var(--accent-soft-border);border-radius:16px;
  padding:8px 13px;text-align:center;}
.chart-seed-val{font-family:var(--font-display);font-size:18px;font-weight:800;color:var(--accent-deep);line-height:1.1;}
.chart-seed-day{font-size:11.5px;font-weight:700;color:var(--text-dim);margin-top:1px;}
.chart-toggle{display:flex;align-items:center;gap:8px;width:100%;background:none;border:none;padding:0;
  margin:22px 0 10px;color:var(--text);}
.chart-toggle .field-label{margin:0;color:var(--text-dim);}
.chart-toggle .cat-caret{margin-left:auto;}
"""

JS = r"""
/* ------------------------------------------------------- progress charts ---
   Metrics are derived from whatever fields an exercise actually has, so a
   handstand hold and a bench press both work without special-casing. Anything
   needing two fields at once (estimated 1RM, volume) only appears when both
   are present - an estimated 1RM on a skill hold would be noise dressed up as
   a number. */
var CHART_REG = {};
var chartSeq = 0;
var DAY_MS = 86400000;

function chSets(wex){ return wex.sets.filter(function(s){ return (s.kind||'set')==='set'; }); }
function chFields(wex, t){ return wex.fields.filter(function(f){ return f.type===t; }); }
function chVals(wex, t){
  var fs = chFields(wex, t), out = [];
  chSets(wex).forEach(function(s){
    fs.forEach(function(f){
      var v = s.values[f.id];
      if (v!==null && v!==undefined && v!=='' && !isNaN(v*1)) out.push(v*1);
    });
  });
  return out;
}
function chPairs(wex){
  var wf = chFields(wex,'weight')[0], rf = chFields(wex,'reps')[0];
  if (!wf || !rf) return [];
  var out = [];
  chSets(wex).forEach(function(s){
    var w = s.values[wf.id], r = s.values[rf.id];
    if (w!==null && w!==undefined && w!=='' && r!==null && r!==undefined && r!=='') out.push({w:w*1, r:r*1});
  });
  return out;
}
function chMax(a){ return a.length ? Math.max.apply(null, a) : null; }
function chMin(a){ return a.length ? Math.min.apply(null, a) : null; }
function chSum(a){ return a.length ? a.reduce(function(x,y){return x+y;},0) : null; }
function chAvg(a){ return a.length ? chSum(a)/a.length : null; }

function fmtWeightVal(v){
  var u = data.settings.weightUnit;
  var d = kgToDisplay(v, u);
  return (Math.round(d*10)/10) + ' ' + u;
}
function fmtWeightAxis(v){
  var d = kgToDisplay(v, data.settings.weightUnit);
  return String(Math.abs(d)>=100 ? Math.round(d) : Math.round(d*10)/10);
}

var CHART_METRICS = [
  { key:'top', label:'Top Set', needs:['weight'], agg:'max',
    calc:function(w){ return chMax(chVals(w,'weight')); },
    value:fmtWeightVal, axis:fmtWeightAxis },
  { key:'bestreps', label:'Best Set', needs:['reps'], agg:'max',
    calc:function(w){ return chMax(chVals(w,'reps')); },
    value:function(v){ return Math.round(v)+' reps'; }, axis:function(v){ return String(Math.round(v)); } },
  { key:'hold', label:'Longest Hold', needs:['time'], agg:'max',
    calc:function(w){ return chMax(chVals(w,'time')); },
    value:function(v){ return secToMMSS(Math.round(v)); }, axis:function(v){ return secToMMSS(Math.round(v)); } },
  { key:'totreps', label:'Total Reps', needs:['reps'], agg:'sum',
    calc:function(w){ return chSum(chVals(w,'reps')); },
    value:function(v){ return Math.round(v)+' reps'; }, axis:function(v){ return String(Math.round(v)); } },
  { key:'e1rm', label:'Est. 1RM', needs:['weight','reps'], agg:'max',
    calc:function(w){ var p=chPairs(w); return p.length ? Math.max.apply(null, p.map(function(x){ return x.w*(1+x.r/30); })) : null; },
    value:fmtWeightVal, axis:fmtWeightAxis, note:'Epley estimate from your heaviest set' },
  { key:'volume', label:'Session Volume', needs:['weight','reps'], agg:'sum',
    calc:function(w){ var p=chPairs(w); return p.length ? p.reduce(function(a,x){ return a+x.w*x.r; },0) : null; },
    value:fmtWeightVal, axis:fmtWeightAxis, note:'Weight multiplied by reps, summed across sets' },
  { key:'assist', label:'Least Assistance', needs:['assisted'], agg:'min',
    calc:function(w){ return chMin(chVals(w,'assisted')); },
    value:fmtWeightVal, axis:fmtWeightAxis, note:'Lower is better - less help each session' },
  { key:'rpe', label:'Avg RPE', needs:['rpe'], agg:'avg',
    calc:function(w){ return chAvg(chVals(w,'rpe')); },
    value:function(v){ return 'RPE '+(Math.round(v*10)/10); }, axis:function(v){ return String(Math.round(v*10)/10); },
    note:'Higher means the session felt harder' },
  { key:'rir', label:'Avg RIR', needs:['rir'], agg:'avg',
    calc:function(w){ return chAvg(chVals(w,'rir')); },
    value:function(v){ return 'RIR '+(Math.round(v*10)/10); }, axis:function(v){ return String(Math.round(v*10)/10); },
    note:'Lower means the session felt harder' }
];

function customNumberMetrics(ex){
  return ex.fields.filter(function(f){ return f.type==='number'; }).map(function(f){
    var suffix = f.unit ? (' '+f.unit) : '';
    return { key:'num:'+f.id, label:'Best '+f.label, needs:[], agg:'max', fieldId:f.id,
      calc:function(w){
        var out=[]; chSets(w).forEach(function(s){
          var v=s.values[f.id];
          if (v!==null && v!==undefined && v!=='' && !isNaN(v*1)) out.push(v*1);
        });
        return chMax(out);
      },
      value:function(v){ return (Math.round(v*100)/100)+suffix; },
      axis:function(v){ return String(Math.round(v*100)/100); } };
  });
}
function metricsFor(ex){
  var types = ex.fields.map(function(f){ return f.type; });
  var base = CHART_METRICS.filter(function(m){
    return m.needs.every(function(t){ return types.indexOf(t)>=0; });
  });
  return base.concat(customNumberMetrics(ex));
}
function combine(agg, vals){
  if (!vals.length) return null;
  if (agg==='max') return chMax(vals);
  if (agg==='min') return chMin(vals);
  if (agg==='sum') return chSum(vals);
  return chAvg(vals);
}
/* One point per session. Two entries of the same exercise in one workout are
   folded together with the metric's own aggregation, not silently plotted twice. */
function seriesFor(ex, metric){
  var pts = [];
  data.workouts.forEach(function(w){
    var vals = [];
    (w.exercises||[]).forEach(function(wex){
      if ((wex.kind||'exercise')!=='exercise' || wex.exerciseId!==ex.id) return;
      var v = metric.calc(wex);
      if (v!==null && v!==undefined && !isNaN(v)) vals.push(v);
    });
    var v = combine(metric.agg, vals);
    if (v===null) return;
    var t = w.completedAt || w.startedAt || (w.date ? new Date(w.date+'T12:00:00').getTime() : null);
    if (!t) return;
    pts.push({ t:t, v:v });
  });
  pts.sort(function(a,b){ return a.t-b.t; });
  return pts;
}

function chartDate(ms){
  return new Date(ms).toLocaleDateString(undefined, {day:'numeric', month:'short'});
}
function niceStep(span, target){
  if (span<=0) return 1;
  var raw = span/target, mag = Math.pow(10, Math.floor(Math.log(raw)/Math.LN10)), n = raw/mag;
  return (n<=1?1:n<=2?2:n<=2.5?2.5:n<=5?5:10)*mag;
}

/* Registers a chart and returns the markup for it. paintCharts() fills it in
   once the browser has laid the container out and a real width exists. */
function chartBlock(ex, metric){
  var id = 'ch'+(++chartSeq);
  var pts = seriesFor(ex, metric);
  CHART_REG[id] = { points:pts, metric:metric };
  var head, foot = '';
  if (pts.length >= 3){
    var last = pts[pts.length-1], prev = pts[pts.length-2];
    var d = last.v - prev.v, cls = Math.abs(d) < 1e-9 ? '' : (d>0 ? 'up' : 'down');
    var sign = d>0 ? '+' : (d<0 ? '\u2212' : '');
    var deltaTxt = Math.abs(d) < 1e-9 ? 'no change' : (sign + metric.value(Math.abs(d)));
    head = '<div><div class="chart-value" data-chart-value="'+id+'">'+esc(metric.value(last.v))+'</div>'+
      '<div class="chart-sub" data-chart-sub="'+id+'"><span>'+esc(chartDate(last.t))+'</span>'+
      '<span class="chart-delta '+cls+'">'+esc(deltaTxt)+'</span></div></div>';
    var bestV = combine(metric.agg==='min'?'min':'max', pts.map(function(p){ return p.v; }));
    var best = pts.filter(function(p){ return p.v===bestV; }).pop();
    foot = '<div class="chart-foot">'+pts.length+' sessions'+
      (best && best!==pts[pts.length-1] ? (' &middot; best '+esc(metric.value(best.v))+' on '+esc(chartDate(best.t))) : '')+
      (metric.note ? ('<br>'+esc(metric.note)) : '')+'</div>';
  } else {
    var latest = pts.length ? pts[pts.length-1] : null;
    head = '<div><div class="chart-value">'+(latest ? esc(metric.value(latest.v)) : '\u2014')+'</div>'+
      '<div class="chart-sub">'+(latest ? esc(chartDate(latest.t)) : 'Nothing logged yet')+'</div></div>';
  }
  var opts = metricsFor(ex).map(function(m){
    return '<option value="'+esc(m.key)+'"'+(m.key===metric.key?' selected':'')+'>'+esc(m.label)+'</option>';
  }).join('');
  return '<div class="chart-card">'+
    '<div class="chart-top">'+head+
      '<select class="chart-metric" data-chart-metric="'+esc(ex.id)+'" aria-label="Chart metric">'+opts+'</select>'+
    '</div>'+
    '<div class="chart-plot" data-chart="'+id+'"></div>'+ foot +'</div>';
}

/* Below three sessions a line chart is a lie dressed as a trend, so show the
   readings themselves and say what's missing. */
function sparseHTML(pts, metric){
  if (!pts.length){
    return '<div class="chart-empty">No sessions logged yet'+
      '<span>Finish a workout with this exercise and it starts plotting here.</span></div>';
  }
  return '<div class="chart-empty">'+
    '<div class="chart-seed">'+pts.map(function(p){
      return '<div class="chart-seed-pill"><div class="chart-seed-val">'+esc(metric.value(p.v))+'</div>'+
        '<div class="chart-seed-day">'+esc(chartDate(p.t))+'</div></div>';
    }).join('')+'</div>'+
    '<span>'+(pts.length===1?'One session so far':'Two sessions so far')+
    ' \u2014 a third turns this into a chart.</span></div>';
}

function drawChart(el){
  var spec = CHART_REG[el.dataset.chart];
  if (!spec) return;
  var pts = spec.points, m = spec.metric;
  if (pts.length < 3){ el.innerHTML = sparseHTML(pts, m); return; }

  var W = el.clientWidth;
  if (!W) return;                                   /* hidden: paint when shown */
  var H = Math.max(158, Math.min(236, Math.round(W*0.44)));
  var padL = 46, padR = 14, padT = 14, padB = 26;
  var iw = W-padL-padR, ih = H-padT-padB;

  var vs = pts.map(function(p){ return p.v; });
  var lo = Math.min.apply(null, vs), hi = Math.max.apply(null, vs);
  if (hi===lo){ hi = lo + (Math.abs(lo)||1)*0.1; lo = lo - (Math.abs(lo)||1)*0.1; }
  var step = niceStep(hi-lo, 3);
  var yLo = Math.floor(lo/step)*step, yHi = Math.ceil(hi/step)*step;
  if (yHi===yLo) yHi = yLo + step;
  var t0 = pts[0].t, t1 = pts[pts.length-1].t;
  if (t1===t0) t1 = t0 + DAY_MS;

  var X = function(t){ return padL + (t-t0)/(t1-t0)*iw; };
  var Y = function(v){ return padT + (1-(v-yLo)/(yHi-yLo))*ih; };
  var xy = pts.map(function(p){ return {x:X(p.t), y:Y(p.v), p:p}; });

  var g = '';
  for (var v=yLo; v<=yHi+1e-9; v+=step){
    var y = Y(v);
    g += '<line x1="'+padL+'" y1="'+y.toFixed(1)+'" x2="'+(W-padR)+'" y2="'+y.toFixed(1)+
         '" stroke="var(--border)" stroke-width="1.5" stroke-dasharray="1 5" stroke-linecap="round"/>'+
         '<text x="'+(padL-9)+'" y="'+(y+4).toFixed(1)+'" text-anchor="end" class="ch-ax">'+esc(m.axis(v))+'</text>';
  }

  /* A break of three weeks or more is drawn dashed, so a lapse reads as a lapse
     rather than as a confident straight line through nothing. */
  var solid = [], bridges = [], run = [xy[0]];
  for (var i=1;i<xy.length;i++){
    if (xy[i].p.t - xy[i-1].p.t > 21*DAY_MS){
      solid.push(run); bridges.push([xy[i-1], xy[i]]); run = [xy[i]];
    } else run.push(xy[i]);
  }
  solid.push(run);
  var d = function(a){ return a.map(function(q,i){ return (i?'L':'M')+q.x.toFixed(1)+' '+q.y.toFixed(1); }).join(' '); };

  var base = H-padB;
  var area = '<path d="'+d(xy)+' L'+xy[xy.length-1].x.toFixed(1)+' '+base+' L'+xy[0].x.toFixed(1)+' '+base+
             ' Z" fill="url(#chg'+el.dataset.chart+')"/>';
  var lines = bridges.map(function(b){
    return '<path d="'+d(b)+'" fill="none" stroke="var(--accent)" stroke-width="2.5" stroke-dasharray="3 6" '+
           'stroke-linecap="round" opacity=".45"/>';
  }).join('') + solid.filter(function(r){ return r.length>1; }).map(function(r){
    return '<path d="'+d(r)+'" fill="none" stroke="var(--accent)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>';
  }).join('');

  var dots = '';
  if (xy.length <= 40){
    dots = xy.slice(0,-1).map(function(q){
      return '<circle cx="'+q.x.toFixed(1)+'" cy="'+q.y.toFixed(1)+'" r="4.2" fill="var(--surface)" stroke="var(--accent)" stroke-width="2.4"/>';
    }).join('');
  }
  var lastQ = xy[xy.length-1];
  dots += '<circle cx="'+lastQ.x.toFixed(1)+'" cy="'+lastQ.y.toFixed(1)+'" r="9" fill="var(--accent)" opacity=".18"/>'+
          '<circle cx="'+lastQ.x.toFixed(1)+'" cy="'+lastQ.y.toFixed(1)+'" r="5.2" fill="var(--accent)" stroke="var(--surface)" stroke-width="2.4"/>';

  var ticks = xy.length<=2 ? [0, xy.length-1] : (W<380 ? [0, xy.length-1] : [0, Math.floor((xy.length-1)/2), xy.length-1]);
  var xlab = ticks.filter(function(v,i,a){ return a.indexOf(v)===i; }).map(function(i){
    var q = xy[i];
    var anchor = i===0 ? 'start' : (i===xy.length-1 ? 'end' : 'middle');
    var x = i===0 ? padL : (i===xy.length-1 ? W-padR : q.x);
    return '<text x="'+x.toFixed(1)+'" y="'+(H-7)+'" text-anchor="'+anchor+'" class="ch-ax">'+esc(chartDate(q.p.t))+'</text>';
  }).join('');

  el.innerHTML = '<svg viewBox="0 0 '+W+' '+H+'" width="'+W+'" height="'+H+'" role="img" '+
    'aria-label="'+esc(m.label)+' over '+pts.length+' sessions">'+
    '<defs><linearGradient id="chg'+el.dataset.chart+'" x1="0" y1="0" x2="0" y2="1">'+
      '<stop offset="0" stop-color="var(--accent)" stop-opacity="0.22"/>'+
      '<stop offset="1" stop-color="var(--accent)" stop-opacity="0"/></linearGradient>'+
    '<style>.ch-ax{font-family:var(--font-ui);font-size:11px;font-weight:700;fill:var(--text-faint);}</style></defs>'+
    g + area + lines + dots + xlab +
    '<line class="ch-guide" y1="'+padT+'" y2="'+base+'" stroke="var(--text-faint)" stroke-width="1.5" stroke-dasharray="3 4" opacity="0"/>'+
    '<circle class="ch-cursor" r="5.6" fill="var(--accent)" stroke="var(--surface)" stroke-width="2.6" opacity="0"/>'+
    '<rect class="ch-hit" x="'+padL+'" y="0" width="'+iw+'" height="'+H+'" fill="transparent" style="cursor:crosshair"/></svg>';
  el._xy = xy;
}

/* Scrubbing: dragging across the plot swaps the big readout to that session
   instead of floating a tooltip, which is unusable with a thumb over it. */
function chartScrub(el, clientX){
  var xy = el._xy, spec = CHART_REG[el.dataset.chart];
  if (!xy || !spec) return;
  var r = el.getBoundingClientRect(), svg = el.querySelector('svg');
  if (!svg) return;
  var x = (clientX - r.left) * (svg.viewBox.baseVal.width / r.width);
  var best = 0;
  for (var i=1;i<xy.length;i++) if (Math.abs(xy[i].x-x) < Math.abs(xy[best].x-x)) best = i;
  var q = xy[best];
  var guide = el.querySelector('.ch-guide'), cur = el.querySelector('.ch-cursor');
  guide.setAttribute('x1', q.x); guide.setAttribute('x2', q.x); guide.setAttribute('opacity','.9');
  cur.setAttribute('cx', q.x); cur.setAttribute('cy', q.y); cur.setAttribute('opacity','1');
  var id = el.dataset.chart;
  var vEl = document.querySelector('[data-chart-value="'+id+'"]');
  var sEl = document.querySelector('[data-chart-sub="'+id+'"]');
  if (vEl) vEl.textContent = spec.metric.value(q.p.v);
  if (sEl) sEl.innerHTML = '<span>'+esc(chartDate(q.p.t))+'</span>';
}
function chartScrubEnd(el){
  var spec = CHART_REG[el.dataset.chart];
  var guide = el.querySelector('.ch-guide'), cur = el.querySelector('.ch-cursor');
  if (guide) guide.setAttribute('opacity','0');
  if (cur) cur.setAttribute('opacity','0');
  if (!spec || spec.points.length<2) return;
  var pts = spec.points, m = spec.metric, last = pts[pts.length-1], prev = pts[pts.length-2];
  var dd = last.v-prev.v, cls = Math.abs(dd)<1e-9 ? '' : (dd>0?'up':'down');
  var sign = dd>0?'+':(dd<0?'\u2212':'');
  var txt = Math.abs(dd)<1e-9 ? 'no change' : (sign+m.value(Math.abs(dd)));
  var id = el.dataset.chart;
  var vEl = document.querySelector('[data-chart-value="'+id+'"]');
  var sEl = document.querySelector('[data-chart-sub="'+id+'"]');
  if (vEl) vEl.textContent = m.value(last.v);
  if (sEl) sEl.innerHTML = '<span>'+esc(chartDate(last.t))+'</span><span class="chart-delta '+cls+'">'+esc(txt)+'</span>';
}

function paintCharts(){
  var els = document.querySelectorAll('[data-chart]');
  for (var i=0;i<els.length;i++) drawChart(els[i]);
}
var chartResizeT = null;
window.addEventListener('resize', function(){
  clearTimeout(chartResizeT);
  chartResizeT = setTimeout(paintCharts, 140);
});
document.addEventListener('pointerdown', function(e){
  var el = e.target.closest && e.target.closest('[data-chart]');
  if (!el || !el._xy) return;
  el._scrub = true;
  if (el.setPointerCapture && e.pointerId!==undefined){ try{ el.setPointerCapture(e.pointerId); }catch(_){} }
  chartScrub(el, e.clientX);
});
document.addEventListener('pointermove', function(e){
  var el = e.target.closest && e.target.closest('[data-chart]');
  if (!el || !el._xy) return;
  if (e.pointerType==='mouse' || el._scrub) chartScrub(el, e.clientX);
});
document.addEventListener('pointerup', function(e){
  var el = e.target.closest && e.target.closest('[data-chart]');
  if (el){ el._scrub = false; chartScrubEnd(el); }
});
document.addEventListener('pointerleave', function(e){
  var el = e.target.closest && e.target.closest('[data-chart]');
  if (el && e.pointerType==='mouse'){ el._scrub = false; chartScrubEnd(el); }
}, true);
document.addEventListener('change', function(e){
  var sel = e.target.closest && e.target.closest('[data-chart-metric]');
  if (!sel) return;
  data.settings.chartMetric = sel.value;
  save(); renderMain();
});
"""

DETAIL = (
    "\n    (metricsFor(ex).length ?\n"
    "      '<button class=\"chart-toggle\" data-action=\"toggle-chart\">'+\n"
    "        '<span class=\"field-label\">Progress</span>'+\n"
    "        '<span class=\"cat-caret '+(data.settings.chartOpen?'':'collapsed')+'\">'+icon('chevronDown')+'</span>'+\n"
    "      '</button>'+\n"
    "      (data.settings.chartOpen ? chartBlock(ex, pickMetric(ex)) : '')\n"
    "    : '')"
)


def apply(src):
    def rep(old, new, why=""):
        nonlocal src
        assert src.count(old) == 1, "expected 1 of %r, found %d (%s)" % (old[:70], src.count(old), why)
        src = src.replace(old, new)

    # chart engine, dropped in before the exercise views that use it
    rep("function renderExercises(){", JS.strip() + "\n\nfunction renderExercises(){")

    # remember the last metric and whether the section is open
    rep("var FIELD_TYPE_NAMES =",
        """function pickMetric(ex){
  var avail = metricsFor(ex);
  if (!avail.length) return null;
  var saved = avail.filter(function(m){ return m.key===data.settings.chartMetric; })[0];
  if (saved) return saved;
  var order = ['top','bestreps','hold','totreps','assist','rpe','rir','e1rm','volume'];
  for (var i=0;i<order.length;i++){
    var hit = avail.filter(function(m){ return m.key===order[i]; })[0];
    if (hit) return hit;
  }
  return avail[0];
}
var FIELD_TYPE_NAMES =""")

    # the section itself, under the exercise's fields
    _anchor = '''    \'<div class="field-label">Default rest</div>\'+\n    '''
    _tail = '\'<div style="color:var(--text-dim);font-size:14px;">\'+(ex.defaultRestSec!=null?fmtRest(ex.defaultRestSec):\'Not set\')+\'</div>\';'
    rep(_anchor + _tail, _anchor + _tail[:-1] + "+" + DETAIL + ";")

    rep("""    case 'select-exercise': ui.selectedExerciseId = el.dataset.id; renderMain(); break;""",
        """    case 'select-exercise': ui.selectedExerciseId = el.dataset.id; renderMain(); break;
    case 'toggle-chart': data.settings.chartOpen = !data.settings.chartOpen; save(); renderMain(); break;""")

    # charts can only be measured once the browser has laid them out
    rep("""    case 'profile': renderProfile(); break;
  }
}""",
        """    case 'profile': renderProfile(); break;
  }
  paintCharts();
}""")

    return src
