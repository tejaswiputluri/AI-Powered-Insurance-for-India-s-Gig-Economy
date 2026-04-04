/**
 * Formatters — Paise → Rupee display, UTC → IST conversion.
 * RULE-03: All money stored as paise. Display converts to rupees.
 * RULE-04: All timestamps stored UTC. Display converts to IST.
 */

/**
 * Convert paise to formatted rupee string.
 * 6700 → "₹67", 33350 → "₹333.50"
 */
export function formatRupees(paise) {
  if (paise == null) return '₹0';
  const rupees = paise / 100;
  if (rupees === Math.floor(rupees)) {
    return `₹${rupees.toLocaleString('en-IN')}`;
  }
  return `₹${rupees.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
}

/**
 * Convert paise to short formatted string.
 * 220000 → "₹2,200"
 */
export function formatRupeesShort(paise) {
  if (paise == null) return '₹0';
  return `₹${Math.round(paise / 100).toLocaleString('en-IN')}`;
}

/**
 * Convert UTC ISO timestamp to IST display string.
 * "2026-03-23T14:30:00Z" → "23 Mar, 8:00 PM IST"
 */
export function formatIST(utcTimestamp) {
  if (!utcTimestamp) return '';
  const date = new Date(utcTimestamp);
  return date.toLocaleString('en-IN', {
    timeZone: 'Asia/Kolkata',
    day: 'numeric',
    month: 'short',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  }) + ' IST';
}

/**
 * Format a date as "Mon 23 Mar".
 */
export function formatDateShort(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-IN', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
  });
}

/**
 * Get claim status display properties.
 */
export function getStatusDisplay(status) {
  const map = {
    pending_fraud_check: { label: 'Processing', color: 'text-blue-400', bg: 'bg-blue-500/20' },
    fraud_checking: { label: 'Checking', color: 'text-blue-400', bg: 'bg-blue-500/20' },
    approved: { label: 'Approved', color: 'text-green-400', bg: 'bg-green-500/20' },
    flagged: { label: 'Flagged', color: 'text-yellow-400', bg: 'bg-yellow-500/20' },
    on_hold: { label: 'Under Review', color: 'text-orange-400', bg: 'bg-orange-500/20' },
    rejected: { label: 'Rejected', color: 'text-red-400', bg: 'bg-red-500/20' },
    paid: { label: 'Paid ✓', color: 'text-green-400', bg: 'bg-green-500/20' },
  };
  return map[status] || { label: status, color: 'text-gray-400', bg: 'bg-gray-500/20' };
}

/**
 * Format percentage.
 */
export function formatPercent(value) {
  if (value == null) return '0%';
  return `${Math.round(value * 100)}%`;
}
