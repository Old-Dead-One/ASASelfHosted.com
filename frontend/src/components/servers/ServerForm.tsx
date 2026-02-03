/**
 * Server form component.
 *
 * Form for creating/editing server listings.
 */

import { useState, FormEvent, useEffect, useCallback, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import type { ServerStatus, GameMode, Ruleset } from '@/types'
import { listMyClusters, type Cluster, resolveMods, type ResolvedMod, apiRequest } from '@/lib/api'
import { Button } from '@/components/ui/Button'

const OTHER_MAP_VALUE = '__other__'

export type PlatformChoice = 'pc' | 'console' | 'crossplay'

const FORM_GAP = 'gap-3'
const FORM_SPACE = 'space-y-3'

const DEFAULT_JOIN_INSTRUCTIONS = `Open ARK: Survival Ascended and go to Join Game.
Select UNOFFICIAL at the top, then enable Show Player Servers.
Enter the name of the server you wish to join in the search bar.
Use Refresh if the server does not appear immediately.
Use the password above if required.
Join details may also be provided via the server's Discord or community page.
These steps may need to be repeated when reconnecting.`

export interface ServerFormData {
    is_self_hosted_confirmed: boolean
    name: string
    description: string
    map_name: string
    join_address: string
    join_password: string
    join_instructions: string
    discord_url: string
    website_url: string
    mod_list: string
    rates: string
    wipe_info: string
    game_mode: GameMode | ''
    ruleset: Ruleset | ''
    rulesets: Ruleset[]
    effective_status: ServerStatus | ''
    cluster_id: string | ''
    platform: PlatformChoice | ''
}

interface ServerFormProps {
    initialData?: Partial<ServerFormData>
    onSubmit: (data: ServerFormData) => Promise<void>
    onCancel?: () => void
    onDelete?: () => void
    submitLabel?: string
}

export function ServerForm({
    initialData,
    onSubmit,
    onCancel,
    onDelete,
    submitLabel = 'Create Server',
}: ServerFormProps) {
    const [formData, setFormData] = useState<ServerFormData>({
        is_self_hosted_confirmed: initialData?.is_self_hosted_confirmed ?? false,
        name: initialData?.name || '',
        description: initialData?.description || '',
        map_name: initialData?.map_name || '',
        join_address: initialData?.join_address || '',
        join_password: initialData?.join_password || '',
        join_instructions: initialData?.join_instructions !== undefined ? initialData.join_instructions : DEFAULT_JOIN_INSTRUCTIONS,
        discord_url: initialData?.discord_url || '',
        website_url: initialData?.website_url || '',
        mod_list: initialData?.mod_list || '',
        rates: initialData?.rates || '',
        wipe_info: initialData?.wipe_info || '',
        game_mode: initialData?.game_mode || '',
        ruleset: initialData?.ruleset || '',
        rulesets: initialData?.rulesets ?? [],
        effective_status: initialData?.effective_status || '',
        cluster_id: initialData?.cluster_id || '',
        platform: initialData?.platform || '',
    })
    const [clusters, setClusters] = useState<Cluster[]>([])
    const [loadingClusters, setLoadingClusters] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)
    const [resolvedMods, setResolvedMods] = useState<ResolvedMod[]>([])
    const [resolvingMods, setResolvingMods] = useState(false)
    const [modResolveError, setModResolveError] = useState<string | null>(null)

    const { data: mapsData } = useQuery({
        queryKey: ['maps'],
        queryFn: async () => apiRequest<{ data: { id: string; name: string }[] }>('/api/v1/maps'),
        staleTime: 300_000,
    })
    const mapOptions = mapsData?.data ?? []
    const mapSelectValue = useMemo(() => {
        const name = formData.map_name.trim()
        if (!name) return ''
        const found = mapOptions.find((m) => m.name === name)
        return found ? found.name : OTHER_MAP_VALUE
    }, [formData.map_name, mapOptions])

    // Load clusters on mount
    useEffect(() => {
        setLoadingClusters(true)
        listMyClusters()
            .then(setClusters)
            .catch(() => {
                // Silently fail - clusters are optional
            })
            .finally(() => setLoadingClusters(false))
    }, [])

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault()
        setError(null)
        setLoading(true)

        try {
            await onSubmit(formData)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to save server')
        } finally {
            setLoading(false)
        }
    }

    const handleResolveMods = useCallback(async () => {
        const modListStr = formData.mod_list.trim()
        if (!modListStr) {
            setResolvedMods([])
            return
        }

        // Parse mod IDs from comma-separated string
        const modIds = modListStr
            .split(',')
            .map((id) => id.trim())
            .filter((id) => id.length > 0)
            .map((id) => {
                const parsed = parseInt(id, 10)
                return isNaN(parsed) ? null : parsed
            })
            .filter((id): id is number => id !== null && id > 0)

        if (modIds.length === 0) {
            setResolvedMods([])
            setModResolveError('No valid mod IDs found')
            return
        }

        setResolvingMods(true)
        setModResolveError(null)

        try {
            const response = await resolveMods(modIds)
            setResolvedMods(response.data)
            if (response.missing.length > 0) {
                setModResolveError(
                    `Could not resolve ${response.missing.length} mod ID(s): ${response.missing.join(', ')}`
                )
            }
        } catch (err) {
            setModResolveError(err instanceof Error ? err.message : 'Failed to resolve mods')
            setResolvedMods([])
        } finally {
            setResolvingMods(false)
        }
    }, [formData.mod_list])

    const hasRuleset = ['vanilla', 'vanilla_qol', 'modded'].some((r) => formData.rulesets.includes(r as Ruleset))
    const canSubmit =
        formData.is_self_hosted_confirmed &&
        formData.map_name.trim() !== '' &&
        formData.game_mode !== '' &&
        formData.platform !== '' &&
        hasRuleset

    return (
        <form onSubmit={handleSubmit} className={FORM_SPACE}>
            {error && <div className="form-error">{error}</div>}

            <section className="relative overflow-hidden rounded-lg tek-border">
                <div className="absolute inset-0 bg-tek-wall" aria-hidden />
                <div className="absolute inset-0 tek-seam opacity-70 pointer-events-none" aria-hidden />
                <div className="relative p-3 space-y-3 bg-background/65 backdrop-blur-[1px]">
                    <div className={`grid grid-cols-1 md:grid-cols-2 ${FORM_GAP} md:items-start`}>
                        <div>
                            <label htmlFor="name" className="label-tek">Server Name <span className={!formData.name.trim() ? 'text-destructive' : ''}>*</span></label>
                            <input id="name" type="text" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} required maxLength={120} className="input-tek" />
                        </div>
                        <div>
                            <label htmlFor="map_name" className="label-tek">Map <span className={!formData.map_name.trim() ? 'text-destructive' : ''}>*</span></label>
                            <select
                                id="map_name"
                                value={mapSelectValue}
                                onChange={(e) => {
                                    const v = e.target.value
                                    if (v === OTHER_MAP_VALUE || v === '') {
                                        setFormData({ ...formData, map_name: v === OTHER_MAP_VALUE ? (mapOptions.some((m) => m.name === formData.map_name) ? '' : formData.map_name) : '' })
                                    } else {
                                        setFormData({ ...formData, map_name: v })
                                    }
                                }}
                                required
                                className="input-tek"
                            >
                                <option value="">Select...</option>
                                {mapOptions.map((m) => (
                                    <option key={m.id} value={m.name}>
                                        {m.name}
                                    </option>
                                ))}
                                <option value={OTHER_MAP_VALUE}>Other</option>
                            </select>
                            {mapSelectValue === OTHER_MAP_VALUE && (
                                <input
                                    type="text"
                                    aria-label="Custom map name"
                                    placeholder="Enter map name"
                                    value={formData.map_name}
                                    onChange={(e) => setFormData({ ...formData, map_name: e.target.value })}
                                    maxLength={80}
                                    className="input-tek mt-2"
                                />
                            )}
                        </div>
                    </div>

                    <div>
                        <label htmlFor="description" className="label-tek">Description</label>
                        <div className="relative">
                            <textarea id="description" value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} rows={2} maxLength={400} className="input-tek-auto !h-auto min-h-[4.5rem] resize-none pr-14 pb-6" />
                            <p className="absolute bottom-2 right-2 text-xs text-muted-foreground pointer-events-none" aria-hidden>{formData.description.length}/400</p>
                        </div>
                    </div>

                    <div className={`grid grid-cols-1 md:grid-cols-2 ${FORM_GAP} md:items-start`}>
                        <div>
                            <label htmlFor="game_mode" className="label-tek">Game Mode <span className={!formData.game_mode ? 'text-destructive' : ''}>*</span></label>
                            <select id="game_mode" value={formData.game_mode} onChange={(e) => setFormData({ ...formData, game_mode: e.target.value as GameMode | '' })} required className="input-tek">
                                <option value="">Select...</option>
                                <option value="pvp">PvP</option>
                                <option value="pve">PvE</option>
                                <option value="pvpve">PvPvE</option>
                            </select>
                        </div>
                        <div>
                            <span className="label-tek">Platform <span className={!formData.platform ? 'text-destructive' : ''}>*</span></span>
                            <div
                                className="inline-flex h-9 rounded-md border border-input/80 bg-muted/40 p-0.5 shadow-sm items-stretch"
                                role="radiogroup"
                                aria-label="Platform"
                            >
                                {(['pc', 'console', 'crossplay'] as const).map((v) => {
                                    const selected = formData.platform === v
                                    return (
                                        <button
                                            key={v}
                                            type="button"
                                            role="radio"
                                            aria-checked={selected}
                                            onClick={() => setFormData({ ...formData, platform: v })}
                                            className={
                                                'h-full px-3 text-sm rounded-[5px] transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1 flex items-center justify-center ' +
                                                (selected
                                                    ? 'bg-background text-foreground shadow-sm border border-border/50'
                                                    : 'text-muted-foreground hover:text-foreground hover:bg-muted/60')
                                            }
                                        >
                                            {v === 'pc' ? 'PC only' : v === 'console' ? 'Console only' : 'Crossplay'}
                                        </button>
                                    )
                                })}
                            </div>
                        </div>

                        <div>
                            <label htmlFor="mod_list" className="label-tek">Mod List (comma-separated)</label>
                            <div className="flex gap-2">
                                <input
                                    id="mod_list"
                                    type="text"
                                    value={formData.mod_list}
                                    onChange={(e) => {
                                        setFormData({ ...formData, mod_list: e.target.value })
                                        setModResolveError(null)
                                    }}
                                    onBlur={handleResolveMods}
                                    placeholder="123456, 789012"
                                    maxLength={500}
                                    className="input-tek flex-1"
                                />
                                <Button
                                    type="button"
                                    variant="secondary"
                                    size="sm"
                                    onClick={handleResolveMods}
                                    disabled={resolvingMods || !formData.mod_list.trim()}
                                    aria-label="Resolve mod names"
                                >
                                    {resolvingMods ? 'Resolving...' : 'Resolve'}
                                </Button>
                            </div>
                            {modResolveError && (
                                <p className="text-xs text-destructive mt-1">{modResolveError}</p>
                            )}
                            {resolvedMods.length > 0 && (
                                <div className="mt-2 flex flex-wrap gap-1.5">
                                    {resolvedMods.map((mod) => (
                                        <span
                                            key={mod.mod_id}
                                            className="inline-flex items-center gap-1 px-2 py-1 text-xs rounded-md bg-muted/60 text-foreground border border-input/60"
                                        >
                                            <span className="font-medium">{mod.name}</span>
                                            <span className="text-muted-foreground">({mod.mod_id})</span>
                                        </span>
                                    ))}
                                </div>
                            )}
                        </div>
                        <div>
                            <div className="flex items-center gap-1.5 mb-0.5">
                                <span className="text-sm font-medium text-foreground">Ruleset <span className={!hasRuleset ? 'text-destructive' : ''}>*</span></span>
                                <span className="group relative inline-flex">
                                    <button
                                        type="button"
                                        className="rounded-full w-4 h-4 flex items-center justify-center text-muted-foreground hover:text-foreground border border-current text-[10px] font-medium leading-none shadow-sm hover:shadow focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1"
                                        aria-label="Ruleset help"
                                        aria-describedby="ruleset-explanation"
                                    >
                                        ?
                                    </button>
                                    <span
                                        id="ruleset-explanation"
                                        role="alert"
                                        className="absolute left-0 top-full z-10 mt-1.5 p-2.5 min-w-[400px] max-w-[500px] rounded-md border border-input bg-muted text-xs text-foreground shadow-md hidden group-hover:block group-focus-within:block"
                                    >
                                        Server Ruleset <br /> Vanilla: Official rates. Mods allowed. No boosts. <br />
                                        Vanilla QoL: Light QoL mods only. Boosts allowed. No heavy mods. <br />
                                        Modded: Full mods allowed. <br />
                                        Boosted is optional where permitted. Choose one base ruleset. <br />
                                    </span>
                                </span>
                            </div>
                            <div className="flex flex-wrap gap-3">
                                {(['vanilla', 'vanilla_qol', 'modded'] as const).map((r) => {
                                    const baseSelected = formData.rulesets.includes(r)
                                    const incompatible: Ruleset[] =
                                        r === 'vanilla'
                                            ? (['vanilla_qol'] as Ruleset[])
                                            : r === 'vanilla_qol'
                                                ? (['vanilla', 'modded'] as Ruleset[])
                                                : (['vanilla_qol'] as Ruleset[])
                                    return (
                                        <button
                                            key={r}
                                            type="button"
                                            role="button"
                                            aria-pressed={baseSelected}
                                            aria-label={r === 'vanilla_qol' ? 'Vanilla QoL' : r.charAt(0).toUpperCase() + r.slice(1)}
                                            onClick={() => {
                                                let next = baseSelected
                                                    ? formData.rulesets.filter((x) => x !== r)
                                                    : [...formData.rulesets.filter((x) => !incompatible.includes(x)), r]
                                                if (r === 'vanilla' && next.includes('vanilla')) next = next.filter((x) => x !== 'boosted')
                                                if (r === 'vanilla_qol' && next.includes('vanilla_qol')) next = next.filter((x) => x !== 'modded')
                                                setFormData({ ...formData, rulesets: next })
                                            }}
                                            className={
                                                'px-3 py-1.5 text-sm rounded-full border transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1 ' +
                                                (baseSelected
                                                    ? 'bg-primary/10 border-primary/40 text-foreground shadow-sm'
                                                    : 'border-input/80 bg-muted/40 text-muted-foreground hover:bg-muted/70 hover:text-foreground hover:border-input')
                                            }
                                        >
                                            {r === 'vanilla_qol' ? 'Vanilla QoL' : r.charAt(0).toUpperCase() + r.slice(1)}
                                        </button>
                                    )
                                })}
                                <button
                                    type="button"
                                    role="button"
                                    aria-pressed={formData.rulesets.includes('boosted')}
                                    aria-label="Boosted"
                                    onClick={() => {
                                        if (formData.rulesets.includes('boosted')) {
                                            setFormData({ ...formData, rulesets: formData.rulesets.filter((r) => r !== 'boosted') })
                                        } else {
                                            const next = [...formData.rulesets.filter((r) => r !== 'vanilla'), 'boosted'] as Ruleset[]
                                            setFormData({ ...formData, rulesets: next })
                                        }
                                    }}
                                    className={
                                        'px-3 py-1.5 text-sm rounded-full border transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1 ' +
                                        (formData.rulesets.includes('boosted')
                                            ? 'bg-amber-500/15 border-amber-500/50 text-amber-900 dark:text-amber-200 shadow-sm'
                                            : 'border-amber-500/30 bg-muted/40 text-muted-foreground hover:bg-amber-500/10 hover:border-amber-500/40 hover:text-foreground')
                                    }
                                >
                                    Boosted
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <section className="relative overflow-hidden rounded-lg tek-border">
                <div className="absolute inset-0 bg-tek-wall" aria-hidden />
                <div className="absolute inset-0 tek-seam opacity-70 pointer-events-none" aria-hidden />
                <div className="relative p-3 space-y-3 bg-background/65 backdrop-blur-[1px]">
                    <div className={`grid grid-cols-1 md:grid-cols-2 ${FORM_GAP} md:items-start`}>
                        <div>
                            <label htmlFor="cluster_id" className="label-tek">Cluster</label>
                            <select id="cluster_id" value={formData.cluster_id} onChange={(e) => setFormData({ ...formData, cluster_id: e.target.value })} disabled={loadingClusters} className="input-tek disabled:opacity-50">
                                <option value="">No cluster</option>
                                {clusters.map((c) => (<option key={c.id} value={c.id}>{c.name}</option>))}
                            </select>
                            {clusters.length === 0 && !loadingClusters && <p className="text-xs text-muted-foreground mt-0.5">No clusters yet.</p>}
                        </div>
                        <div>
                            <label htmlFor="join_address" className="label-tek">Join Address</label>
                            <input id="join_address" type="text" value={formData.join_address} onChange={(e) => setFormData({ ...formData, join_address: e.target.value })} maxLength={256} className="input-tek" />
                        </div>
                    </div>

                    <div className={`grid grid-cols-1 md:grid-cols-3 ${FORM_GAP} md:items-start`}>
                        <div>
                            <label htmlFor="join_password" className="label-tek">Join Password (optional)</label>
                            <input id="join_password" type="text" value={formData.join_password} onChange={(e) => setFormData({ ...formData, join_password: e.target.value })} placeholder="Leave empty if none" maxLength={64} className="input-tek w-full" />
                        </div>
                        <div>
                            <label htmlFor="discord_url" className="label-tek">Discord URL (optional)</label>
                            <input id="discord_url" type="url" value={formData.discord_url} onChange={(e) => setFormData({ ...formData, discord_url: e.target.value })} placeholder="https://discord.gg/..." maxLength={512} className="input-tek w-full" />
                        </div>
                        <div>
                            <label htmlFor="website_url" className="label-tek">Website URL (optional)</label>
                            <input id="website_url" type="url" value={formData.website_url} onChange={(e) => setFormData({ ...formData, website_url: e.target.value })} placeholder="https://..." maxLength={512} className="input-tek w-full" />
                        </div>
                    </div>

                    <div>
                        <div className="flex items-center gap-1.5 mb-0.5">
                            <label htmlFor="join_instructions" className="label-tek">Join Instructions</label>
                            <span className="group relative inline-flex">
                                <button
                                    type="button"
                                    className="rounded-full w-4 h-4 flex items-center justify-center text-muted-foreground hover:text-foreground border border-current text-[10px] font-medium leading-none shadow-sm hover:shadow focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1"
                                    aria-label="Join Instructions help"
                                    aria-describedby="instructions-explanation"
                                >
                                    ?
                                </button>
                                <span
                                    id="instructions-explanation"
                                    role="alert"
                                    className="absolute left-0 top-full z-10 mt-1.5 p-2.5 min-w-[300px] max-w-[400px] rounded-md border border-input bg-muted text-xs text-foreground shadow-md hidden group-hover:block group-focus-within:block"
                                >
                                    The default text is a suggestion and can be changed as desired.
                                </span>
                            </span>
                        </div>
                        <div className="relative">
                            <textarea id="join_instructions" value={formData.join_instructions} onChange={(e) => setFormData({ ...formData, join_instructions: e.target.value })} rows={6} maxLength={400} className="input-tek-auto !h-auto min-h-[9rem] resize-none pr-14 pb-6" />
                            <p className="absolute bottom-2 right-2 text-xs text-muted-foreground pointer-events-none" aria-hidden>{formData.join_instructions.length}/400</p>
                        </div>
                    </div>

                    <div className={`grid grid-cols-1 md:grid-cols-2 ${FORM_GAP} md:items-start`}>
                        <div>
                            <label htmlFor="rates" className="label-tek">Rates</label>
                            <input id="rates" type="text" value={formData.rates} onChange={(e) => setFormData({ ...formData, rates: e.target.value })} maxLength={200} className="input-tek" />
                        </div>
                        <div>
                            <label htmlFor="effective_status" className="label-tek">Status</label>
                            <select id="effective_status" value={formData.effective_status} onChange={(e) => setFormData({ ...formData, effective_status: e.target.value as ServerStatus | '' })} className="input-tek">
                                <option value="">Select...</option>
                                <option value="online">Online</option>
                                <option value="offline">Offline</option>
                                <option value="unknown">Unknown</option>
                            </select>
                        </div>
                    </div>

                    <div className={`grid grid-cols-1 md:grid-cols-2 ${FORM_GAP} items-stretch`}>
                        <div className="flex flex-col">
                            <span className="label-tek">Required</span>
                            <div className="rounded-md border border-input/80 bg-muted/30 p-3 flex flex-col flex-1 min-h-[4.5rem] shadow-sm">
                                <p className="text-xs text-muted-foreground mb-2">ASASelfHosted is only for self-hosted servers (own hardware or cloud), not ASA official or Nitrado.</p>
                                <label className="flex items-center gap-2 cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={formData.is_self_hosted_confirmed}
                                        onChange={(e) => setFormData({ ...formData, is_self_hosted_confirmed: e.target.checked })}
                                        className="h-4 w-4 rounded border-input bg-background shadow-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1"
                                        aria-label="Confirm self-hosted"
                                    />
                                    <span className="text-sm text-foreground">I confirm this is a self-hosted server.</span>
                                </label>
                            </div>
                        </div>
                        <div className="flex flex-col">
                            <label htmlFor="wipe_info" className="label-tek">Wipe Info</label>
                            <textarea id="wipe_info" value={formData.wipe_info} onChange={(e) => setFormData({ ...formData, wipe_info: e.target.value })} rows={2} maxLength={400} className="input-tek-auto flex-1 min-h-[4.5rem] !h-auto resize-none" />
                        </div>
                    </div>
                </div>
            </section>

            <div className="border-t border-input/60 pt-4 mt-2 flex gap-3 items-center">
                <Button
                    type="submit"
                    variant="primary"
                    size="sm"
                    disabled={loading || !canSubmit}
                    aria-label={submitLabel}
                >
                    {loading ? 'Saving...' : submitLabel}
                </Button>
                {onCancel && (
                    <Button type="button" variant="secondary" size="sm" onClick={onCancel} aria-label="Cancel">
                        Cancel
                    </Button>
                )}
                {onDelete && (
                    <Button
                        type="button"
                        variant="danger"
                        size="sm"
                        onClick={onDelete}
                        className="ml-auto"
                        aria-label="Delete server"
                    >
                        Delete
                    </Button>
                )}
            </div>
        </form>
    )
}
