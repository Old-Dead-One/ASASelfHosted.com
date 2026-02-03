/**
 * Verification Explained — trust page.
 *
 * Plain-language and technical explanation of what verification means on ASA Self-Hosted.
 * Content must match platform behavior; no Stripe, agent, or roadmap references.
 */

export function VerificationPage() {
    return (
        <div className="py-8 px-4 max-w-3xl mx-auto">
            <h1 className="text-3xl font-bold text-foreground mb-6">
                Verification Explained
            </h1>

            <section className="mb-8 p-4 rounded-lg border-2 border-primary/30 bg-primary/5">
                <h2 className="text-xl font-semibold text-foreground mb-3">
                    TL;DR
                </h2>
                <p className="text-muted-foreground mb-3">
                    &quot;Verified&quot; means a server&apos;s identity has been cryptographically confirmed — not that the server is good, safe, or endorsed.
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground mb-3">
                    <li>Verification is optional and controlled by the server owner.</li>
                    <li>It confirms <strong>identity</strong>, not quality, safety, or playstyle.</li>
                    <li>It does not grant featured placement or ranking advantages.</li>
                    <li>It cannot be faked remotely (signed heartbeats + replay protection).</li>
                    <li>Badges and rankings are data-driven; rankings are not purchasable.</li>
                </ul>
                <p className="text-muted-foreground">
                    Verification exists so the data you see actually comes from the server it claims to represent.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    What &quot;Verified&quot; means on ASA Self-Hosted
                </h2>
                <p className="text-muted-foreground">
                    On ASA Self-Hosted, a <strong>Verified</strong> server is one whose identity has been cryptographically confirmed.
                </p>
                <p className="text-muted-foreground">
                    Verification is controlled by the server owner. It exists so players—and the directory itself—can tell that heartbeats and listing data come from the same server that claims to be running the game, not from an imposter or a misconfigured setup.
                </p>
                <p className="text-muted-foreground">
                    Verification confirms <strong>identity</strong>, not quality or playstyle.<br />
                    It does not guarantee uptime, population, moderation quality, or community behavior.
                </p>
                <p className="text-muted-foreground">
                    Verification is optional. Servers may list without it.
                </p>
                <p className="text-muted-foreground">
                    Verification exists to ensure that the data you see in the directory actually comes from the server it claims to represent.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    What verification confirms
                </h2>
                <p className="text-muted-foreground">
                    When a server is verified, the following are cryptographically verified:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li><strong>Server identity</strong> — the key that signs heartbeats</li>
                    <li><strong>Heartbeat authenticity</strong> — signed payloads from that server</li>
                    <li><strong>Map identity</strong> — which map the server reports</li>
                    <li><strong>Cluster membership</strong> — when the server is part of a cluster</li>
                </ul>
                <p className="text-muted-foreground">
                    The emphasis is on <strong>proof</strong>.<br />
                    We verify that data came from the claimed source—not that the server is &quot;good,&quot; &quot;safe,&quot; or endorsed.
                </p>
            </section>

            <section className="mb-8 p-4 rounded-lg border-2 border-amber-500/50 bg-amber-500/5">
                <h2 className="text-xl font-semibold text-foreground mb-3">
                    What verification does <em>not</em> do
                </h2>
                <p className="text-muted-foreground mb-3">Verification:</p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Does <strong>not</strong> grant featured placement in the directory</li>
                    <li>Does <strong>not</strong> bypass platform rules or moderation</li>
                    <li>Does <strong>not</strong> allow remote control of servers</li>
                    <li>Does <strong>not</strong> collect player data by default</li>
                    <li>Does <strong>not</strong> make rankings purchasable—rankings are data-driven only</li>
                </ul>
                <p className="text-muted-foreground mt-3">
                    Verification is not an endorsement and not a quality rating.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    How verification works (technical overview)
                </h2>
                <p className="text-muted-foreground">
                    Server owners (or cluster owners) use a <strong>public/private key pair</strong>.
                </p>
                <p className="text-muted-foreground">
                    The server or agent sends heartbeats that are <strong>signed with the private key</strong>.<br />
                    ASA Self-Hosted verifies the signature using the corresponding public key.
                </p>
                <p className="text-muted-foreground">
                    This allows the platform to confirm that:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>The heartbeat was produced by the claimed server</li>
                    <li>The data has not been altered in transit</li>
                </ul>
                <p className="text-muted-foreground">
                    Replay protection ensures old heartbeats cannot be reused.
                </p>
                <p className="text-muted-foreground">
                    Because only the holder of the private key can produce valid signatures, verification <strong>cannot be faked remotely</strong>. This prevents impersonation and spoofed listings.
                </p>
            </section>

            <section className="space-y-4">
                <h2 className="text-xl font-semibold text-foreground">
                    Badges and rankings
                </h2>
                <p className="text-muted-foreground">
                    Badges on ASA Self-Hosted are <strong>data-driven</strong>. They reflect what the platform can verify or observe (for example: verified, new, stable).
                </p>
                <p className="text-muted-foreground">
                    Verification is a prerequisite for some badges, not all.
                </p>
                <p className="text-muted-foreground">
                    Rankings (such as quality or favorites) are <strong>not purchasable</strong> and are not influenced by payment.
                </p>
            </section>
        </div>
    )
}
