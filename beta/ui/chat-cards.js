(function registerChatCards(root) {
  const STYLE_ID = "__rappChatCardsStyle";
  const SCRIPT_STATE = {
    cards: [],
    captureWaiters: new Map(),
    context: null,
    controller: null,
    enabled: false,
    openedHerd: false,
    primaryId: null,
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

  function driveCard(id, part = "") {
    return `herd.card[${id}]${part ? `.${part}` : ""}`;
  }

  function installStyles() {
    let link = document.getElementById(STYLE_ID);
    if (link) return link;
    link = document.createElement("link");
    link.id = STYLE_ID;
    link.rel = "stylesheet";
    link.href = new URL("chat-cards.css", document.baseURI).href;
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
    document.querySelector(".chat-card-toast")?.remove();
    const toast = document.createElement("div");
    toast.className = "chat-card-toast";
    toast.dataset.drive = "cardTable.toast";
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
        type: "rapp-beta:card-capture",
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

  async function persistCapture(capture) {
    if (!hasConversation(capture)) {
      throw new Error("There is no Brainstem conversation to park.");
    }
    const existing = SCRIPT_STATE.primaryId
      ? SCRIPT_STATE.cards.find((card) => card.id === SCRIPT_STATE.primaryId)
      : null;
    const card = await SCRIPT_STATE.context.api.cardsPark({
      ...(existing || {}),
      ...(existing ? { id: existing.id } : {}),
      title: capture.title,
      route: routeForCapture(capture),
      turns: capture.turns,
      history: capture.history,
      table: existing?.table || { faceUp: true },
    });
    postToFrame({ type: "rapp-beta:card-parked", id: card.id });
    SCRIPT_STATE.primaryId = null;
    return card;
  }

  async function parkCurrent() {
    const capture = await requestCapture();
    const card = await persistCapture(capture);
    await refreshCards();
    showToast(`Parked "${card.title}".`);
    return card;
  }

  async function wakeCard(id) {
    if (SCRIPT_STATE.primaryId !== id) {
      const current = await requestCapture();
      if (hasConversation(current)) await persistCapture(current);
    }
    const card = await SCRIPT_STATE.context.api.cardsWake(id);
    SCRIPT_STATE.primaryId = card.id;
    postToFrame({ type: "rapp-beta:card-wake", card });
    await refreshCards();
    showToast(`Woke "${card.title}".`);
    return card;
  }

  async function foldCard(id) {
    const result = await SCRIPT_STATE.context.api.cardsFold(id);
    if (SCRIPT_STATE.primaryId === id) {
      SCRIPT_STATE.primaryId = null;
      postToFrame({ type: "rapp-beta:card-clear" });
    }
    await refreshCards();
    showToast(`Folded "${result.card.title}".`, {
      actionLabel: "Undo",
      action: async () => {
        await SCRIPT_STATE.context.api.cardsUndo(id);
        await refreshCards();
      },
      duration: 10000,
    });
    return result.card;
  }

  async function raceCard(id) {
    const current = await requestCapture();
    if (hasConversation(current)) await persistCapture(current);
    const race = await SCRIPT_STATE.context.api.cardsRace(id);
    SCRIPT_STATE.primaryId = null;
    postToFrame({
      type: "rapp-beta:card-race",
      id: race.contender.id,
      question: race.question,
    });
    await refreshCards();
    showToast(
      "Race staged. Pick a model or companion, then send the question.",
      { duration: 10000 },
    );
    return race;
  }

  function cardCanRace(card) {
    const lastUser = [...(card.turns || [])]
      .reverse()
      .find((turn) => turn.role === "user");
    return Boolean(lastUser?.text?.trim().endsWith("?"));
  }

  function cardExcerpt(card) {
    const last = [...(card.turns || [])]
      .reverse()
      .find((turn) => !turn.pending && turn.text);
    const text = String(last?.text || "Waiting for a reply...").trim();
    return [...text].slice(0, 140).join("");
  }

  function attachSwipe(tile, card) {
    let pointerId = null;
    let startX = 0;
    let deltaX = 0;
    const reset = () => {
      pointerId = null;
      deltaX = 0;
      tile.classList.remove("swiping");
      tile.style.removeProperty("--swipe-x");
      tile.style.removeProperty("--swipe-tilt");
    };
    tile.addEventListener("pointerdown", (event) => {
      if (event.target.closest("button,select,a,input")) return;
      pointerId = event.pointerId;
      startX = event.clientX;
      tile.setPointerCapture?.(pointerId);
      tile.classList.add("swiping");
    });
    tile.addEventListener("pointermove", (event) => {
      if (pointerId !== event.pointerId) return;
      deltaX = event.clientX - startX;
      tile.style.setProperty("--swipe-x", `${deltaX}px`);
      tile.style.setProperty(
        "--swipe-tilt",
        `${Math.max(-10, Math.min(10, deltaX / 14))}deg`,
      );
    });
    tile.addEventListener("pointerup", (event) => {
      if (pointerId !== event.pointerId) return;
      const movement = deltaX;
      reset();
      if (movement >= 72) void wakeCard(card.id).catch(showError);
      else if (movement <= -72) void foldCard(card.id).catch(showError);
    });
    tile.addEventListener("pointercancel", reset);
  }

  function attachCardDrag(tile, card) {
    tile.draggable = true;
    tile.addEventListener("dragstart", (event) => {
      event.dataTransfer.effectAllowed = "move";
      event.dataTransfer.setData("application/x-rapp-chat-card", card.id);
      tile.classList.add("dragging");
    });
    tile.addEventListener("dragend", () => tile.classList.remove("dragging"));
  }

  function cardTile(card, { folded = false } = {}) {
    const tile = document.createElement("article");
    tile.className = `chat-card${folded ? " folded" : ""}`;
    tile.dataset.chatCard = card.id;
    tile.dataset.drive = driveCard(card.id);
    tile.dataset.seat = card.table?.seat || "";
    tile.dataset.status = card.status;
    tile.tabIndex = 0;
    tile.setAttribute("aria-label", `${card.title}, ${card.status} chat card`);

    const corner = document.createElement("span");
    corner.className = "chat-card-corner";
    corner.textContent = String(card.turns?.length || 0);
    const face = document.createElement("div");
    face.className = "chat-card-face";
    const banner = document.createElement("div");
    banner.className = "chat-card-banner";
    const title = document.createElement("strong");
    title.textContent = card.title;
    const status = document.createElement("span");
    status.textContent = card.status;
    banner.append(title, status);
    const art = document.createElement("div");
    art.className = "chat-card-art";
    art.setAttribute("aria-hidden", "true");
    for (let index = 0; index < Math.min(6, card.turns?.length || 0); index += 1) {
      const pip = document.createElement("i");
      art.appendChild(pip);
    }
    const excerpt = document.createElement("p");
    excerpt.textContent = cardExcerpt(card);
    const meta = document.createElement("div");
    meta.className = "chat-card-meta";
    meta.textContent = `${card.route?.model || "auto"} · ${
      card.turns?.length || 0
    } turns`;
    const actions = document.createElement("div");
    actions.className = "chat-card-actions";
    const wake = document.createElement("button");
    wake.type = "button";
    wake.dataset.drive = driveCard(card.id, "wake");
    wake.textContent = "Wake";
    wake.addEventListener("click", () => void wakeCard(card.id).catch(showError));
    actions.appendChild(wake);
    if (!folded) {
      const race = document.createElement("button");
      race.type = "button";
      race.dataset.drive = driveCard(card.id, "race");
      race.textContent = "Race";
      race.disabled = !cardCanRace(card);
      race.title = race.disabled
        ? "The last user turn must be a question."
        : "Race this question with another model or companion.";
      race.addEventListener(
        "click",
        () => void raceCard(card.id).catch(showError),
      );
      const fold = document.createElement("button");
      fold.type = "button";
      fold.dataset.drive = driveCard(card.id, "fold");
      fold.textContent = "Fold";
      fold.addEventListener(
        "click",
        () => void foldCard(card.id).catch(showError),
      );
      actions.append(race, fold);
    }
    face.append(banner, art, excerpt, meta, actions);
    tile.append(corner, face);
    attachSwipe(tile, card);
    attachCardDrag(tile, card);
    tile.addEventListener("keydown", (event) => {
      if (event.key === "ArrowRight" || event.key === "Enter") {
        event.preventDefault();
        void wakeCard(card.id).catch(showError);
      } else if (event.key === "ArrowLeft" && !folded) {
        event.preventDefault();
        void foldCard(card.id).catch(showError);
      } else if (event.key.toLowerCase() === "r" && !folded && cardCanRace(card)) {
        event.preventDefault();
        void raceCard(card.id).catch(showError);
      }
    });
    return tile;
  }

  function applyCustomPosition(tile, card, customTable) {
    const seat = Number(card.table?.seat) || 1;
    const position = customTable?.seatPositions?.[(seat - 1)
      % customTable.seatPositions.length];
    if (!position) return;
    tile.style.setProperty("--custom-x", `${position.x}%`);
    tile.style.setProperty("--custom-y", `${position.y}%`);
    tile.style.setProperty("--custom-rotation", `${position.rotation}deg`);
  }

  function renderDiscard(surface, folded) {
    let pile = surface.querySelector(".chat-card-discard");
    if (!folded.length) {
      pile?.remove();
      return;
    }
    if (!pile) {
      pile = document.createElement("section");
      pile.className = "chat-card-discard";
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.drive = "cardTable.discard";
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
    pile.querySelectorAll(".chat-card.folded").forEach((card) => card.remove());
    for (const card of folded.slice(0, 12)) {
      pile.appendChild(cardTile(card, { folded: true }));
    }
  }

  function renderCards() {
    const surface = document.querySelector(".chat-card-surface");
    if (!surface) return;
    surface.querySelectorAll(":scope > .chat-card").forEach((tile) => tile.remove());
    surface.querySelector(".chat-card-overflow")?.remove();
    const active = SCRIPT_STATE.cards.filter((card) => card.status !== "folded");
    const folded = SCRIPT_STATE.cards.filter((card) => card.status === "folded");
    const custom = SCRIPT_STATE.context?.state?.cardTable;
    for (const card of active.slice(0, 12)) {
      const tile = cardTile(card);
      if (SCRIPT_STATE.context.aprilFools.table === "custom") {
        applyCustomPosition(tile, card, custom);
      }
      surface.appendChild(tile);
    }
    if (active.length > 12) {
      const overflow = document.createElement("div");
      overflow.className = "chat-card-overflow";
      overflow.textContent = `+${active.length - 12} cards in the pile`;
      surface.appendChild(overflow);
    }
    renderDiscard(surface, folded);
  }

  function applyTheme() {
    const herd = document.getElementById("surgeon-herd");
    const surface = herd?.querySelector(".chat-card-surface");
    if (!herd || !surface) return;
    for (const name of ["poker", "yugioh", "pokemon", "mtg", "uno", "custom"]) {
      herd.classList.remove(`card-theme-${name}`);
    }
    const table = SCRIPT_STATE.context.aprilFools.table || "poker";
    herd.classList.add("chat-card-table", `card-theme-${table}`);
    herd.dataset.cardTable = table;
    const custom = SCRIPT_STATE.context.state.cardTable;
    if (table === "custom" && custom) {
      surface.style.setProperty("--table-felt", custom.feltColor);
      surface.style.setProperty("--card-width", `${custom.cardSize.width}px`);
      surface.style.setProperty("--card-height", `${custom.cardSize.height}px`);
      surface.dataset.faceDownRule = custom.faceDownRule;
      surface.dataset.dealPattern = custom.dealPattern;
    } else {
      surface.style.removeProperty("--table-felt");
      surface.style.removeProperty("--card-width");
      surface.style.removeProperty("--card-height");
      delete surface.dataset.faceDownRule;
      delete surface.dataset.dealPattern;
    }
    const theme = document.querySelector(".chat-card-theme");
    if (theme) theme.value = table;
    document.querySelector(".chat-card-load-custom")
      ?.toggleAttribute("hidden", table !== "custom");
  }

  async function changeTheme(value) {
    if (value === "custom") {
      const loaded = await SCRIPT_STATE.context.api.cardsLoadCustomTable();
      if (loaded.canceled) {
        document.querySelector(".chat-card-theme").value =
          SCRIPT_STATE.context.aprilFools.table;
      }
      return;
    }
    await SCRIPT_STATE.context.api.setAprilFools({ table: value });
  }

  function randomIndex(length) {
    if (length < 1) return -1;
    const values = new Uint32Array(1);
    crypto.getRandomValues(values);
    return values[0] % length;
  }

  async function runDeal(action) {
    const surface = document.querySelector(".chat-card-surface");
    if (!surface || !action) return;
    surface.classList.remove("deal-riffle", "deal-fan", "deal-seats", "deal-draw");
    void surface.offsetWidth;
    surface.classList.add(`deal-${action === "deal-to-seats" ? "seats" : action}`);
    if (action === "draw-one") {
      const candidates = SCRIPT_STATE.cards.filter((card) => (
        card.status === "parked" || card.status === "racing"
      ));
      const index = randomIndex(candidates.length);
      if (index < 0) throw new Error("There is no parked card to draw.");
      await new Promise((resolve) => addTimer(resolve, 320));
      await wakeCard(candidates[index].id);
    }
  }

  function ensureControls(herd, surface) {
    let controls = herd.querySelector(".chat-card-controls");
    if (controls) return controls;
    controls = document.createElement("div");
    controls.className = "chat-card-controls";
    controls.dataset.drive = "cardTable.controls";
    const label = document.createElement("strong");
    label.textContent = "April Fools card table";
    const theme = document.createElement("select");
    theme.className = "chat-card-theme";
    theme.dataset.drive = "cardTable.theme";
    theme.setAttribute("aria-label", "Card table theme");
    const labels = {
      poker: "Poker felt",
      yugioh: "Duel zones",
      pokemon: "Active bench",
      mtg: "Battlefield",
      uno: "Color hand",
      custom: "Custom local JSON",
    };
    for (const [value, text] of Object.entries(labels)) {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = text;
      theme.appendChild(option);
    }
    theme.addEventListener("change", () => {
      void changeTheme(theme.value).catch(showError);
    });
    const load = document.createElement("button");
    load.type = "button";
    load.className = "chat-card-load-custom";
    load.dataset.drive = "cardTable.loadCustom";
    load.textContent = "Load table…";
    load.addEventListener("click", () => {
      void SCRIPT_STATE.context.api.cardsLoadCustomTable().catch(showError);
    });
    const deal = document.createElement("select");
    deal.dataset.drive = "cardTable.deal";
    deal.setAttribute("aria-label", "Deal cards");
    for (const [value, text] of [
      ["", "Deal…"],
      ["riffle", "Riffle"],
      ["fan", "Fan"],
      ["deal-to-seats", "Deal to seats"],
      ["draw-one", "Draw one"],
    ]) {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = text;
      deal.appendChild(option);
    }
    deal.addEventListener("change", () => {
      const action = deal.value;
      deal.value = "";
      void runDeal(action).catch(showError);
    });
    controls.append(label, theme, load, deal);
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
    grab.innerHTML = "<span aria-hidden=\"true\">♠</span> Park chat";
    grab.addEventListener("click", () => void parkCurrent().catch(showError));
    grab.addEventListener("dragstart", (event) => {
      event.dataTransfer.effectAllowed = "move";
      event.dataTransfer.setData("application/x-rapp-brainstem-chat", "park");
    });
    document.querySelector("main")?.appendChild(grab);
    return grab;
  }

  function ensureSurface(herd, grid) {
    let surface = herd.querySelector(".chat-card-surface");
    if (!surface) {
      surface = document.createElement("section");
      surface.className = "chat-card-surface";
      surface.dataset.drive = "cardTable.surface";
      surface.setAttribute("aria-label", "Parked Brainstem chat cards");
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
      if (event.dataTransfer.types.includes("application/x-rapp-chat-card")) {
        event.preventDefault();
        event.dataTransfer.dropEffect = "move";
      }
    }, { signal });
    main?.addEventListener("drop", (event) => {
      const id = event.dataTransfer.getData("application/x-rapp-chat-card");
      if (!id) return;
      event.preventDefault();
      void wakeCard(id).catch(showError);
    }, { signal });
  }

  function receiveFrameMessage(event) {
    if (event.source !== SCRIPT_STATE.context?.frame?.contentWindow) return;
    if (event.data?.type === "rapp-beta:card-capture-result") {
      const waiter = SCRIPT_STATE.captureWaiters.get(event.data.requestId);
      if (!waiter) return;
      SCRIPT_STATE.captureWaiters.delete(event.data.requestId);
      if (event.data.ok) waiter.resolve(event.data.card);
      else waiter.reject(new Error(event.data.error || "Chat capture failed."));
      return;
    }
    if (event.data?.type === "rapp-beta:card-pending-complete") {
      void SCRIPT_STATE.context.api.cardsComplete(
        event.data.id,
        event.data.completion,
      ).then(refreshCards).catch(showError);
    }
  }

  async function refreshCards() {
    if (!SCRIPT_STATE.enabled) return [];
    const sequence = ++SCRIPT_STATE.refreshSequence;
    const cards = await SCRIPT_STATE.context.api.cardsList();
    if (!SCRIPT_STATE.enabled || sequence !== SCRIPT_STATE.refreshSequence) {
      return cards;
    }
    SCRIPT_STATE.cards = cards;
    renderCards();
    return cards;
  }

  async function enable(context) {
    SCRIPT_STATE.context = context;
    if (SCRIPT_STATE.enabled) {
      applyTheme();
      await refreshCards();
      return;
    }
    SCRIPT_STATE.enabled = true;
    SCRIPT_STATE.controller = new AbortController();
    SCRIPT_STATE.openedHerd = document.body.classList.contains(
      "surgeon-herd-open",
    );
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
    applyTheme();
    await refreshCards();
  }

  function disable() {
    if (!SCRIPT_STATE.enabled) return;
    SCRIPT_STATE.enabled = false;
    SCRIPT_STATE.refreshSequence += 1;
    SCRIPT_STATE.controller?.abort();
    SCRIPT_STATE.controller = null;
    for (const timer of SCRIPT_STATE.timers) clearTimeout(timer);
    SCRIPT_STATE.timers.clear();
    for (const waiter of SCRIPT_STATE.captureWaiters.values()) {
      waiter.reject(new Error("April Fools card table was turned off."));
    }
    SCRIPT_STATE.captureWaiters.clear();
    document.getElementById("brainstem-chat-grab")?.remove();
    document.querySelector(".chat-card-controls")?.remove();
    document.querySelector(".chat-card-surface")?.remove();
    document.querySelector(".chat-card-toast")?.remove();
    const herd = document.getElementById("surgeon-herd");
    if (herd) {
      herd.className = herd.className
        .split(/\s+/)
        .filter((name) => !name.startsWith("card-theme-")
          && name !== "chat-card-table")
        .join(" ");
      delete herd.dataset.cardTable;
    }
    removeStyles();
    if (!SCRIPT_STATE.openedHerd) SCRIPT_STATE.context?.exitHerd();
    SCRIPT_STATE.cards = [];
    SCRIPT_STATE.context = null;
    SCRIPT_STATE.primaryId = null;
  }

  root.RappChatCards = Object.freeze({
    disable,
    enabled: () => SCRIPT_STATE.enabled,
    parkCurrent,
    refresh: refreshCards,
    sync: enable,
  });
})(globalThis);
