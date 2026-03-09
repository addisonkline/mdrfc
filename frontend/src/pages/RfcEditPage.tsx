import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import MDEditor from '@uiw/react-md-editor';
import { FormField } from '../components/forms/FormField';
import { SubmitButton } from '../components/forms/SubmitButton';
import { getRfc, updateRfc } from '../api/rfcs';
import {
  validateRfcTitle,
  validateRfcSlug,
  validateRfcSummary,
  validateRfcContent,
} from '../validation';
import type { UpdateRfcData } from '../types';

export function RfcEditPage() {
  const { id } = useParams<{ id: string }>();
  const rfcId = Number(id);
  const navigate = useNavigate();

  const [original, setOriginal] = useState<{
    title: string;
    slug: string;
    status: 'draft' | 'open';
    summary: string;
    content: string;
  } | null>(null);
  const [title, setTitle] = useState('');
  const [slug, setSlug] = useState('');
  const [status, setStatus] = useState<'draft' | 'open'>('draft');
  const [summary, setSummary] = useState('');
  const [content, setContent] = useState('');
  const [errors, setErrors] = useState<Record<string, string | null>>({});
  const [serverError, setServerError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);

  useEffect(() => {
    getRfc(rfcId)
      .then((res) => {
        const r = res.rfc;
        const s = r.status === 'draft' || r.status === 'open' ? r.status : 'draft';
        setOriginal({ title: r.title, slug: r.slug, status: s, summary: r.summary, content: r.content });
        setTitle(r.title);
        setSlug(r.slug);
        setStatus(s);
        setSummary(r.summary);
        setContent(r.content);
      })
      .catch((err) => setServerError(err.message))
      .finally(() => setFetching(false));
  }, [rfcId]);

  function validate(): boolean {
    const e = {
      title: validateRfcTitle(title),
      slug: validateRfcSlug(slug),
      summary: validateRfcSummary(summary),
      content: validateRfcContent(content),
    };
    setErrors(e);
    return !Object.values(e).some(Boolean);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!validate() || !original) return;
    setLoading(true);
    setServerError(null);

    const patch: UpdateRfcData = {};
    if (title !== original.title) patch.title = title;
    if (slug !== original.slug) patch.slug = slug;
    if (status !== original.status) patch.status = status;
    if (summary !== original.summary) patch.summary = summary;
    if (content !== original.content) patch.content = content;

    if (Object.keys(patch).length === 0) {
      navigate(`/rfc/${rfcId}`);
      return;
    }

    try {
      await updateRfc(rfcId, patch);
      navigate(`/rfc/${rfcId}`);
    } catch (err) {
      setServerError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  if (fetching) return <p className="text-gray-500">Loading...</p>;

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="mb-6 text-2xl font-bold">Edit RFC</h1>
      <form onSubmit={handleSubmit}>
        <FormField label="Title" error={errors.title}>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            onBlur={() => setErrors((p) => ({ ...p, title: validateRfcTitle(title) }))}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
        </FormField>

        <FormField label="Slug" error={errors.slug}>
          <input
            value={slug}
            onChange={(e) => setSlug(e.target.value)}
            onBlur={() => setErrors((p) => ({ ...p, slug: validateRfcSlug(slug) }))}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
        </FormField>

        <FormField label="Status" error={null}>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value as 'draft' | 'open')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          >
            <option value="draft">Draft</option>
            <option value="open">Open</option>
          </select>
        </FormField>

        <FormField label="Summary" error={errors.summary}>
          <textarea
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            onBlur={() => setErrors((p) => ({ ...p, summary: validateRfcSummary(summary) }))}
            rows={2}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
        </FormField>

        <FormField label="Content" error={errors.content}>
          <div data-color-mode="light">
            <MDEditor
              value={content}
              onChange={(val) => setContent(val ?? '')}
              height={400}
            />
          </div>
        </FormField>

        {serverError && <p className="mb-4 text-sm text-red-600">{serverError}</p>}
        <SubmitButton loading={loading}>Save Changes</SubmitButton>
      </form>
    </div>
  );
}
