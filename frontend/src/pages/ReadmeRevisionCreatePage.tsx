import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import MDEditor from '@uiw/react-md-editor';
import { createReadmeRevision, getReadme } from '../api/readme';
import { FormField } from '../components/forms/FormField';
import { SubmitButton } from '../components/forms/SubmitButton';
import { validateReadmeContent, validateReadmeReason } from '../validation';

export function ReadmeRevisionCreatePage() {
  const navigate = useNavigate();
  const [reason, setReason] = useState('');
  const [content, setContent] = useState('');
  const [isPublic, setIsPublic] = useState(false);
  const [hasExistingReadme, setHasExistingReadme] = useState(false);
  const [errors, setErrors] = useState<Record<string, string | null>>({});
  const [serverError, setServerError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);

  useEffect(() => {
    getReadme()
      .then((response) => {
        setContent(response.readme.content);
        setIsPublic(response.readme.public);
        setHasExistingReadme(true);
      })
      .catch((err) => {
        if ((err as { status?: number }).status !== 404) {
          setServerError((err as Error).message);
        }
      })
      .finally(() => setFetching(false));
  }, []);

  function validate(): boolean {
    const nextErrors = {
      reason: validateReadmeReason(reason),
      content: validateReadmeContent(content),
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
      const result = await createReadmeRevision({
        reason,
        content,
        public: isPublic,
      });
      navigate(`/readme/revisions/${result.revision.revision_id}`);
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
    <div className="mx-auto max-w-4xl">
      <div className="mb-6">
        <div className="flex flex-wrap gap-3 text-sm">
          <Link to="/readme" className="text-blue-600 hover:text-blue-800">
            Back to Server Guide
          </Link>
          <Link to="/readme/revisions" className="text-blue-600 hover:text-blue-800">
            Back to Revision History
          </Link>
        </div>
        <h1 className="mt-3 text-2xl font-bold">
          {hasExistingReadme ? 'Publish README Revision' : 'Create Server Guide'}
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          {hasExistingReadme
            ? 'Update the current server guide content or visibility.'
            : 'Publish the initial server guide for this MDRFC instance.'}
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        <FormField label="Revision Reason" error={errors.reason}>
          <input
            value={reason}
            onChange={(event) => setReason(event.target.value)}
            onBlur={() =>
              setErrors((current) => ({
                ...current,
                reason: validateReadmeReason(reason),
              }))
            }
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
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
              <span className="block font-medium text-gray-900">Make this README public</span>
              <span className="block text-gray-500">
                Private README revisions remain visible to authenticated users only.
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
        <SubmitButton loading={loading}>
          {hasExistingReadme ? 'Publish Revision' : 'Create Server Guide'}
        </SubmitButton>
      </form>
    </div>
  );
}
