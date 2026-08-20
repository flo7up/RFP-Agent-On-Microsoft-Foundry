const elements = {
  agent: document.querySelector("#agent"),
  agentSpeech: document.querySelector("#agentSpeech"),
  connectionState: document.querySelector("#connectionState"),
  currentActivity: document.querySelector("#currentActivity"),
  currentActivityArea: document.querySelector("#currentActivityArea"),
  currentActivityTitle: document.querySelector("#currentActivityTitle"),
  downloadDocument: document.querySelector("#downloadDocument"),
  eventCount: document.querySelector("#eventCount"),
  eventLog: document.querySelector("#eventLog"),
  handoverDoc: document.querySelector("#handoverDoc"),
  journeyTrail: document.querySelector("#journeyTrail"),
  office: document.querySelector("#office"),
  opportunityInput: document.querySelector("#opportunityInput"),
  planMeter: document.querySelector(".plan-meter"),
  planMeterFill: document.querySelector("#planMeterFill"),
  planProgress: document.querySelector("#planProgress"),
  printedDocument: document.querySelector("#printedDocument"),
  printedFileName: document.querySelector("#printedFileName"),
  reviewerBubble: document.querySelector("#reviewerBubble"),
  routePath: document.querySelector("#routePath"),
  runButton: document.querySelector("#runButton"),
  runForm: document.querySelector("#runForm"),
  themeToggle: document.querySelector("#themeToggle"),
  todoList: document.querySelector("#todoList"),
  visitor: document.querySelector("#visitor"),
  visitorBubble: document.querySelector("#visitorBubble"),
};

const locations = {
  bed: { x: 186, y: 258 },
  entrance: { x: 48, y: 272 },
  briefing_area: { x: 55, y: 240 },
  planning_desk: { x: 103, y: 137 },
  writing_desk: { x: 153, y: 137 },
  opportunity_shelf: { x: 274, y: 68 },
  proposal_shelf: { x: 274, y: 126 },
  neighbor_house: { x: 292, y: 210 },
  printer: { x: 315, y: 268 },
};

const stationLabels = {
  briefing_area: "Brief",
  entrance: "Door",
  planning_desk: "Plan",
  writing_desk: "Draft",
  opportunity_shelf: "Search",
  proposal_shelf: "Evidence",
  neighbor_house: "Review",
  printer: "Publish",
};
const processedSequences = new Set();
const visualQueue = [];
let activeSource = null;
let currentLocation = "bed";
let currentRunId = null;
let eventTotal = 0;
let isAnimating = false;
let journeyStops = [];
let todos = [];

function setThemeIconLabel() {
  const theme = document.documentElement.dataset.theme;
  elements.themeToggle.setAttribute("aria-label", `Switch to ${theme === "dark" ? "light" : "dark"} theme`);
}

elements.themeToggle.addEventListener("click", () => {
  document.documentElement.dataset.theme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  setThemeIconLabel();
});

setThemeIconLabel();

function setConnection(label, state = "ready") {
  elements.connectionState.className = "connection-state";
  if (state === "running") elements.connectionState.classList.add("is-running");
  if (state === "error") elements.connectionState.classList.add("is-error");
  elements.connectionState.lastChild.textContent = label;
}

function updateJourney(event) {
  if (!(event.location in locations)) return;
  const previous = journeyStops.at(-1);
  if (previous?.location === event.location) return;

  const visit = journeyStops.filter((stop) => stop.location === event.location).length + 1;
  journeyStops.push({ location: event.location, visit });
  elements.journeyTrail.querySelector(".journey-empty")?.remove();
  elements.journeyTrail.querySelector(".is-current")?.classList.remove("is-current");

  if (journeyStops.length > 1) {
    const link = document.createElement("i");
    link.className = "journey-link";
    link.setAttribute("aria-hidden", "true");
    elements.journeyTrail.append(link);
  }

  const stop = document.createElement("div");
  stop.className = "journey-stop is-current";
  stop.title = event.title;
  const number = document.createElement("span");
  number.textContent = String(journeyStops.length);
  const label = document.createElement("strong");
  label.textContent = stationLabels[event.location];
  stop.append(number, label);
  if (visit > 1) {
    const returnLabel = document.createElement("em");
    returnLabel.textContent = `return ${visit}`;
    stop.append(returnLabel);
  }
  elements.journeyTrail.append(stop);
  elements.journeyTrail.scrollLeft = elements.journeyTrail.scrollWidth;
}

