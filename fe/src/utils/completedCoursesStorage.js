const STORAGE_KEY = 'completedCourseIds';

function parseStoredIds() {
  try {
    const raw = window.localStorage?.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.map((v) => Number(v)).filter(Number.isFinite);
  } catch (e) {
    return [];
  }
}

function persistIds(ids) {
  try {
    const unique = Array.from(new Set(ids.map((v) => Number(v)).filter(Number.isFinite)));
    window.localStorage?.setItem(STORAGE_KEY, JSON.stringify(unique));
  } catch (e) {
    // ignore
  }
}

export function getCompletedCourseIds() {
  return new Set(parseStoredIds());
}

export function addCompletedCourseId(courseId) {
  if (!courseId) return;
  const ids = parseStoredIds();
  ids.push(Number(courseId));
  persistIds(ids);
  emitCompletedCoursesChanged();
}

export function removeCompletedCourseId(courseId) {
  if (!courseId) return;
  const ids = parseStoredIds().filter((id) => id !== Number(courseId));
  persistIds(ids);
  emitCompletedCoursesChanged();
}

export function emitCompletedCoursesChanged() {
  window.dispatchEvent(new CustomEvent('completedCoursesChanged'));
}

export function listenCompletedCoursesChange(handler) {
  window.addEventListener('completedCoursesChanged', handler);
  return () => window.removeEventListener('completedCoursesChanged', handler);
}
