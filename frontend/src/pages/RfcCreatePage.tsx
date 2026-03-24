import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import MDEditor from '@uiw/react-md-editor';
import { FormField } from '../components/forms/FormField';
import { SubmitButton } from '../components/forms/SubmitButton';
import { createRfc } from '../api/rfcs';
import {
  parseAgentContributors,
  validateAgentContributors,
  validateRfcContent,
  validateRfcSlug,
  validateRfcSummary,
  validateRfcTitle,
} from '../validation';

export function RfcCreatePage() {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [slug, setSlug] = useState('');
  const [status, setStatus] = useState<'draft' | 'open'>('draft');
  const [summary, setSummary] = useState('');
  const [content, setContent] = useState('');
  const [agentContributorsInput, setAgentContributorsInput] = useState('');
  const [isPublic, setIsPublic] = useState(false);
  const [errors, setErrors] = useState<Record<string, string | null>>({});
  const [serverError, setServerError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function validate(): boolean {
    const nextErrors = {
      title: validateRfcTitle(title),
      slug: validateRfcSlug(slug),
      summary: validateRfcSummary(summary),
      content: validateRfcContent(content),
      agent_contributors: validateAgentContributors(agentContributorsInput),
    };
    setErrors(nextErrors);
    return !Object.values(nextErrors).some(Boolean);
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!validate()) return;

    setLoading(true);
    setServerError(null);

    try {
      const result = await createRfc({
        title,
        slug,
        status,
        summary,
        content,
        public: isPublic,
        agent_contributors: parseAgentContributors(agentContributorsInput),
      });
      navigate(`/rfcs/${result.rfc_id}`);
    } catch (err) {
      setServerError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="mb-2 text-2xl font-bold">Create RFC</h1>
      <p className="mb-6 text-sm text-gray-500">
        Draft a new RFC and choose whether it should be visible publicly from the start.
      </p>

      <form onSubmit={handleSubmit}>
        <FormField label="Title" error={errors.title}>
          <input
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            onBlur={() => setErrors((current) => ({ ...current, title: validateRfcTitle(title) }))}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
        </FormField>

        <FormField label="Slug" error={errors.slug}>
          <input
            value={slug}
            onChange={(event) => setSlug(event.target.value)}
            onBlur={() => setErrors((current) => ({ ...current, slug: validateRfcSlug(slug) }))}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
        </FormField>

        <FormField label="Status" error={null}>
          <select
            value={status}
            onChange={(event) => setStatus(event.target.value as 'draft' | 'open')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          >
            <option value="draft">Draft</option>
            <option value="open">Open</option>
          </select>
        </FormField>

        <FormField label="Summary" error={errors.summary}>
          <textarea
            value={summary}
            onChange={(event) => setSummary(event.target.value)}
            onBlur={() =>
              setErrors((current) => ({ ...current, summary: validateRfcSummary(summary) }))
            }
            rows={3}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
        </FormField>

        <FormField label="Agent Contributors" error={errors.agent_contributors}>
          <textarea
            value={agentContributorsInput}
            onChange={(event) => setAgentContributorsInput(event.target.value)}
            onBlur={() =>
              setErrors((current) => ({
                ...current,
                agent_contributors: validateAgentContributors(agentContributorsInput),
              }))
            }
            rows={3}
            placeholder={`codex@openai\ngpt@openai`}
            className="w-full rounded-md border border-gray-300 px-3 py-2 font-mono text-sm focus:border-blue-500 focus:outline-none"
          />
          <p className="mt-1 text-xs text-gray-500">One `agent@host` per line or comma-separated.</p>
        </FormField>

        <div className="mb-4 rounded-md border border-gray-200 bg-gray-50 p-3">
          <label className="flex items-start gap-3 text-sm text-gray-700">
            <input
              type="checkbox"
              checked={isPublic}
              onChange={(event) => setIsPublic(event.target.checked)}
              className="mt-0.5 rounded border-gray-300"
            />
            <span>
              <span className="block font-medium text-gray-900">Make this RFC public</span>
              <span className="block text-gray-500">
                Unchecked RFCs are only visible to authenticated users until a later revision
                changes visibility.
              </span>
            </span>
          </label>
        </div>

        <FormField label="Content" error={errors.content}>
          <div data-color-mode="light">
            <MDEditor value={content} onChange={(value) => setContent(value ?? '')} height={420} />
          </div>
        </FormField>

        {serverError && <p className="mb-4 text-sm text-red-600">{serverError}</p>}
        <SubmitButton loading={loading}>Create RFC</SubmitButton>
      </form>
    </div>
  );
}
