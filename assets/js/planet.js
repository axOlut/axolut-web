// Fond animé : ciel étoilé qui scintille et planète holographique en rotation (WebGL).
// Suit doucement le pointeur, se met en pause hors écran, respecte « réduire les animations »
// et baisse sa qualité d'elle-même sur les appareils modestes.
(() => {
  const canvas = document.querySelector("[data-sky]");
  if (!canvas) return;
  const mini = canvas.dataset.sky === "mini";
  const gl = canvas.getContext("webgl", { antialias: false, alpha: true, premultipliedAlpha: true, powerPreference: "low-power" });
  if (!gl) { canvas.parentElement.classList.add("no-gl"); return; }

  const vs = "attribute vec2 p; void main(){ gl_Position = vec4(p, 0., 1.); }";
  const fs = `precision highp float;
  uniform vec2 r; uniform float t; uniform vec2 m; uniform vec3 P; uniform float k; uniform float px;
  float h21(vec2 p){ p = fract(p*vec2(123.34, 456.21)); p += dot(p, p + 45.32); return fract(p.x*p.y); }
  float h31(vec3 p){ p = fract(p*.3183099 + .1); p *= 17.; return fract(p.x*p.y*p.z*(p.x + p.y + p.z)); }
  float n3(vec3 x){ vec3 i = floor(x), f = fract(x); f = f*f*(3. - 2.*f);
    return mix(mix(mix(h31(i), h31(i+vec3(1,0,0)), f.x), mix(h31(i+vec3(0,1,0)), h31(i+vec3(1,1,0)), f.x), f.y),
               mix(mix(h31(i+vec3(0,0,1)), h31(i+vec3(1,0,1)), f.x), mix(h31(i+vec3(0,1,1)), h31(i+vec3(1,1,1)), f.x), f.y), f.z); }
  vec2 rot(vec2 v, float a){ float c = cos(a), s = sin(a); return vec2(c*v.x - s*v.y, s*v.x + c*v.y); }

  vec3 stars(vec2 fc){
    vec3 c = vec3(0.);
    for (int L = 0; L < 3; L++){
      float fl = float(L);
      float s = 34. + fl*30.;
      vec2 g = fc/s + fl*13.7;
      vec2 id = floor(g), f = fract(g) - .5;
      float rnd = h21(id + fl*17.);
      if (rnd > .62){
        vec2 o = (vec2(h21(id + 3.1), h21(id + 7.7)) - .5)*.7;
        vec2 dv = (f - o)*s;
        float d = length(dv);
        float tw = .5 + .5*sin(t*(.6 + rnd*2.4) + rnd*60.);
        tw = tw*tw*tw;
        float big = step(.93, rnd);
        float b = exp(-d*d/(1.1 + big*1.6))*(.18 + .82*tw);
        b += big*tw*.5*(exp(-abs(dv.x)*1.2)*exp(-dv.y*dv.y*.05) + exp(-abs(dv.y)*1.2)*exp(-dv.x*dv.x*.05));
        c += mix(vec3(.75, .85, 1.), vec3(.45, .95, 1.), h21(id + 5.))*b*(1. - fl*.25);
      }
    }
    return c;
  }

  void main(){
    vec2 uv = (gl_FragCoord.xy - .5*r)/r.y;
    vec3 col = stars(gl_FragCoord.xy/px)*.9;
    vec2 q = (uv - P.xy)/P.z;
    float d = length(q);
    vec3 holo = vec3(.32, .86, 1.);

    // halo de l'atmosphère
    col += vec3(.18, .45, 1.)*.55*exp(-max(d - 1., 0.)*5.5)*smoothstep(.2, 1., d);

    if (d < 1.){
      col *= .15;
      float z = sqrt(1. - d*d);
      float spin = t*.09 + m.x*.35, tilt = .38 - m.y*.15;
      vec3 nf = vec3(q, z), nb = vec3(q, -z);
      nf.yz = rot(nf.yz, tilt); nb.yz = rot(nb.yz, tilt);
      nf.xz = rot(nf.xz, spin); nb.xz = rot(nb.xz, spin);
      float aa = 1.4/(P.z*r.y/px);
      // grille de méridiens et parallèles (face avant nette, face arrière en transparence)
      float lonF = atan(nf.x, nf.z), latF = asin(clamp(nf.y, -1., 1.));
      float lonB = atan(nb.x, nb.z), latB = asin(clamp(nb.y, -1., 1.));
      float stepL = 6.2831853/24., stepT = 3.1415926/12.;
      float wF = aa/(z + .2);
      float gF = max(smoothstep(wF, 0., abs(fract(lonF/stepL + .5) - .5)*stepL*cos(latF)),
                     smoothstep(wF, 0., abs(fract(latF/stepT + .5) - .5)*stepT));
      float gB = max(smoothstep(wF, 0., abs(fract(lonB/stepL + .5) - .5)*stepL*cos(latB)),
                     smoothstep(wF, 0., abs(fract(latB/stepT + .5) - .5)*stepT));
      // continents en points lumineux
      float land = n3(nf*2.1)*.62 + n3(nf*4.7)*.28 + n3(nf*10.)*.1;
      vec2 cell = vec2(lonF*cos(latF), latF)*24.;
      float dotm = smoothstep(.30, .14, length(fract(cell) - .5))*smoothstep(.50, .56, land);
      float landB = n3(nb*2.1)*.62 + n3(nb*4.7)*.28 + n3(nb*10.)*.1;
      vec2 cellB = vec2(lonB*cos(latB), latB)*24.;
      float dotB = smoothstep(.30, .14, length(fract(cellB) - .5))*smoothstep(.50, .56, landB);
      float fres = pow(1. - z, 2.4);
      float light = .35 + .65*clamp(dot(normalize(vec3(q, z)), normalize(vec3(-.5 + m.x*.4, .45 + m.y*.3, .75))), 0., 1.);
      vec3 base = vec3(.03, .08, .22)*(.4 + .6*z);
      col += base + holo*(gF*.42*light + gB*.10 + dotm*.6*light + dotB*.16 + fres*.75);
      col *= .86 + .14*sin(gl_FragCoord.y/px*1.3 - t*5.);
    }

    // anneau d'orbite et satellite
    vec2 rq = rot(q, -.32);
    vec2 ab = vec2(1.75, .40);
    float ed = abs(length(rq/ab) - 1.)*ab.y;
    float behind = step(0., rq.y)*step(d, 1.);
    float ringW = 1.2/(P.z*r.y/px);
    col += vec3(.36, .78, 1.)*smoothstep(ringW*1.6, 0., ed)*.55*(1. - behind);
    col += vec3(.36, .78, 1.)*smoothstep(ringW*10., 0., ed)*.08*(1. - behind);
    float an = t*.35;
    vec2 sp = vec2(cos(an), sin(an))*ab;
    float sHide = step(0., sp.y)*step(length(sp), 1.);
    float sd = length(rq - sp);
    col += vec3(.7, .95, 1.)*(exp(-sd*sd*900.) + .25*exp(-sd*sd*60.))*(1. - sHide);

    col *= k;
    float al = clamp(max(col.r, max(col.g, col.b)), 0., 1.);
    gl_FragColor = vec4(col, al);
  }`;

  const sh = (type, src) => { const x = gl.createShader(type); gl.shaderSource(x, src); gl.compileShader(x); return x; };
  const prog = gl.createProgram();
  gl.attachShader(prog, sh(gl.VERTEX_SHADER, vs));
  gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, fs));
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) { canvas.parentElement.classList.add("no-gl"); return; }
  gl.useProgram(prog);
  gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  const loc = gl.getAttribLocation(prog, "p");
  gl.enableVertexAttribArray(loc);
  gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
  const U = (n) => gl.getUniformLocation(prog, n);
  const uR = U("r"), uT = U("t"), uM = U("m"), uP = U("P"), uK = U("k"), uPx = U("px");

  const still = matchMedia("(prefers-reduced-motion: reduce)");
  let w = 0, h = 0, raf = 0, visible = true, ready = false, frozen = false;
  let res = 0.8, minGap = 0, last = 0, frames = 0, sum = 0, slow = 0, dpr = 1;
  const t0 = performance.now(), frozenAt = 20;
  const target = { x: 0, y: 0 }, pt = { x: 0, y: 0 };
  let planet = [0, 0, .4], glow = 1;

  function layout() {
    const a = w / h, wide = innerWidth > 900;
    if (mini) { planet = wide ? [a * .5 - .30, -.02, .30] : [a * .32, .22, a * .36]; glow = wide ? .62 : .4; }
    else { planet = wide ? [a * .5 - .40, -.02, .40] : [0, .25, a * .44]; glow = wide ? .66 : .55; }
  }
  function size() {
    dpr = Math.min(window.devicePixelRatio || 1, 1.5) * res;
    const b = canvas.getBoundingClientRect();
    w = Math.max(1, Math.round(b.width * dpr)); h = Math.max(1, Math.round(b.height * dpr));
    if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; gl.viewport(0, 0, w, h); }
    layout();
  }
  function draw(time) {
    pt.x += (target.x - pt.x) * .05; pt.y += (target.y - pt.y) * .05;
    gl.uniform2f(uR, w, h); gl.uniform1f(uT, time); gl.uniform2f(uM, pt.x, pt.y);
    gl.uniform3f(uP, planet[0], planet[1], planet[2]); gl.uniform1f(uK, glow); gl.uniform1f(uPx, dpr);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }
  const now = () => (performance.now() - t0) / 1000;
  function loop(ts) {
    raf = 0;
    if (!visible || document.hidden) return;
    if (ts - last >= minGap) {
      const dt = last ? ts - last : 16;
      last = ts;
      draw((ts - t0) / 1000);
      frames++;
      if (frames > 1 && frames <= 7) sum += dt;
      if (frames === 7) {
        const avg = sum / 6;
        if (avg > 60) { frozen = true; return; }
        if (avg > 22) { res = .55; minGap = 33; size(); }
      } else if (frames > 7) {
        slow = dt > minGap + 30 ? slow + 1 : Math.max(0, slow - 1);
        if (slow > 10) { frozen = true; return; }
      }
    }
    raf = requestAnimationFrame(loop);
  }
  function start() {
    if (!ready) return;
    if (still.matches || frozen) { draw(still.matches ? frozenAt : now()); return; }
    if (!raf) { last = 0; raf = requestAnimationFrame(loop); }
  }

  size();
  draw(still.matches ? frozenAt : 0);
  requestAnimationFrame(() => canvas.classList.add("on"));
  const go = () => { ready = true; start(); };
  if (document.readyState === "complete") setTimeout(go, 300);
  else addEventListener("load", () => setTimeout(go, 300), { once: true });

  new ResizeObserver(() => { size(); if (still.matches || frozen || !raf) draw(still.matches ? frozenAt : now()); }).observe(canvas);
  new IntersectionObserver(([en]) => { visible = en.isIntersecting; if (visible) start(); }).observe(canvas);
  document.addEventListener("visibilitychange", start);
  still.addEventListener?.("change", start);

  const zone = canvas.parentElement;
  zone.addEventListener("pointermove", (ev) => {
    const b = canvas.getBoundingClientRect();
    target.x = Math.max(-1, Math.min(1, ((ev.clientX - b.left) / b.width) * 2 - 1));
    target.y = Math.max(-1, Math.min(1, -(((ev.clientY - b.top) / b.height) * 2 - 1)));
  }, { passive: true });
  zone.addEventListener("pointerleave", () => { target.x = 0; target.y = 0; });
})();
