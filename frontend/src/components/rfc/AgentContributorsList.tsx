interface AgentContributorsListProps {
  contributors: string[];
  emptyLabel?: string;
}

export function AgentContributorsList({
  contributors,
  emptyLabel = 'No agent contributors',
}: AgentContributorsListProps) {
  if (contributors.length === 0) {
    return <span className="text-sm text-gray-400">{emptyLabel}</span>;
  }

  return (
    <div className="flex flex-wrap gap-2">
      {contributors.map((contributor) => (
        <span
          key={contributor}
          className="rounded-full bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-700"
        >
          {contributor}
        </span>
      ))}
    </div>
  );
}
