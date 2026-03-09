import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import MDEditor from '@uiw/react-md-editor';
import { FormField } from '../components/forms/FormField';
import { SubmitButton } from '../components/forms/SubmitButton';
import { createRfc } from '../api/rfcs';
import {
  validateRfcTitle,
  validateRfcSlug,
  validateRfcSummary,
  validateRfcContent,
} from '../validation';

export function RfcCreatePage() {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [slug, setSlug] = useState('');
  const [status, setStatus] = useState<'draft' | 'open'>('draft');
  const [summary, setSummary] = useState('');
  const [content, setContent] = useState('');
  const [errors, setErrors] = useState<Record<string, string | null>>({});
  const [serverError, setServerError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

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
    if (!validate()) return;
    setLoading(true);
    setServerError(null);
    try {
      const result = await createRfc({ title, slug, status, summary, content });
      navigate(`/rfc/${result.rfc_id}`);
    } catch (err) {
      setServerError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="mb-6 text-2xl font-bold">Create RFC</h1>
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
        <SubmitButton loading={loading}>Create RFC</SubmitButton>
      </form>
    </div>
  );
}