function setSpeech(message) {
  elements.agentSpeech.textContent = message;
  elements.agentSpeech.classList.remove("is-updated");
  requestAnimationFrame(() => elements.agentSpeech.classList.add("is-updated"));
}

const poseClasses = ["pose-reading", "pose-planning", "pose-typing", "pose-reaching", "pose-printing"];
const facingClasses = ["facing-left", "facing-right", "facing-up", "facing-down"];

function clearPose() {
  elements.agent.classList.remove(...poseClasses);
}

function setFacing(from, to) {
  elements.agent.classList.remove(...facingClasses);
  const deltaX = to.x - from.x;
  const deltaY = to.y - from.y;
  if (Math.abs(deltaX) >= Math.abs(deltaY)) {
    elements.agent.classList.add(deltaX < 0 ? "facing-left" : "facing-right");
  } else {
    elements.agent.classList.add(deltaY < 0 ? "facing-up" : "facing-down");
  }
}

function setStationPose(locationName) {
  clearPose();
  elements.agent.classList.remove(...facingClasses);
  const poseByLocation = {
    briefing_area: "pose-reading",
    planning_desk: "pose-planning",
    writing_desk: "pose-typing",
    opportunity_shelf: "pose-reaching",
    proposal_shelf: "pose-reaching",
    neighbor_house: "pose-reading",
    printer: "pose-printing",
  };
  const facingByLocation = {
    briefing_area: "facing-down",
    entrance: "facing-right",
    planning_desk: "facing-up",
    writing_desk: "facing-up",
    opportunity_shelf: "facing-right",
    proposal_shelf: "facing-right",
    neighbor_house: "facing-right",
    printer: "facing-right",
  };
  const facing = facingByLocation[locationName];
  const pose = poseByLocation[locationName];
  if (facing) elements.agent.classList.add(facing);
  if (pose) elements.agent.classList.add(pose);
}

function enterSleep() {
  currentLocation = "bed";
  elements.office.dataset.active = "idle";
  elements.agent.classList.remove("is-waking", "is-stretching", "is-walking");
  elements.agent.classList.remove(...facingClasses);
  clearPose();
  elements.agent.classList.add("is-sleeping");
  elements.agent.classList.remove("speech-left", "speech-right", "speech-below");
  elements.agent.setAttribute("aria-label", "Sleeping opportunity proposal agent");
  setSpeech("Z z z...");
}

async function wakeAgent() {
  if (!elements.agent.classList.contains("is-sleeping")) return;
  elements.agent.classList.remove("is-sleeping");
  elements.agent.classList.add("is-waking");
  elements.agent.setAttribute("aria-label", "Waking opportunity proposal agent");
  setSpeech("Huh? A new brief?");
  await new Promise((resolve) => window.setTimeout(resolve, 420));
  elements.agent.classList.remove("is-waking");
  elements.agent.classList.add("is-stretching");
  setSpeech("Stretch first. Architecture second.");
  await new Promise((resolve) => window.setTimeout(resolve, 850));
  elements.agent.classList.remove("is-stretching");
  elements.agent.setAttribute("aria-label", "Opportunity proposal agent");
}

const wait = (ms) =>
  new Promise((resolve) =>
    window.setTimeout(resolve, window.matchMedia("(prefers-reduced-motion: reduce)").matches ? 20 : ms),
  );

async function doorbellHandover() {
  elements.office.classList.add("is-ringing");
  elements.visitor.classList.add("is-present");
  elements.visitorBubble.textContent = "Ding dong!";
  await wait(1000);
  await wakeAgent();
  await moveAgent("entrance");
  elements.office.classList.remove("is-ringing");
  elements.visitorBubble.textContent = "A new opportunity for you.";
  await wait(450);
  elements.handoverDoc.classList.add("is-passing");
  await wait(900);
  elements.handoverDoc.classList.remove("is-passing");
  setSpeech("Thank you. Let me take a look.");
  await wait(650);
  elements.visitorBubble.textContent = "";
  elements.visitor.classList.remove("is-present");
}

