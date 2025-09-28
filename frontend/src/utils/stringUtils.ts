// Simple fuzzy match utility (Levenshtein distance approximation)
export function fuzzyMatch(needle: string, haystack: string): boolean {
  needle = needle.toLowerCase().trim();
  haystack = haystack.toLowerCase().trim();
  
  if (haystack.includes(needle)) return true;
  
  // Basic Levenshtein distance (simplified)
  const nLen = needle.length;
  const hLen = haystack.length;
  if (nLen > hLen) return false;
  if (nLen === hLen) return needle === haystack;
  
  const matrix = Array.from({ length: nLen + 1 }, () => Array(hLen + 1).fill(0));
  
  for (let i = 0; i <= nLen; i++) matrix[i][0] = i;
  for (let j = 0; j <= hLen; j++) matrix[0][j] = j;
  
  for (let i = 1; i <= nLen; i++) {
    for (let j = 1; j <= hLen; j++) {
      const cost = needle[i - 1] === haystack[j - 1] ? 0 : 1;
      matrix[i][j] = Math.min(
        matrix[i - 1][j] + 1,      // deletion
        matrix[i][j - 1] + 1,      // insertion
        matrix[i - 1][j - 1] + cost // substitution
      );
    }
  }
  
  // Allow distance up to 2 or 20% of length
  return matrix[nLen][hLen] <= Math.max(2, Math.floor(nLen * 0.2));
}