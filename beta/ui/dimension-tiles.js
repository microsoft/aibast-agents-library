(function registerDimensionTiles(root) {
  const STYLE_ID = "__rappDimensionTilesStyle";
  const SCRIPT_STATE = {
    tiles: [],
    captureWaiters: new Map(),
    context: null,
    controller: null,
    createdHerd: false,
    enabled: false,
    openedHerd: false,
    primaryFrameGeneration: null,
    primaryId: null,
    primaryRouteKey: null,
    refreshSequence: 0,
    timers: new Set(),
  };

  function addTimer(callback, delay) {
    const timer = setTimeout(() => {
      SCRIPT_STATE.timers.delete(timer);
      callback();
    }, delay);
    SCRIPT_STATE.timers.add(timer);
    return timer;
  }

  function driveTile(id, part = "") {
    return `herd.tile[${id}]${part ? `.${part}` : ""}`;
  }

  function installStyles() {
    let link = document.getElementById(STYLE_ID);
    if (link) return link;
    link = document.createElement("link");
    link.id = STYLE_ID;
    link.rel = "stylesheet";
    link.href = new URL("dimension-tiles.css", document.baseURI).href;
    document.head.appendChild(link);
    return link;
  }

  function removeStyles() {
    document.getElementById(STYLE_ID)?.remove();
  }

  function postToFrame(message) {
    SCRIPT_STATE.context?.frame?.contentWindow?.postMessage(message, "*");
  }

  function showToast(message, {
    action,
    actionLabel,
    duration = 8000,
  } = {}) {
    if (!SCRIPT_STATE.enabled) return null;
    document.querySelector(".dimension-tile-toast")?.remove();
    const toast = document.createElement("div");
    toast.className = "dimension-tile-toast";
    toast.dataset.drive = "tableView.toast";
    toast.setAttribute("role", "status");
    const text = document.createElement("span");
    text.textContent = String(message || "");
    toast.appendChild(text);
    if (action && actionLabel) {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = actionLabel;
      button.addEventListener("click", () => {
        toast.remove();
        Promise.resolve(action()).catch(showError);
      }, { once: true });
      toast.appendChild(button);
    }
    document.body.appendChild(toast);
    addTimer(() => toast.remove(), duration);
    return toast;
  }

  function showError(error) {
    showToast(String(error?.message || error), { duration: 10000 });
  }

  function requestCapture() {
    const frameWindow = SCRIPT_STATE.context?.frame?.contentWindow;
    if (!frameWindow) {
      return Promise.reject(new Error("The Brainstem frame is unavailable."));
    }
    const requestId = crypto.randomUUID();
    return new Promise((resolve, reject) => {
      const timer = addTimer(() => {
        SCRIPT_STATE.captureWaiters.delete(requestId);
        reject(new Error("Timed out while capturing the Brainstem chat."));
      }, 10000);
      SCRIPT_STATE.captureWaiters.set(requestId, {
        resolve(value) {
          clearTimeout(timer);
          SCRIPT_STATE.timers.delete(timer);
          resolve(value);
        },
        reject(error) {
          clearTimeout(timer);
          SCRIPT_STATE.timers.delete(timer);
          reject(error);
        },
      });
      frameWindow.postMessage({
        type: "rapp-beta:tile-capture",
        requestId,
      }, "*");
    });
  }

  function hasConversation(capture) {
    return capture?.turns?.some((turn) => turn.role === "user");
  }

  function routeForCapture(capture) {
    const state = SCRIPT_STATE.context?.state || {};
    return {
      url: String(state.url || ""),
      rappid: String(state.brainstem?.callerRappid || ""),
      compositionHash: String(state.brainstem?.compositionHash || ""),
      model: String(capture.model || "auto"),
    };
  }

  function routeKey(state = SCRIPT_STATE.context?.state) {
    return [
      state?.brainstem?.callerRappid || "",
      state?.brainstem?.compositionHash || "",
    ].join("|");
  }

  function assertTileRoute(tile) {
    const current = routeKey();
    const stored = [
      tile.route?.rappid || "",
      tile.route?.compositionHash || "",
    ].join("|");
    if (!tile.route?.rappid || !tile.route?.compositionHash || stored !== current) {
      throw new Error(
        "This tile belongs to a different Brainstem route or composition and cannot be restored here.",
      );
    }
  }

  async function persistCapture(capture) {
    if (!hasConversation(capture)) {
      throw new Error("There is no Brainstem conversation to park.");
    }
    const boundToCurrentFrame = (
      SCRIPT_STATE.primaryFrameGeneration
        === SCRIPT_STATE.context.frameGeneration
      && SCRIPT_STATE.primaryRouteKey === routeKey()
    );
    const existing = SCRIPT_STATE.primaryId && boundToCurrentFrame
      ? SCRIPT_STATE.tiles.find((tile) => tile.id === SCRIPT_STATE.primaryId)
      : null;
    if (!boundToCurrentFrame) SCRIPT_STATE.primaryId = null;
    const tile = await SCRIPT_STATE.context.api.tilesPark({
      ...(existing || {}),
      ...(existing ? { id: existing.id } : {}),
      title: capture.title,
      route: routeForCapture(capture),
      turns: capture.turns,
      history: capture.restorable
        ? capture.history
        : existing?.history || capture.history,
      restorable: capture.restorable || existing?.restorable === true,
      restoreError: capture.restorable || existing?.restorable === true
        ? null
        : capture.restoreError,
      table: existing?.table || { faceUp: true },
    });
    postToFrame({
      type: "rapp-beta:tile-parked",
      id: tile.id,
      requestIds: capture.pendingRequestIds || [],
    });
    SCRIPT_STATE.primaryId = null;
    SCRIPT_STATE.primaryFrameGeneration = null;
    SCRIPT_STATE.primaryRouteKey = null;
    return tile;
  }

  async function parkCurrent() {
    const capture = await requestCapture();
    const tile = await persistCapture(capture);
    await refreshTiles();
    showToast(`Parked "${tile.title}".`);
    return tile;
  }

  async function wakeTile(id) {
    const requested = SCRIPT_STATE.tiles.find((tile) => tile.id === id);
    if (requested?.restorable === false) {
      throw new Error(requested.restoreError || "This tile cannot be restored.");
    }
    assertTileRoute(requested);
    if (
      SCRIPT_STATE.primaryId === id
      && SCRIPT_STATE.primaryFrameGeneration
        === SCRIPT_STATE.context.frameGeneration
      && SCRIPT_STATE.primaryRouteKey === routeKey()
    ) {
      const winner = await SCRIPT_STATE.context.api.tilesWake(id);
      await refreshTiles();
      return winner;
    }
    if (SCRIPT_STATE.primaryId !== id) {
      const current = await requestCapture();
      if (hasConversation(current)) await persistCapture(current);
    }
    const tile = await SCRIPT_STATE.context.api.tilesWake(id);
    SCRIPT_STATE.primaryId = tile.id;
    SCRIPT_STATE.primaryFrameGeneration = SCRIPT_STATE.context.frameGeneration;
    SCRIPT_STATE.primaryRouteKey = routeKey();
    postToFrame({ type: "rapp-beta:tile-wake", tile });
    await refreshTiles();
    showToast(`Woke "${tile.title}".`);
    return tile;
  }

  async function foldTile(id) {
    if (SCRIPT_STATE.primaryId === id) {
      const current = await requestCapture();
      if (hasConversation(current)) await persistCapture(current);
    }
    const result = await SCRIPT_STATE.context.api.tilesFold(id);
    if (SCRIPT_STATE.primaryId === id) {
      SCRIPT_STATE.primaryId = null;
      SCRIPT_STATE.primaryFrameGeneration = null;
      SCRIPT_STATE.primaryRouteKey = null;
      postToFrame({ type: "rapp-beta:tile-clear" });
    }
    await refreshTiles();
    showToast(`Folded "${result.tile.title}".`, {
      actionLabel: "Undo",
      action: async () => {
        await SCRIPT_STATE.context.api.tilesUndo(id);
        await refreshTiles();
      },
      duration: 10000,
    });
    return result.tile;
  }

  async function raceTile(id) {
    const source = SCRIPT_STATE.tiles.find((tile) => tile.id === id);
    assertTileRoute(source);
    const current = await requestCapture();
    if (hasConversation(current)) await persistCapture(current);
    const race = await SCRIPT_STATE.context.api.tilesRace(id);
    const raceTarget = document.querySelector(".dimension-tile-race-target")?.value
      || "brainstem";
    if (raceTarget.startsWith("twin:")) {
      const twinId = raceTarget.slice(5);
      const result = await SCRIPT_STATE.context.api.twinChat(
        twinId,
        race.question,
      );
      const reply = String(
        result.response || result.assistant_response || result.result || "",
      );
      if (!reply) throw new Error(`Twin ${twinId} returned an empty race reply.`);
      await SCRIPT_STATE.context.api.tilesComplete(race.contender.id, {
        reply,
        html: "",
        history: [
          { role: "user", content: race.question },
          { role: "assistant", content: reply },
        ],
        model: `twin:${twinId}`,
        requestId: `twin-${crypto.randomUUID()}`,
      });
      SCRIPT_STATE.primaryId = null;
      SCRIPT_STATE.primaryFrameGeneration = null;
      SCRIPT_STATE.primaryRouteKey = null;
      await refreshTiles();
      showToast(`Twin ${twinId} answered the race.`);
      return race;
    }
    SCRIPT_STATE.primaryId = race.contender.id;
    SCRIPT_STATE.primaryFrameGeneration = SCRIPT_STATE.context.frameGeneration;
    SCRIPT_STATE.primaryRouteKey = routeKey();
    postToFrame({
      type: "rapp-beta:tile-race",
      id: race.contender.id,
      question: race.question,
    });
    await refreshTiles();
    showToast(
      "Race staged. Pick a model or companion, then send the question.",
      { duration: 10000 },
    );
    return race;
  }

  async function populateRaceTargets() {
    const select = document.querySelector(".dimension-tile-race-target");
    if (!select) return;
    const selected = select.value || "brainstem";
    select.replaceChildren();
    const brainstem = document.createElement("option");
    brainstem.value = "brainstem";
    brainstem.textContent = "Race target: Brainstem model";
    select.appendChild(brainstem);
    let twins;
    try {
      twins = await SCRIPT_STATE.context.api.twinList();
    } catch (error) {
      showError(new Error(
        `Twin race targets are unavailable: ${String(error?.message || error)}`,
      ));
      return;
    }
    for (const twin of twins || []) {
      const option = document.createElement("option");
      option.value = `twin:${twin.id}`;
      option.textContent = `Race target: ${twin.name || twin.id}`;
      select.appendChild(option);
    }
    if ([...select.options].some((option) => option.value === selected)) {
      select.value = selected;
    }
  }

  function tileCanRace(tile) {
    if (tile.status === "racing") return false;
    const lastUser = [...(tile.turns || [])]
      .reverse()
      .find((turn) => turn.role === "user");
    return Boolean(lastUser?.text?.trim().endsWith("?"));
  }

  function tileExcerpt(tile) {
    const last = [...(tile.turns || [])]
      .reverse()
      .find((turn) => !turn.pending && turn.text);
    const text = String(last?.text || "Waiting for a reply...").trim();
    return [...text].slice(0, 140).join("");
  }

  function attachSwipe(element, tile) {
    let pointerId = null;
    let startX = 0;
    let deltaX = 0;
    let wheelDelta = 0;
    let wheelTimer = null;
    const reset = () => {
      pointerId = null;
      deltaX = 0;
      element.classList.remove("swiping");
      element.style.removeProperty("--swipe-x");
      element.style.removeProperty("--swipe-tilt");
    };
    element.addEventListener("pointerdown", (event) => {
      if (event.target.closest("button,select,a,input")) return;
      pointerId = event.pointerId;
      startX = event.clientX;
      try {
        element.setPointerCapture?.(pointerId);
      } catch {
        // Synthetic UI-driver pointers do not belong to a native pointer stream.
      }
      element.classList.add("swiping");
    });
    element.addEventListener("pointermove", (event) => {
      if (pointerId !== event.pointerId) return;
      deltaX = event.clientX - startX;
      element.style.setProperty("--swipe-x", `${deltaX}px`);
      element.style.setProperty(
        "--swipe-tilt",
        `${Math.max(-10, Math.min(10, deltaX / 14))}deg`,
      );
    });
    element.addEventListener("pointerup", (event) => {
      if (pointerId !== event.pointerId) return;
      const movement = deltaX;
      reset();
      if (movement >= 72) void wakeTile(tile.id).catch(showError);
      else if (movement <= -72) void foldTile(tile.id).catch(showError);
    });
    element.addEventListener("pointercancel", reset);
    element.addEventListener("wheel", (event) => {
      if (Math.abs(event.deltaX) <= Math.abs(event.deltaY)) return;
      event.preventDefault();
      wheelDelta += event.deltaX;
      clearTimeout(wheelTimer);
      wheelTimer = setTimeout(() => { wheelDelta = 0; }, 260);
      if (Math.abs(wheelDelta) < 72) return;
      const movement = wheelDelta;
      wheelDelta = 0;
      clearTimeout(wheelTimer);
      if (movement > 0) void wakeTile(tile.id).catch(showError);
      else void foldTile(tile.id).catch(showError);
    }, { passive: false });
  }

  function attachTileDrag(handle, element, tile) {
    handle.draggable = true;
    handle.addEventListener("dragstart", (event) => {
      event.dataTransfer.effectAllowed = "move";
      event.dataTransfer.setData("application/x-rapp-dimension-tile", tile.id);
      element.classList.add("dragging");
    });
    handle.addEventListener("dragend", () => element.classList.remove("dragging"));
  }

  function createTile(tile, { folded = false } = {}) {
    const element = document.createElement("article");
    element.className = `dimension-tile${folded ? " folded" : ""}`;
    element.dataset.dimensionTile = tile.id;
    element.dataset.drive = driveTile(tile.id);
    element.dataset.seat = tile.table?.seat || "";
    element.dataset.status = tile.status;
    const seat = Number(tile.table?.seat) || 1;
    element.style.setProperty("--fan-angle", `${(seat - 6) * 2}deg`);
    element.tabIndex = 0;
    element.setAttribute(
      "aria-label",
      `${tile.title}, ${tile.status} dimension tile`,
    );

    const corner = document.createElement("span");
    corner.className = "dimension-tile-corner";
    corner.textContent = String(tile.turns?.length || 0);
    const drag = document.createElement("span");
    drag.className = "dimension-tile-drag";
    drag.dataset.drive = driveTile(tile.id, "drag");
    drag.title = "Drag this tile onto the Brainstem";
    drag.setAttribute("aria-label", `Drag ${tile.title}`);
    drag.textContent = "⠿";
    const face = document.createElement("div");
    face.className = "dimension-tile-face";
    const banner = document.createElement("div");
    banner.className = "dimension-tile-banner";
    const title = document.createElement("strong");
    title.textContent = tile.title;
    const status = document.createElement("span");
    status.textContent = tile.status;
    banner.append(title, status);
    const art = document.createElement("div");
    art.className = "dimension-tile-art";
    art.setAttribute("aria-hidden", "true");
    for (let index = 0; index < Math.min(6, tile.turns?.length || 0); index += 1) {
      const pip = document.createElement("i");
      art.appendChild(pip);
    }
    const excerpt = document.createElement("p");
    excerpt.textContent = tileExcerpt(tile);
    const meta = document.createElement("div");
    meta.className = "dimension-tile-meta";
    meta.textContent = `${tile.route?.model || "auto"} · ${
      tile.turns?.length || 0
    } turns`;
    const actions = document.createElement("div");
    actions.className = "dimension-tile-actions";
    const wake = document.createElement("button");
    wake.type = "button";
    wake.dataset.drive = driveTile(tile.id, "wake");
    wake.textContent = "Wake";
    wake.disabled = tile.restorable === false;
    wake.title = tile.restorable === false
      ? tile.restoreError
      : "Wake this chat in the Brainstem.";
    wake.addEventListener("click", () => void wakeTile(tile.id).catch(showError));
    actions.appendChild(wake);
    if (!folded) {
      const race = document.createElement("button");
      race.type = "button";
      race.dataset.drive = driveTile(tile.id, "race");
      race.textContent = "Race";
      race.disabled = !tileCanRace(tile);
      race.title = race.disabled
        ? "The last user turn must be a question."
        : "Race this question with another model or companion.";
      race.addEventListener(
        "click",
        () => void raceTile(tile.id).catch(showError),
      );
      const fold = document.createElement("button");
      fold.type = "button";
      fold.dataset.drive = driveTile(tile.id, "fold");
      fold.textContent = "Fold";
      fold.addEventListener(
        "click",
        () => void foldTile(tile.id).catch(showError),
      );
      actions.append(race, fold);
    }
    face.append(banner, art, excerpt, meta, actions);
    element.append(corner, drag, face);
    attachSwipe(element, tile);
    attachTileDrag(drag, element, tile);
    element.addEventListener("keydown", (event) => {
      if (event.key === "ArrowRight" || event.key === "Enter") {
        event.preventDefault();
        void wakeTile(tile.id).catch(showError);
      } else if (event.key === "ArrowLeft" && !folded) {
        event.preventDefault();
        void foldTile(tile.id).catch(showError);
      } else if (event.key.toLowerCase() === "r" && !folded && tileCanRace(tile)) {
        event.preventDefault();
        void raceTile(tile.id).catch(showError);
      }
    });
    const custom = SCRIPT_STATE.context?.state?.tableLayout;
    if (SCRIPT_STATE.context?.tableView?.layout === "custom" && custom) {
      const seat = Number(tile.table?.seat) || 1;
      const faceDown = custom.faceDownRule === "all"
        || (custom.faceDownRule === "folded" && tile.status === "folded")
        || (custom.faceDownRule === "alternate" && seat % 2 === 0);
      element.classList.toggle("face-down", faceDown);
    }
    return element;
  }

  function applyCustomPosition(element, tile, customLayout) {
    const seat = Number(tile.table?.seat) || 1;
    const position = customLayout?.seatPositions?.[(seat - 1)
      % customLayout.seatPositions.length];
    if (!position) return;
    element.style.setProperty("--custom-x", `${position.x}%`);
    element.style.setProperty("--custom-y", `${position.y}%`);
    element.style.setProperty("--custom-rotation", `${position.rotation}deg`);
  }

  function renderDiscard(surface, folded) {
    let pile = surface.querySelector(".dimension-tile-discard");
    if (!folded.length) {
      pile?.remove();
      return;
    }
    if (!pile) {
      pile = document.createElement("section");
      pile.className = "dimension-tile-discard";
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.drive = "tableView.discard";
      button.addEventListener("click", () => {
        pile.classList.toggle("open");
        button.setAttribute(
          "aria-expanded",
          String(pile.classList.contains("open")),
        );
      });
      pile.appendChild(button);
      surface.appendChild(pile);
    }
    const button = pile.querySelector("button");
    button.textContent = `Discard pile · ${folded.length}`;
    pile.querySelectorAll(".dimension-tile.folded").forEach((tile) => tile.remove());
    for (const [index, tile] of folded.entries()) {
      const element = createTile(tile, { folded: true });
      const spread = Math.min(8, 48 / Math.max(1, folded.length));
      element.style.setProperty(
        "--pile-angle",
        `${(index - ((folded.length - 1) / 2)) * spread}deg`,
      );
      element.style.setProperty("--pile-offset", `${index * -7}px`);
      pile.appendChild(element);
    }
  }

  function renderOverflow(surface, overflowTiles) {
    let pile = surface.querySelector(".dimension-tile-overflow");
    if (!overflowTiles.length) {
      pile?.remove();
      return;
    }
    if (!pile) {
      pile = document.createElement("section");
      pile.className = "dimension-tile-overflow";
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.drive = "tableView.overflow";
      button.addEventListener("click", () => {
        pile.classList.toggle("open");
        button.setAttribute(
          "aria-expanded",
          String(pile.classList.contains("open")),
        );
      });
      pile.appendChild(button);
      surface.appendChild(pile);
    }
    pile.querySelector("button").textContent =
      `Overflow pile · ${overflowTiles.length}`;
    pile.querySelectorAll(".dimension-tile").forEach((tile) => tile.remove());
    for (const [index, tile] of overflowTiles.entries()) {
      const element = createTile(tile);
      const spread = Math.min(8, 48 / Math.max(1, overflowTiles.length));
      element.style.setProperty(
        "--pile-angle",
        `${(index - ((overflowTiles.length - 1) / 2)) * spread}deg`,
      );
      element.style.setProperty("--pile-offset", `${index * 7}px`);
      pile.appendChild(element);
    }
  }

  function renderTiles() {
    const surface = document.querySelector(".dimension-tile-surface");
    if (!surface) return;
    surface.querySelectorAll(":scope > .dimension-tile").forEach((tile) => tile.remove());
    surface.querySelector(".dimension-tile-overflow")?.remove();
    const active = SCRIPT_STATE.tiles.filter((tile) => tile.status !== "folded");
    const folded = SCRIPT_STATE.tiles.filter((tile) => tile.status === "folded");
    const custom = SCRIPT_STATE.context?.state?.tableLayout;
    for (const tile of active.slice(0, 12)) {
      const element = createTile(tile);
      if (SCRIPT_STATE.context.tableView.layout === "custom") {
        applyCustomPosition(element, tile, custom);
      }
      surface.appendChild(element);
    }
    renderOverflow(surface, active.slice(12));
    renderDiscard(surface, folded);
  }

  function applyLayout() {
    const herd = document.getElementById("surgeon-herd");
    const surface = herd?.querySelector(".dimension-tile-surface");
    if (!herd || !surface) return;
    for (const name of ["table", "row", "focus", "grid", "stack", "custom"]) {
      herd.classList.remove(`tile-layout-${name}`);
    }
    const layoutName = SCRIPT_STATE.context.tableView.layout || "table";
    herd.classList.add("dimension-tile-view", `tile-layout-${layoutName}`);
    herd.dataset.tableLayout = layoutName;
    const custom = SCRIPT_STATE.context.state.tableLayout;
    if (layoutName === "custom" && custom) {
      surface.style.setProperty("--table-surface", custom.surfaceColor);
      surface.style.setProperty("--tile-width", `${custom.tileSize.width}px`);
      surface.style.setProperty("--tile-height", `${custom.tileSize.height}px`);
      surface.dataset.faceDownRule = custom.faceDownRule;
      surface.dataset.arrangePattern = custom.arrangePattern;
    } else {
      surface.style.removeProperty("--table-surface");
      surface.style.removeProperty("--tile-width");
      surface.style.removeProperty("--tile-height");
      delete surface.dataset.faceDownRule;
      delete surface.dataset.arrangePattern;
    }
    const layout = document.querySelector(".dimension-tile-layout");
    if (layout) layout.value = layoutName;
    document.querySelector(".dimension-tile-load-custom")
      ?.toggleAttribute("hidden", layoutName !== "custom");
  }

  async function changeLayout(value) {
    if (value === "custom") {
      const loaded = await SCRIPT_STATE.context.api.tilesLoadCustomLayout();
      if (loaded.canceled) {
        document.querySelector(".dimension-tile-layout").value =
          SCRIPT_STATE.context.tableView.layout;
      }
      return;
    }
    await SCRIPT_STATE.context.api.setTableView({ layout: value });
  }

  function randomIndex(length) {
    if (length < 1) return -1;
    const values = new Uint32Array(1);
    crypto.getRandomValues(values);
    return values[0] % length;
  }

  async function runArrange(action) {
    const surface = document.querySelector(".dimension-tile-surface");
    if (!surface || !action) return;
    surface.classList.remove("arrange-reorder", "arrange-spread", "arrange-distribute", "arrange-open");
    void surface.offsetWidth;
    surface.classList.add(`arrange-${action}`);
    if (action === "open-one") {
      const candidates = SCRIPT_STATE.tiles.filter((tile) => (
        tile.status === "parked" || tile.status === "racing"
      ));
      const index = randomIndex(candidates.length);
      if (index < 0) throw new Error("There is no parked tile to draw.");
      await new Promise((resolve) => addTimer(resolve, 320));
      await wakeTile(candidates[index].id);
    }
  }

  function ensureControls(herd, surface) {
    let controls = herd.querySelector(".dimension-tile-controls");
    if (controls) return controls;
    controls = document.createElement("div");
    controls.className = "dimension-tile-controls";
    controls.dataset.drive = "tableView.controls";
    const label = document.createElement("strong");
    label.textContent = "Table view";
    const layout = document.createElement("select");
    layout.className = "dimension-tile-layout";
    layout.dataset.drive = "tableView.layout";
    layout.setAttribute("aria-label", "Table layout");
    const labels = {
      table: "Table",
      row: "Rows",
      focus: "Focus",
      grid: "Grid",
      stack: "Stack",
      custom: "Custom…",
    };
    for (const [value, text] of Object.entries(labels)) {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = text;
      layout.appendChild(option);
    }
    layout.addEventListener("change", () => {
      void changeLayout(layout.value).catch(showError);
    });
    const load = document.createElement("button");
    load.type = "button";
    load.className = "dimension-tile-load-custom";
    load.dataset.drive = "tableView.loadCustom";
    load.textContent = "Load layout…";
    load.addEventListener("click", () => {
      void SCRIPT_STATE.context.api.tilesLoadCustomLayout().catch(showError);
    });
    const raceTarget = document.createElement("select");
    raceTarget.className = "dimension-tile-race-target";
    raceTarget.dataset.drive = "tableView.raceTarget";
    raceTarget.setAttribute("aria-label", "Race target");
    const arrange = document.createElement("select");
    arrange.dataset.drive = "tableView.arrange";
    arrange.setAttribute("aria-label", "Arrange tiles");
    for (const [value, text] of [
      ["", "Arrange…"],
      ["reorder", "Reorder"],
      ["fan", "Spread"],
      ["distribute", "Distribute"],
      ["open-one", "Open one"],
    ]) {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = text;
      arrange.appendChild(option);
    }
    arrange.addEventListener("change", () => {
      const action = arrange.value;
      arrange.value = "";
      void runArrange(action).catch(showError);
    });
    controls.append(label, layout, load, raceTarget, arrange);
    herd.insertBefore(controls, surface);
    return controls;
  }

  function ensureGrabHandle() {
    let grab = document.getElementById("brainstem-chat-grab");
    if (grab) return grab;
    grab = document.createElement("button");
    grab.id = "brainstem-chat-grab";
    grab.type = "button";
    grab.draggable = true;
    grab.dataset.drive = "brainstem.grab";
    grab.title = "Grab this chat and park it in the herd";
    grab.innerHTML = "<span aria-hidden=\"true\">▤</span> Park chat";
    grab.addEventListener("click", () => void parkCurrent().catch(showError));
    grab.addEventListener("dragstart", (event) => {
      event.dataTransfer.effectAllowed = "move";
      event.dataTransfer.setData("application/x-rapp-brainstem-chat", "park");
    });
    document.querySelector("main")?.appendChild(grab);
    return grab;
  }

  function ensureSurface(herd, grid) {
    let surface = herd.querySelector(".dimension-tile-surface");
    if (!surface) {
      surface = document.createElement("section");
      surface.className = "dimension-tile-surface";
      surface.dataset.drive = "tableView.surface";
      surface.setAttribute("aria-label", "Parked Brainstem dimension tiles");
      herd.insertBefore(surface, grid);
    }
    return surface;
  }

  function installDragTargets(herd) {
    const signal = SCRIPT_STATE.controller.signal;
    herd.addEventListener("dragover", (event) => {
      if (event.dataTransfer.types.includes("application/x-rapp-brainstem-chat")) {
        event.preventDefault();
        event.dataTransfer.dropEffect = "move";
      }
    }, { signal });
    herd.addEventListener("drop", (event) => {
      if (!event.dataTransfer.getData("application/x-rapp-brainstem-chat")) return;
      event.preventDefault();
      void parkCurrent().catch(showError);
    }, { signal });
    const main = document.querySelector("main");
    main?.addEventListener("dragover", (event) => {
      if (event.dataTransfer.types.includes("application/x-rapp-dimension-tile")) {
        event.preventDefault();
        event.dataTransfer.dropEffect = "move";
      }
    }, { signal });
    main?.addEventListener("drop", (event) => {
      const id = event.dataTransfer.getData("application/x-rapp-dimension-tile");
      if (!id) return;
      event.preventDefault();
      void wakeTile(id).catch(showError);
    }, { signal });
  }

  function receiveFrameMessage(event) {
    if (event.source !== SCRIPT_STATE.context?.frame?.contentWindow) return;
    if (event.data?.type === "rapp-beta:tile-capture-result") {
      const waiter = SCRIPT_STATE.captureWaiters.get(event.data.requestId);
      if (!waiter) return;
      SCRIPT_STATE.captureWaiters.delete(event.data.requestId);
      if (event.data.ok) waiter.resolve(event.data.tile);
      else waiter.reject(new Error(event.data.error || "Chat capture failed."));
      return;
    }
  }

  function completionSaved(event) {
    if (!SCRIPT_STATE.enabled) return;
    if (
      event.restoreInFrame
      && SCRIPT_STATE.primaryId === event.id
    ) {
      postToFrame({
        type: "rapp-beta:tile-late-completion",
        completion: event.completion,
      });
    }
    void refreshTiles().catch(showError);
  }

  function completionFailed(error) {
    if (SCRIPT_STATE.enabled) showError(error);
  }

  function tileDetached(id) {
    if (!SCRIPT_STATE.enabled || SCRIPT_STATE.primaryId !== id) return;
    const detached = SCRIPT_STATE.tiles.find((tile) => tile.id === id);
    SCRIPT_STATE.primaryId = null;
    SCRIPT_STATE.primaryFrameGeneration = null;
    SCRIPT_STATE.primaryRouteKey = null;
    if (detached) {
      void SCRIPT_STATE.context.api.tilesParkExisting(detached.id)
        .then(refreshTiles)
        .catch(showError);
    }
  }

  function frameChanged({ generation } = {}) {
    if (SCRIPT_STATE.context) {
      SCRIPT_STATE.context.frameGeneration = generation;
    }
    if (
      SCRIPT_STATE.primaryId
      && SCRIPT_STATE.primaryFrameGeneration !== generation
    ) {
      const detached = SCRIPT_STATE.tiles.find((tile) => (
        tile.id === SCRIPT_STATE.primaryId
      ));
      SCRIPT_STATE.primaryId = null;
      SCRIPT_STATE.primaryFrameGeneration = null;
      SCRIPT_STATE.primaryRouteKey = null;
      if (SCRIPT_STATE.enabled && detached) {
        void SCRIPT_STATE.context.api.tilesParkExisting(detached.id)
          .then(refreshTiles)
          .catch(showError);
      }
    }
  }

  async function refreshTiles() {
    if (!SCRIPT_STATE.enabled) return [];
    const sequence = ++SCRIPT_STATE.refreshSequence;
    const tiles = await SCRIPT_STATE.context.api.tilesList();
    if (!SCRIPT_STATE.enabled || sequence !== SCRIPT_STATE.refreshSequence) {
      return tiles;
    }
    SCRIPT_STATE.tiles = tiles;
    renderTiles();
    return tiles;
  }

  async function enable(context) {
    SCRIPT_STATE.context = context;
    if (SCRIPT_STATE.enabled) {
      applyLayout();
      await populateRaceTargets();
      await refreshTiles();
      return;
    }
    SCRIPT_STATE.enabled = true;
    SCRIPT_STATE.controller = new AbortController();
    SCRIPT_STATE.openedHerd = document.body.classList.contains(
      "surgeon-herd-open",
    );
    SCRIPT_STATE.createdHerd = !context.hadHerdDom;
    try {
      installStyles();
      context.enterHerd();
      const { grid, herd } = context.ensureHerd();
      const surface = ensureSurface(herd, grid);
      ensureControls(herd, surface);
      ensureGrabHandle();
      installDragTargets(herd);
      window.addEventListener("message", receiveFrameMessage, {
        signal: SCRIPT_STATE.controller.signal,
      });
      applyLayout();
      if (context.state.tableLayoutError) showError(context.state.tableLayoutError);
      await populateRaceTargets();
      await refreshTiles();
      postToFrame({ type: "rapp-beta:tile-ready" });
      addTimer(() => postToFrame({ type: "rapp-beta:tile-ready" }), 150);
      addTimer(() => postToFrame({ type: "rapp-beta:tile-ready" }), 600);
    } catch (error) {
      disable();
      throw error;
    }
  }

  function disable() {
    if (!SCRIPT_STATE.enabled) {
      if (typeof document !== "undefined") {
        removeStyles();
        document.getElementById("__rappDimensionTilesScript")?.remove();
      }
      return;
    }
    SCRIPT_STATE.enabled = false;
    SCRIPT_STATE.refreshSequence += 1;
    SCRIPT_STATE.controller?.abort();
    SCRIPT_STATE.controller = null;
    for (const timer of SCRIPT_STATE.timers) clearTimeout(timer);
    SCRIPT_STATE.timers.clear();
    for (const waiter of SCRIPT_STATE.captureWaiters.values()) {
      waiter.reject(new Error("Table view was turned off."));
    }
    SCRIPT_STATE.captureWaiters.clear();
    document.getElementById("brainstem-chat-grab")?.remove();
    document.querySelector(".dimension-tile-controls")?.remove();
    document.querySelector(".dimension-tile-surface")?.remove();
    document.querySelector(".dimension-tile-toast")?.remove();
    const herd = document.getElementById("surgeon-herd");
    if (herd) {
      herd.className = herd.className
        .split(/\s+/)
        .filter((name) => !name.startsWith("tile-layout-")
          && name !== "dimension-tile-view")
        .join(" ");
      delete herd.dataset.tableLayout;
    }
    removeStyles();
    document.getElementById("__rappDimensionTilesScript")?.remove();
    if (SCRIPT_STATE.createdHerd) {
      SCRIPT_STATE.context?.destroyHerd();
    } else if (!SCRIPT_STATE.openedHerd) {
      SCRIPT_STATE.context?.exitHerd();
    }
    SCRIPT_STATE.tiles = [];
    SCRIPT_STATE.createdHerd = false;
    SCRIPT_STATE.context = null;
    SCRIPT_STATE.primaryId = null;
    SCRIPT_STATE.primaryFrameGeneration = null;
    SCRIPT_STATE.primaryRouteKey = null;
  }

  root.RappDimensionTiles = Object.freeze({
    tileDetached,
    completionFailed,
    completionSaved,
    disable,
    enabled: () => SCRIPT_STATE.enabled,
    frameChanged,
    parkCurrent,
    refresh: refreshTiles,
    sync: enable,
  });
})(globalThis);
