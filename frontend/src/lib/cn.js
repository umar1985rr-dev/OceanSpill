/** Tiny class-name joiner (no tailwind-merge needed for our usage). */
export function cn(...parts) {
  return parts.filter(Boolean).join(" ");
}
