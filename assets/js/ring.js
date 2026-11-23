// L'anneau lumineux du haut de page : le « O » d'axOlut, dessiné en temps réel (WebGL).
// Il suit doucement le doigt ou la souris, se met en pause hors écran et respecte « réduire les animations ».
(() => {
  const canvas = document.querySelector("[data-ring]");
  if (!canvas) return;
  const gl = canvas.getContext("webgl", { antialias: false, alpha: true, premultipliedAlpha: true, powerPreference: "low-power" });
  if (!gl) { canvas.closest(".hero")?.classList.add("no-gl"); return; }

  const vs = `attribute vec2 p; void main(){ gl_Position = vec4(p, 0., 1.); }`;
  const fs = `precision highp float;
  uniform vec2 r; uniform float t; uniform vec2 m; uniform float s;
  float h(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
  float n(vec2 p){ vec2 i = floor(p), f = fract(p); f = f*f*(3.-2.*f);
    return mix(mix(h(i), h(i+vec2(1,0)), f.x), mix(h(i+vec2(0,1)), h(i+vec2(1,1)), f.x), f.y); }
  float fbm(vec2 p){ float v = 0., a = .5; for (int i = 0; i < 3; i++){ v += a*n(p); p = p*2.03 + 7.1; a *= .5; } return v; }
  void main(){
    vec2 uv = (gl_FragCoord.xy - .5*r) / min(r.x, r.y);
    // légère perspective qui suit le pointeur
    uv.x *= 1. + .10*m.x*sign(uv.x);
    uv.y *= 1. + .14*m.y*sign(uv.y);
    uv /= s;
    float a = atan(uv.y, uv.x), d = length(uv);
    float R = .30;
    float w = fbm(vec2(cos(a)*1.4 + t*.11, sin(a)*1.4 - t*.09) + d*2.);
    float rr = R + (w - .5)*.028;
    float band = abs(d - rr);
    float core = smoothstep(.030, .0, band);
    float glow = .010 / (band + .012); glow = glow*glow;
    float flow = .5 + .5*sin(a*2. - t*.55 + w*5.);
    vec3 lagoon = vec3(.21, .82, .90), cobalt = vec3(.23, .42, 1.), violet = vec3(.50, .40, .98);
    vec3 col = mix(cobalt, lagoon, flow);
    col = mix(col, violet, smoothstep(.55, 1., sin(a + t*.21))*.30);
    float pm = length(m);
    float hl = pow(max(0., cos(a - atan(m.y, m.x + 1e-4))), 10.) * pm;
    vec3 o = col*(core*.95 + glow*.42) + vec3(1.)*hl*core*.75;
    // brume à l'intérieur de l'anneau
    o += mix(cobalt, lagoon, .4) * .10 * smoothstep(R*1.05, 0., d) * n(uv*2.6 + vec2(t*.04, -t*.03));
    // poussière de lumière
    float dust = step(.9985, h(floor(gl_FragCoord.xy*.5) + floor(t*.6))) * smoothstep(.75, .2, d);
    o += lagoon * dust * .35;
    o *= smoothstep(1.05, .35, d);
    float al = clamp(max(o.r, max(o.g, o.b)), 0., 1.);
    gl_FragColor = vec4(o, al);
  }`;

  const sh = (type, src) => { const x = gl.createShader(type); gl.shaderSource(x, src); gl.compileShader(x); return x; };
  const prog = gl.createProgram();
  gl.attachShader(prog, sh(gl.VERTEX_SHADER, vs));
  gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, fs));
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) { canvas.closest(".hero")?.classList.add("no-gl"); return; }
  gl.useProgram(prog);
  gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  const loc = gl.getAttribLocation(prog, "p");
  gl.enableVertexAttribArray(loc);
  gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
  const U = (k) => gl.getUniformLocation(prog, k);
  const uR = U("r"), uT = U("t"), uM = U("m"), uS = U("s");

  const still = matchMedia("(prefers-reduced-motion: reduce)");
  let w = 0, h = 0, raf = 0, visible = true, t0 = performance.now(), frozenAt = 12.;
  // Qualité adaptative : on baisse la résolution puis la cadence si l'appareil peine, et on fige en dernier recours.
  let res = 0.75, minGap = 0, last = 0, slow = 0, frames = 0, sum = 0, ready = false;
  const target = { x: 0, y: 0 }, pt = { x: 0, y: 0 };
  let scale = 1;

  function size() {
    const dpr = Math.min(window.devicePixelRatio || 1, 1.5) * res;
    const b = canvas.getBoundingClientRect();
    w = Math.max(1, Math.round(b.width * dpr)); h = Math.max(1, Math.round(b.height * dpr));
    if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; gl.viewport(0, 0, w, h); }
  }
  function draw(time) {
    pt.x += (target.x - pt.x) * .05; pt.y += (target.y - pt.y) * .05;
    gl.uniform2f(uR, w, h);
    gl.uniform1f(uT, time);
    gl.uniform2f(uM, pt.x, pt.y);
    gl.uniform1f(uS, scale);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }
  function loop(now) {
    raf = 0;
    if (!visible || document.hidden) return;
    if (now - last >= minGap) {
      const dt = last ? now - last : 16;
      last = now;
      draw((now - t0) / 1000);
      // premières images : on mesure, puis on ajuste une fois pour toutes
      frames++;
      if (frames > 1 && frames <= 7) sum += dt;
      if (frames === 7) {
        const avg = sum / 6;
        if (avg > 60) { frozen = true; return; }
        if (avg > 22) { res = 0.5; minGap = 33; size(); }
      } else if (frames > 7) {
        slow = dt > minGap + 30 ? slow + 1 : Math.max(0, slow - 1);
        if (slow > 10) { frozen = true; return; }
      }
    }
    raf = requestAnimationFrame(loop);
  }
  let frozen = false;
  function start() {
    if (!ready) return;
    if (still.matches || frozen) { draw(frozen ? (performance.now() - t0) / 1000 : frozenAt); return; }
    if (!raf) { last = 0; raf = requestAnimationFrame(loop); }
  }

  size();
  draw(still.matches ? frozenAt : 0);
  requestAnimationFrame(() => canvas.classList.add("on"));
  // l'animation démarre une fois la page chargée, pour ne jamais ralentir l'affichage du texte
  const go = () => { ready = true; start(); };
  if (document.readyState === "complete") setTimeout(go, 300);
  else addEventListener("load", () => setTimeout(go, 300), { once: true });

  new ResizeObserver(() => { size(); if (still.matches || frozen || !raf) draw(still.matches ? frozenAt : (performance.now() - t0) / 1000); }).observe(canvas);
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; if (visible) start(); }).observe(canvas);
  document.addEventListener("visibilitychange", start);
  still.addEventListener?.("change", start);

  const hero = canvas.closest(".hero") || document;
  hero.addEventListener("pointermove", (e) => {
    const b = canvas.getBoundingClientRect();
    target.x = Math.max(-1, Math.min(1, ((e.clientX - b.left) / b.width) * 2 - 1));
    target.y = Math.max(-1, Math.min(1, -(((e.clientY - b.top) / b.height) * 2 - 1)));
    if (still.matches || frozen) draw(still.matches ? frozenAt : (performance.now() - t0) / 1000);
  }, { passive: true });
  hero.addEventListener("pointerleave", () => { target.x = 0; target.y = 0; });
  // l'anneau grandit un peu quand on fait défiler la page
  addEventListener("scroll", () => { scale = 1 + Math.min(scrollY / innerHeight, 1) * .25; }, { passive: true });
})();
