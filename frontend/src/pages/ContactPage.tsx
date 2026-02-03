/**
 * Contact page.
 *
 * Placeholder for site contact (form and/or email). To be wired up right before initial release.
 * Linked from Legal (Section 13), Data Rights, and footer.
 */

export function ContactPage() {
    return (
        <div className="py-8 px-4 max-w-3xl mx-auto">
            <h1 className="text-3xl font-bold text-foreground mb-2">
                Contact
            </h1>
            <p className="text-sm text-muted-foreground mb-6">
                Get in touch with ASA Self-Hosted.
            </p>
            <section className="space-y-4">
                <p className="text-muted-foreground">
                    For questions about the Privacy Policy, data rights requests (access, correction, deletion), or other inquiries, use the contact method below.
                </p>
                <p className="text-muted-foreground text-sm italic">
                    Contact form and email will be wired up before initial release.
                </p>
            </section>
        </div>
    )
}