function pointsToLobby(locationName) {
  const location = locations[locationName] || locations.briefing_area;
  const lowerHub = { x: 176, y: 240 };
  const upperDoor = { x: 176, y: 145 };
  const paths = {
    bed: [location, { x: 186, y: 240 }, lowerHub],
    entrance: [location, { x: 48, y: 240 }, lowerHub],
    briefing_area: [location, lowerHub],
    planning_desk: [location, { x: 103, y: 145 }, upperDoor, lowerHub],
    writing_desk: [location, { x: 153, y: 145 }, upperDoor, lowerHub],
    opportunity_shelf: [location, { x: 205, y: 68 }, { x: 205, y: 145 }, upperDoor, lowerHub],
    proposal_shelf: [location, { x: 205, y: 126 }, { x: 205, y: 145 }, upperDoor, lowerHub],
    neighbor_house: [location, { x: 282, y: 210 }, { x: 282, y: 240 }, lowerHub],
    printer: [location, { x: 282, y: 268 }, { x: 282, y: 240 }, lowerHub],
  };
  return paths[locationName] || [location, lowerHub];
}

function samePoint(left, right) {
  return left.x === right.x && left.y === right.y;
}

function routePoints(originName, destinationName) {
  const originPath = pointsToLobby(originName);
  const destinationPath = pointsToLobby(destinationName);
  let originIndex = originPath.length - 1;
  let destinationIndex = destinationPath.length - 1;
  while (
    originIndex >= 0 &&
    destinationIndex >= 0 &&
    samePoint(originPath[originIndex], destinationPath[destinationIndex])
  ) {
    originIndex -= 1;
    destinationIndex -= 1;
  }
  const points = [
    ...originPath.slice(0, originIndex + 2),
    ...destinationPath.slice(0, destinationIndex + 1).reverse(),
  ];
  return points.filter(
    (point, index, values) => index === 0 || !samePoint(point, values[index - 1]),
  );
}

async function moveSegment(origin, destination) {
  setFacing(origin, destination);
  const distance = Math.hypot(destination.x - origin.x, destination.y - origin.y);
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const duration = reducedMotion ? 20 : Math.max(260, Math.min(720, distance * 4));
  elements.agent.style.setProperty("--walk-duration", `${duration}ms`);
  elements.agent.style.setProperty("--agent-x", `${destination.x / 4}%`);
  elements.agent.style.setProperty("--agent-y", `${destination.y / 3}%`);
  await new Promise((resolve) => window.setTimeout(resolve, duration + 20));
}

async function moveAgent(locationName) {
  const destination = locations[locationName] || locations.briefing_area;
  const resolvedLocation = locationName in locations ? locationName : "briefing_area";
  const points = routePoints(currentLocation, resolvedLocation);
  clearPose();
  elements.office.dataset.active = resolvedLocation;
  elements.routePath.setAttribute(
    "d",
    points.map((point, index) => `${index === 0 ? "M" : "L"}${point.x} ${point.y}`).join(" "),
  );
  elements.routePath.classList.add("is-visible");
  elements.agent.classList.add("is-walking");
  elements.agent.classList.toggle("speech-left", destination.x < 100);
  elements.agent.classList.toggle("speech-right", destination.x > 285);
  elements.agent.classList.toggle("speech-below", destination.y < 90);
  for (let index = 1; index < points.length; index += 1) {
    await moveSegment(points[index - 1], points[index]);
  }
  currentLocation = resolvedLocation;
  elements.agent.classList.remove("is-walking");
  elements.routePath.classList.remove("is-visible");
  setStationPose(resolvedLocation);
}

