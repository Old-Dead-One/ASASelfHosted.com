/**
 * Add Server card component.
 *
 * Displays an outline-style card with a plus icon for adding a new server.
 * Used in the dashboard carousel. Uses style-guide tokens and focus ring.
 * Supports disabled state when server limit is reached.
 */

interface AddServerCardProps {
    onAddServer: () => void
    onAddCluster: () => void
    addServerDisabled?: boolean
    addServerDisabledReason?: string
    /** When true, hide the "Add cluster" button. */
    hasCluster?: boolean
    serversUsed?: number
    serversLimit?: number
    clustersUsed?: number
    clustersLimit?: number
}

function PlusCircle({ colorClassName }: { colorClassName: string }) {
    return (
        <div className={`w-10 h-10 rounded-full border-2 flex items-center justify-center ${colorClassName}`.trim()}>
            <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="w-5 h-5"
            >
                <line x1="12" y1="5" x2="12" y2="19" />
                <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
        </div>
    )
}

export function AddServerCard({
    onAddServer,
    onAddCluster,
    addServerDisabled,
    addServerDisabledReason,
    hasCluster,
    serversUsed,
    serversLimit,
    clustersUsed,
    clustersLimit,
}: AddServerCardProps) {
    return (
        <div className="w-full h-full min-h-[260px] max-h-[260px] overflow-hidden rounded-xl border-2 border-dashed border-input bg-background-elevated/60 shadow-md shadow-black/30 transition-all p-3 flex flex-col gap-3 hover:border-primary/50 hover:bg-muted/20">
            <button
                type="button"
                onClick={onAddServer}
                disabled={addServerDisabled}
                title={addServerDisabled ? addServerDisabledReason : undefined}
                className="flex-1 min-h-0 rounded-lg hover:bg-muted/20 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:opacity-60 disabled:cursor-not-allowed flex flex-col items-center justify-center gap-2"
                aria-label={addServerDisabled ? addServerDisabledReason ?? 'Add new server (limit reached)' : 'Add new server'}
            >
                <PlusCircle colorClassName="border-primary/50 text-primary" />
                <div className="text-center">
                    <p className="text-lg font-semibold text-foreground">Add Server</p>
                    {serversUsed != null && serversLimit != null && (
                        <p className="text-xs text-muted-foreground mt-1">
                            <span className="font-medium text-primary/90">{serversUsed}</span> of{' '}
                            <span className="font-medium text-primary/90">{serversLimit}</span> used
                        </p>
                    )}
                </div>
            </button>

            {!hasCluster && (
                <>
                    <div className="h-px bg-input/70" aria-hidden />
                    <button
                        type="button"
                        onClick={onAddCluster}
                        className="flex-1 min-h-0 rounded-lg hover:bg-amber-500/10 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:ring-offset-2 focus-visible:ring-offset-background flex flex-col items-center justify-center gap-2"
                        aria-label="Add cluster"
                    >
                        <PlusCircle colorClassName="border-amber-500/45 text-amber-400" />
                        <div className="text-center">
                            <p className="text-lg font-semibold text-foreground">Add Cluster</p>
                            {clustersUsed != null && clustersLimit != null && (
                                <p className="text-xs text-muted-foreground mt-1">
                                    <span className="font-medium text-amber-400">{clustersUsed}</span> of{' '}
                                    <span className="font-medium text-amber-400">{clustersLimit}</span> used
                                </p>
                            )}
                        </div>
                    </button>
                </>
            )}
        </div>
    )
}
