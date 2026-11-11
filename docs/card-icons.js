import * as T from "../vendor/three/three.module.min.js";
import {cardSymbols} from "./card-icon-symbols.js";

let enhanced = false;

export function enhanceCardIcons() {
  if (enhanced) return;
  enhanced = true;
  const surface = document.createElement("canvas");
  const options = {alpha: true, antialias: true, preserveDrawingBuffer: true};
  // Supplying the context avoids Three's console error when WebGL is unavailable.
  const context = surface.getContext("webgl2", options) || surface.getContext("webgl", options);
  if (!context) {
    document.documentElement.dataset.cardIcons = "fallback";
    return;
  }
  const renderer = new T.WebGLRenderer({canvas: surface, context, ...options});
  const material = new T.MeshStandardMaterial({roughness: 0.5, metalness: 0.1});
  const symbols = cardSymbols(material);
  const scene = new T.Scene();
  scene.add(...Object.values(symbols));
  const white = new T.Color().setRGB(1, 1, 1);
  scene.add(new T.HemisphereLight(white, white, 1.5));
  const light = new T.DirectionalLight(white, 1.9);
  light.position.set(2.5, 3.5, 4);
  scene.add(light);
  const camera = new T.OrthographicCamera(-1.4, 1.4, 1.4, -1.4, 0.1, 20);
  camera.position.z = 6;
  const motion = matchMedia("(prefers-reduced-motion: reduce)");
  const entries = new Map();
  const listeners = new AbortController();
  const eventOptions = {signal: listeners.signal};
  let hovered = null;
  let focused = null;
  let active = null;
  let frame = 0;
  let started = 0;
  let stopped = false;

  function removeCanvas(entry) {
    entry.canvas?.remove();
    entry.canvas = null;
    delete entry.icon.dataset.iconDrawn;
  }

  function dispose() {
    if (stopped) return;
    stopped = true;
    cancelAnimationFrame(frame);
    listeners.abort();
    intersections.disconnect();
    mutations.disconnect();
    theme.disconnect();
    for (const entry of entries.values()) removeCanvas(entry);
    entries.clear();
    for (const symbol of Object.values(symbols)) {
      symbol.traverse(object => object.geometry?.dispose());
    }
    material.dispose();
    renderer.dispose();
  }

  function fallback() {
    document.documentElement.dataset.cardIcons = "fallback";
    dispose();
  }

  function draw(entry, turn = 0) {
    if (stopped || !entry.seen || !entry.icon.isConnected) return;
    const icon = entry.icon;
    const size = Math.round(icon.clientWidth * Math.min(devicePixelRatio, 2));
    if (!size) return;
    const canvas = entry.canvas || document.createElement("canvas");
    const target = canvas.getContext("2d");
    if (!target) {
      fallback();
      return;
    }
    canvas.width = canvas.height = size;
    canvas.setAttribute("aria-hidden", "true");
    const symbol = symbols[icon.dataset.iconKind] || symbols.general;
    material.color.set(getComputedStyle(icon).color);
    symbol.rotation.copy(symbol.userData.rest);
    symbol.rotation.y += turn;
    symbol.visible = true;
    try {
      renderer.setSize(size, size, false);
      renderer.render(scene, camera);
      target.drawImage(surface, 0, 0);
    } catch {
      fallback();
      return;
    } finally {
      symbol.visible = false;
    }
    if (!entry.canvas) icon.append(canvas);
    entry.canvas = canvas;
    icon.dataset.iconDrawn = "";
  }

  function animate(now) {
    frame = 0;
    if (!active || stopped) return;
    draw(active, Math.sin((now - started) / 1600) * 0.24);
    if (!stopped) frame = requestAnimationFrame(animate);
  }

  function selectActive() {
    const desired = motion.matches || document.hidden ? null : hovered || focused;
    const next = desired?.seen ? desired : null;
    if (next === active) return;
    cancelAnimationFrame(frame);
    frame = 0;
    const previous = active;
    active = next;
    if (previous?.seen) draw(previous);
    if (active && !stopped) {
      started = performance.now();
      frame = requestAnimationFrame(animate);
    }
  }

  const intersections = new IntersectionObserver(changes => {
    for (const change of changes) {
      const entry = entries.get(change.target);
      if (!entry) continue;
      entry.seen = change.isIntersecting && change.intersectionRect.width > 0
        && change.intersectionRect.height > 0;
      if (entry.seen) draw(entry);
      else removeCanvas(entry);
    }
    selectActive();
  });

  function discover(root) {
    if (!(root instanceof Element)) return;
    const icons = [...root.querySelectorAll(".agent-icon")];
    if (root.matches(".agent-icon")) icons.push(root);
    for (const icon of icons) {
      if (entries.has(icon)) continue;
      const entry = {icon, seen: false, canvas: null};
      entries.set(icon, entry);
      intersections.observe(icon);
    }
  }

  const mutations = new MutationObserver(changes => {
    for (const change of changes) {
      for (const node of change.addedNodes) discover(node);
    }
    for (const [icon, entry] of entries) {
      if (icon.isConnected) continue;
      intersections.unobserve(icon);
      removeCanvas(entry);
      entries.delete(icon);
      if (hovered === entry) hovered = null;
      if (focused === entry) focused = null;
    }
    selectActive();
  });
  mutations.observe(document.body, {childList: true, subtree: true});
  const theme = new MutationObserver(() => {
    for (const entry of entries.values()) if (entry.seen) draw(entry);
  });
  theme.observe(document.documentElement, {attributes: true, attributeFilter: ["data-theme"]});

  const cardEntry = target => {
    const card = target instanceof Element ? target.closest(".agent-card") : null;
    return card ? entries.get(card.querySelector(".agent-icon")) : null;
  };
  document.addEventListener("pointerover", event => {
    hovered = event.pointerType === "touch" ? null : cardEntry(event.target);
    selectActive();
  }, eventOptions);
  document.addEventListener("pointerout", event => {
    hovered = cardEntry(event.relatedTarget);
    selectActive();
  }, eventOptions);
  document.addEventListener("focusin", event => {
    focused = cardEntry(event.target);
    selectActive();
  }, eventOptions);
  document.addEventListener("focusout", event => {
    focused = cardEntry(event.relatedTarget);
    selectActive();
  }, eventOptions);
  document.addEventListener("visibilitychange", selectActive, eventOptions);
  motion.addEventListener("change", selectActive, eventOptions);
  window.addEventListener("resize", () => {
    for (const entry of entries.values()) {
      const size = Math.round(entry.icon.clientWidth * Math.min(devicePixelRatio, 2));
      if (entry.seen && entry.canvas?.width !== size) draw(entry);
    }
  }, eventOptions);
  surface.addEventListener("webglcontextlost", fallback, eventOptions);
  window.addEventListener("pagehide", event => {
    if (!event.persisted) dispose();
  }, eventOptions);
  discover(document.body);
  document.documentElement.dataset.cardIcons = "ready";
}
