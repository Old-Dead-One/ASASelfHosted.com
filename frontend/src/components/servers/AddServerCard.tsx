/**
 * Add Server card component.
 *
 * Displays an outline-style card with a plus icon for adding a new server.
 * Used in the dashboard carousel. Uses style-guide tokens and focus ring.
 */

interface AddServerCardProps {
    onClick: () => void
}

export function AddServerCard({ onClick }: AddServerCardProps) {
    return (
        <button
            type="button"
            onClick={onClick}
            className="w-full h-full min-h-[260px] rounded-xl border-2 border-dashed border-input bg-background-elevated/60 shadow-md shadow-black/30 p-4 hover:border-primary/50 hover:bg-muted/20 transition-all flex flex-col items-center justify-center gap-4 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:ring-offset-2 focus-visible:ring-offset-background"
            aria-label="Add new server"
        >
            <div className="w-16 h-16 rounded-full border-2 border-primary/50 flex items-center justify-center">
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="w-8 h-8 text-primary"
                >
                    <line x1="12" y1="5" x2="12" y2="19" />
                    <line x1="5" y1="12" x2="19" y2="12" />
                </svg>
            </div>
            <div className="text-center">
                <p className="text-lg font-semibold text-foreground mb-1">Add Server</p>
                <p className="text-sm text-muted-foreground">Create a new server listing</p>
            </div>
        </button>
    )
}
