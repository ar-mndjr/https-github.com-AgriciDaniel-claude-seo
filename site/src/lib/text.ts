/** Escape text for HTML, then turn **bold** into <strong>. Used where the CMS
 *  stores a short piece of text that may contain simple emphasis. */
export function inline(s: string = ''): string {
  const esc = s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  return esc.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
}

/** Map a tone name chosen in the CMS to the CSS classes used by the design. */
export const tileClass = (tone?: string) => `t-${tone || 'indigo'}`;