function eventTime(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? ""
    : date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function activityCategory(event) {
  if (event.kind.startsWith("plan.")) return "Plan";
  if (event.kind.startsWith("research.opportunities")) return "Search";
  if (event.kind.startsWith("research.proposals")) return "Evidence";
  if (event.kind.startsWith("review.")) return "Review";
  if (event.kind.startsWith("document.compos") || event.kind === "document.drafting" || event.kind === "document.revision_requested") return "Draft";
  if (event.kind.startsWith("document.")) return "Publish";
  return "Run";
}

function updateCurrentActivity(event) {
  const isError = event.status === "error" || event.kind.endsWith(".failed");
  const isComplete = event.kind === "agent.completed";
  elements.currentActivity.dataset.state = isError ? "error" : isComplete ? "complete" : "active";
  elements.currentActivityArea.textContent = activityCategory(event);
  elements.currentActivityTitle.textContent = event.title;
}

function addTimelineEvent(event) {
  elements.eventLog.querySelector(".timeline-empty")?.remove();
  const item = document.createElement("details");
  const statusClass = event.status === "error" ? "error" : event.status === "completed" ? "completed" : "active";
  item.className = `event-item is-${statusClass}`;

  const summary = document.createElement("summary");
  const meta = document.createElement("div");
  meta.className = "event-meta";
  const heading = document.createElement("span");
  heading.className = "event-heading";
  const category = document.createElement("small");
  category.className = "event-category";
  category.textContent = activityCategory(event);
  const title = document.createElement("strong");
  title.textContent = event.title;
  heading.append(category, title);
  const time = document.createElement("time");
  time.dateTime = event.occurred_at;
  time.textContent = eventTime(event.occurred_at);
  meta.append(heading, time);

  const message = document.createElement("p");
  message.className = "event-message";
  message.textContent = event.message;
  summary.append(meta, message);
  item.append(summary);

  if (event.data && Object.keys(event.data).length > 0) {
    const data = document.createElement("pre");
    data.className = "event-data";
    data.textContent = JSON.stringify(event.data, null, 2);
    item.append(data);
  }
  elements.eventLog.append(item);
  elements.eventLog.scrollTop = elements.eventLog.scrollHeight;
  eventTotal += 1;
  elements.eventCount.textContent = `${eventTotal} ${eventTotal === 1 ? "event" : "events"}`;
}

function normalizeTodos(values) {
  if (!Array.isArray(values)) return [];
  return values.map((value, index) => {
    if (typeof value === "string") {
      return { id: index + 1, title: value, description: "", is_complete: false, reason: "" };
    }
    return {
      id: Number(value.id ?? index + 1),
      title: String(value.title ?? `Task ${index + 1}`),
      description: String(value.description ?? ""),
      is_complete: Boolean(value.is_complete),
      reason: String(value.reason ?? ""),
    };
  });
}

function mergeCreatedTodos(values) {
  const created = normalizeTodos(values);
  todos = todos.filter((todo) => !todo.pending);
  created.forEach((todo) => {
    const existingIndex = todos.findIndex((existing) => existing.id === todo.id);
    if (existingIndex >= 0) {
      todos[existingIndex] = todo;
    } else {
      todos.push(todo);
    }
  });
}

function renderTodos() {
  elements.todoList.replaceChildren();
  if (!todos.length) {
    const empty = document.createElement("li");
    empty.className = "empty-state";
    empty.textContent = "Waiting for the Harness plan.";
    elements.todoList.append(empty);
    elements.planProgress.textContent = "0 / 0";
    elements.planMeter.setAttribute("aria-valuemax", "0");
    elements.planMeter.setAttribute("aria-valuenow", "0");
    elements.planMeterFill.style.width = "0%";
    return;
  }
  todos.forEach((todo, index) => {
    const item = document.createElement("li");
    item.className = "todo-row";
    item.classList.toggle("is-complete", todo.is_complete);
    item.classList.toggle("is-pending", Boolean(todo.pending));
    const status = document.createElement("span");
    status.className = "todo-status";
    status.textContent = todo.is_complete ? "✓" : todo.pending ? "+" : String(index + 1);
    status.setAttribute("aria-hidden", "true");
    const copy = document.createElement("span");
    copy.className = "todo-copy";
    const title = document.createElement("strong");
    title.textContent = todo.title;
    copy.append(title);
    const detailText = todo.is_complete && todo.reason ? todo.reason : todo.description;
    if (detailText) {
      const detail = document.createElement("span");
      detail.className = "todo-detail";
      detail.textContent = detailText;
      copy.append(detail);
      item.title = detailText;
    }
    const state = document.createElement("span");
    state.className = "todo-state";
    state.textContent = todo.is_complete ? "Done" : todo.pending ? "Adding" : "Queued";
    item.append(status, copy, state);
    elements.todoList.append(item);
  });
  const completed = todos.filter((todo) => todo.is_complete).length;
  elements.planProgress.textContent = `${completed} / ${todos.length}`;
  elements.planMeter.setAttribute("aria-valuemax", String(todos.length));
  elements.planMeter.setAttribute("aria-valuenow", String(completed));
  elements.planMeterFill.style.width = `${(completed / todos.length) * 100}%`;
}

function updateTodos(event) {
  if (event.kind === "plan.started" && Array.isArray(event.data?.todos)) {
    todos = todos.filter((todo) => !todo.pending);
    event.data.todos.forEach((title, index) => {
      todos.push({
        id: `pending-${event.sequence}-${index}`,
        title: String(title),
        is_complete: false,
        pending: true,
      });
    });
  }
  if (event.kind === "plan.completed" && Array.isArray(event.data?.todos)) {
    mergeCreatedTodos(event.data.todos);
  }
  if (event.kind === "plan.failed") {
    todos = todos.filter((todo) => !todo.pending);
  }
  if (event.kind === "plan.updated" && Array.isArray(event.data?.completed_items)) {
    const completedItems = new Map(
      event.data.completed_items.map((item) => [Number(item.id), String(item.reason ?? "")]),
    );
    todos = todos.map((todo) =>
      completedItems.has(todo.id)
        ? { ...todo, is_complete: true, reason: completedItems.get(todo.id) }
        : todo,
    );
  }
  if (event.kind === "plan.removed" && Array.isArray(event.data?.removed_ids)) {
    const ids = new Set(event.data.removed_ids.map((id) => Number(id)));
    todos = todos.filter((todo) => !ids.has(todo.id));
  }
  if (event.kind === "agent.completed" && Array.isArray(event.data?.todos)) {
    const previousTodos = new Map(todos.map((todo) => [todo.id, todo]));
    todos = normalizeTodos(event.data.todos).map((todo) => ({
      ...todo,
      reason: previousTodos.get(todo.id)?.reason || todo.reason,
    }));
  }
  renderTodos();
}

function showPrintedDocument(event) {
  const fileName = event.data?.file_name || "draft-opportunity-proposal.md";
  elements.printedFileName.textContent = fileName;
  elements.downloadDocument.href = `/api/runs/${currentRunId}/document`;
  elements.printedDocument.hidden = false;
  elements.printedDocument.classList.add("is-visible");
}

async function applyVisualEvent(event) {
  if (event.kind === "agent.started") {
    await doorbellHandover();
  }
  await wakeAgent();
  await moveAgent(event.location);
  if (event.kind === "review.started") {
    elements.reviewerBubble.textContent = "Let me sharpen the style.";
  } else if (event.kind === "review.completed") {
    elements.reviewerBubble.textContent = "Style pass complete.";
  } else if (event.kind === "review.failed") {
    elements.reviewerBubble.textContent = "This needs another pass.";
  } else if (event.location !== "neighbor_house") {
    elements.reviewerBubble.textContent = "";
  }
  setSpeech(event.kind.startsWith("review.") ? "" : event.message);
  if (event.kind === "document.published" || event.kind === "agent.completed") {
    showPrintedDocument(event);
  }
  await new Promise((resolve) => window.setTimeout(resolve, event.status === "completed" ? 650 : 350));
  if (event.kind === "agent.completed" || event.kind === "run.failed") {
    await new Promise((resolve) => window.setTimeout(resolve, 900));
    await moveAgent("bed");
    enterSleep();
  }
}

async function drainVisualQueue() {
  if (isAnimating) return;
  isAnimating = true;
  while (visualQueue.length) {
    await applyVisualEvent(visualQueue.shift());
  }
  isAnimating = false;
}

function handleHarnessEvent(event) {
  if (processedSequences.has(event.sequence)) return;
  processedSequences.add(event.sequence);
  addTimelineEvent(event);
  updateCurrentActivity(event);
  updateTodos(event);
  updateJourney(event);
  visualQueue.push(event);
  drainVisualQueue();

  if (event.kind === "review.failed") {
    setConnection("Revising", "running");
  } else if (event.status === "error" || event.kind.endsWith(".failed")) {
    setConnection("Needs attention", "error");
    elements.runButton.disabled = false;
    elements.runButton.querySelector("span").textContent = "Run again";
  } else if (event.kind === "agent.completed") {
    setConnection("Complete");
    elements.runButton.disabled = false;
    elements.runButton.querySelector("span").textContent = "Run again";
  } else {
    setConnection("Running", "running");
  }
}

function resetRun() {
  activeSource?.close();
  activeSource = null;
  currentRunId = null;
  currentLocation = "bed";
  eventTotal = 0;
  journeyStops = [];
  todos = [];
  processedSequences.clear();
  visualQueue.length = 0;
  elements.eventCount.textContent = "0 events";
  elements.currentActivity.dataset.state = "idle";
  elements.currentActivityArea.textContent = "Idle";
  elements.currentActivityTitle.textContent = "Waiting for an opportunity";
  elements.eventLog.replaceChildren();
  const empty = document.createElement("div");
  empty.className = "timeline-empty";
  empty.innerHTML = '<span aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 3v4m0 10v4M3 12h4m10 0h4M5.6 5.6l2.8 2.8m7.2 7.2 2.8 2.8m0-12.8-2.8 2.8m-7.2 7.2-2.8 2.8"/></svg></span><p>Starting run...</p>';
  elements.eventLog.append(empty);
  elements.office.dataset.active = "idle";
  elements.agent.style.setProperty("--agent-x", `${186 / 4}%`);
  elements.agent.style.setProperty("--agent-y", `${258 / 3}%`);
  elements.office.classList.remove("is-ringing");
  elements.visitor.classList.remove("is-present");
  elements.visitorBubble.textContent = "";
  elements.reviewerBubble.textContent = "";
  elements.handoverDoc.classList.remove("is-passing");
  elements.printedDocument.classList.remove("is-visible");
  elements.printedDocument.hidden = true;
  enterSleep();
  renderTodos();
  elements.journeyTrail.replaceChildren();
  const journeyEmpty = document.createElement("span");
  journeyEmpty.className = "journey-empty";
  journeyEmpty.textContent = "Waiting for the Harness route.";
  elements.journeyTrail.append(journeyEmpty);
}

async function startRun(opportunity) {
  resetRun();
  elements.runButton.disabled = true;
  elements.runButton.querySelector("span").textContent = "Agent running";
  setConnection("Connecting", "running");
  const response = await fetch("/api/runs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ opportunity }),
  });
  if (!response.ok) throw new Error(`Unable to start run (${response.status}).`);
  const run = await response.json();
  currentRunId = run.run_id;
  activeSource = new EventSource(run.events_url);
  activeSource.addEventListener("harness", (message) => handleHarnessEvent(JSON.parse(message.data)));
  activeSource.addEventListener("stream-end", () => {
    activeSource.close();
    activeSource = null;
    if (elements.runButton.disabled) {
      elements.runButton.disabled = false;
      elements.runButton.querySelector("span").textContent = "Run again";
    }
  });
  activeSource.onerror = () => {
    if (!activeSource) return;
    setConnection("Reconnecting", "running");
  };
}

elements.runForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const opportunity = elements.opportunityInput.value.trim();
  if (!opportunity) return;
  try {
    await startRun(opportunity);
  } catch (error) {
    setConnection("Unavailable", "error");
    setSpeech(error instanceof Error ? error.message : "Unable to start the run.");
    elements.runButton.disabled = false;
    elements.runButton.querySelector("span").textContent = "Try again";
  }
});

fetch("/api/config")
  .then((response) => response.json())
  .then((config) => {
    elements.opportunityInput.value = config.default_opportunity || "";
  })
  .catch(() => {
    setConnection("Configuration unavailable", "error");
  });

renderTodos();

export { handleHarnessEvent, resetRun };