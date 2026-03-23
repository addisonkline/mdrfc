import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import MDEditor from '@uiw/react-md-editor';
import { FormField } from '../components/forms/FormField';
import { SubmitButton } from '../components/forms/SubmitButton';
import { createRfcRevision } from '../api/revisions';
import { getRfc } from '../api/rfcs';
import { useAuth } from '../hooks/useAuth';
import {
  formatAgentContributors,
  parseAgentContributors,
  validateAgentContributors,
  validateRevisionMessage,
  validateRfcContent,
  validateRfcSlug,
  validateRfcSummary,
  validateRfcTitle,
} from '../validation';

interface EditableRfcState {
  title: string;
  slug: string;
  status: 'draft' | 'open';
  summary: string;
  content: string;
  public: boolean;
  agentContributors: string[];
}

function arraysEqual(left: string[], right: string[]): boolean {
  return left.length === right.length && left.every((value, index) => value === right[index]);
}

export function RfcRevisionCreatePage() {
  const { id } = useParams<{ id: string }>();
  const rfcId = Number(id);
  const navigate = useNavigate();
  const { user } = useAuth();

  const [original, setOriginal] = useState<EditableRfcState | null>(null);
  const [title, setTitle] = useState('');
  const [slug, setSlug] = useState('');
  const [status, setStatus] = useState<'draft' | 'open'>('draft');
  const [summary, setSummary] = useState('');
  const [content, setContent] = useState('');
  const [isPublic, setIsPublic] = useState(false);
  const [agentContributorsInput, setAgentContributorsInput] = useState('');
  const [message, setMessage] = useState('');
  const [errors, setErrors] = useState<Record<string, string | null>>({});
  const [serverError, setServerError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [rfcTitle, setRfcTitle] = useState('');

  useEffect(() => {
    getRfc(rfcId)
      .then((response) => {
        const rfc = response.rfc;
        if (user && user.id !== rfc.author_id) {
          throw new Error('Only the RFC author can create revisions.');
        }
        if (rfc.review_requested || rfc.status === 'accepted' || rfc.status === 'rejected') {
          throw new Error('This RFC is no longer open for revisions.');
        }

        const nextStatus = rfc.status === 'draft' || rfc.status === 'open' ? rfc.status : 'draft';
        const currentAgentContributors = rfc.agent_contributions[rfc.current_revision] ?? [];
        const nextState: EditableRfcState = {
          title: rfc.title,
          slug: rfc.slug,
          status: nextStatus,
          summary: rfc.summary,
          content: rfc.content,
          public: rfc.public,
          agentContributors: currentAgentContributors,
        };

        setOriginal(nextState);
        setTitle(nextState.title);
        setSlug(nextState.slug);
        setStatus(nextState.status);
        setSummary(nextState.summary);
        setContent(nextState.content);
        setIsPublic(nextState.public);
        setAgentContributorsInput(formatAgentContributors(nextState.agentContributors));
        setRfcTitle(rfc.title);
      })
      .catch((err) => setServerError(err.message))
      .finally(() => setFetching(false));
  }, [rfcId, user]);

  function validate(): boolean {
    const nextErrors = {
      title: validateRfcTitle(title),
      slug: validateRfcSlug(slug),
      summary: validateRfcSummary(summary),
      content: validateRfcContent(content),
      agent_contributors: validateAgentContributors(agentContributorsInput),
      message: validateRevisionMessage(message),
    };
    setErrors(nextErrors);
    return !Object.values(nextErrors).some(Boolean);
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!validate() || !original) return;

    const nextAgentContributors = parseAgentContributors(agentContributorsInput);
    const update: {
      title?: string;
      slug?: string;
      status?: 'draft' | 'open';
      summary?: string;
      content?: string;
      public?: boolean;
      agent_contributors?: string[];
    } = {};

    if (title !== original.title) update.title = title;
    if (slug !== original.slug) update.slug = slug;
    if (status !== original.status) update.status = status;
    if (summary !== original.summary) update.summary = summary;
    if (content !== original.content) update.content = content;
    if (isPublic !== original.public) update.public = isPublic;
    if (!arraysEqual(nextAgentContributors, original.agentContributors)) {
      update.agent_contributors = nextAgentContributors;
    }

    if (Object.keys(update).length === 0) {
      setServerError('Make at least one change before creating a revision.');
      return;
    }

    setLoading(true);
    setServerError(null);

    try {
      const result = await createRfcRevision(rfcId, { update, message });
      navigate(`/rfcs/${rfcId}/revisions/${result.revision.id}`);
    } catch (err) {
      setServerError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  if (fetching) {
    return <p className="text-gray-500">Loading...</p>;
  }

  return (
    <div className="mx-auto max-w-3xl">
      <div className="mb-6">
        <Link to={`/rfcs/${rfcId}`} className="text-sm text-blue-600 hover:text-blue-800">
          Back to RFC
        </Link>
        <h1 className="mt-2 text-2xl font-bold">Create Revision</h1>
        {rfcTitle && <p className="mt-1 text-sm text-gray-500">{rfcTitle}</p>}
      </div>

      {serverError && !original ? (
        <div className="rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {serverError}
        </div>
      ) : null}

      {original ? (
        <form onSubmit={handleSubmit}>
          <FormField label="Revision Message" error={errors.message}>
            <input
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              onBlur={() =>
                setErrors((current) => ({
                  ...current,
                  message: validateRevisionMessage(message),
                }))
              }
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            />
          </FormField>

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
                <span className="block font-medium text-gray-900">Public visibility</span>
                <span className="block text-gray-500">
                  Toggle whether this revision publishes the RFC to anonymous readers.
                </span>
              </span>
            </label>
          </div>

          <FormField label="Content" error={errors.content}>
            <div data-color-mode="light">
              <MDEditor
                value={content}
                onChange={(value) => setContent(value ?? '')}
                height={420}
              />
            </div>
          </FormField>

          {serverError && <p className="mb-4 text-sm text-red-600">{serverError}</p>}
          <SubmitButton loading={loading}>Create Revision</SubmitButton>
        </form>
      ) : null}
    </div>
  );
}
