import GithubSlugger from 'github-slugger';

const HEADING_RE = /^#{1,6}\s+(.+)$/gm;

export interface HeadingInfo {
  text: string;
  slug: string;
}

/**
 * Strip inline markdown syntax to get plain text, matching how rehype-slug
 * sees heading content after HTML rendering.
 */
function stripInlineMarkdown(text: string): string {
  return (
    text
      // images: ![alt](url) → alt
      .replace(/!\[([^\]]*)\]\([^)]*\)/g, '$1')
      // links: [text](url) → text
      .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')
      // bold/italic: ***text***, **text**, *text*, ___text___, __text__, _text_
      .replace(/\*{1,3}([^*]+)\*{1,3}/g, '$1')
      .replace(/_{1,3}([^_]+)_{1,3}/g, '$1')
      // strikethrough: ~~text~~
      .replace(/~~([^~]+)~~/g, '$1')
      // inline code: `text`
      .replace(/`([^`]+)`/g, '$1')
  );
}

export function extractHeadings(content: string): HeadingInfo[] {
  const slugger = new GithubSlugger();
  const headings: HeadingInfo[] = [];
  let match: RegExpExecArray | null;
  while ((match = HEADING_RE.exec(content)) !== null) {
    const rawText = match[1].trim();
    const plainText = stripInlineMarkdown(rawText);
    const slug = slugger.slug(plainText);
    if (slug) {
      headings.push({ text: plainText, slug });
    }
  }
  return headings;
}
