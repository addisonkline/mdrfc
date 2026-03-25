const HEADING_RE = /^#{1,6}\s+(.+)$/gm;

export interface HeadingInfo {
  text: string;
  slug: string;
}

function slugifyHeading(text: string): string {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

export function extractHeadings(content: string): HeadingInfo[] {
  const headings: HeadingInfo[] = [];
  let match: RegExpExecArray | null;
  while ((match = HEADING_RE.exec(content)) !== null) {
    const text = match[1].trim();
    const slug = slugifyHeading(text);
    if (slug) {
      headings.push({ text, slug });
    }
  }
  return headings;
}
