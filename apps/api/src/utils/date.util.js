function addHours(hours) {
  return new Date(Date.now() + hours * 3600 * 1000);
}

function addDays(days) {
  return new Date(Date.now() + days * 24 * 3600 * 1000);
}

function isExpired(date) {
  return new Date(date) < new Date();
}

function isFuture(date) {
  return new Date(date) > new Date();
}

function isAfter(dateA, dateB) {
  return new Date(dateA) > new Date(dateB);
}

function diffInDays(dateA, dateB) {
  const ms = new Date(dateA) - new Date(dateB);
  return Math.floor(ms / (1000 * 60 * 60 * 24));
}

function formatDate(date) {
  return new Date(date).toLocaleDateString("fr-FR");
}

module.exports = {
  addHours,
  addDays,
  isExpired,
  isFuture,
  isAfter,
  diffInDays,
  formatDate,
};
