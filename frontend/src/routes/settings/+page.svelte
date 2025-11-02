<!-- /frontend/src/routes/settings/+page.svelte -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/services/api';
	import Button from '$lib/components/atomic/Button.svelte';
	import Card from '$lib/components/atomic/Card.svelte';

	// --- Types ---
	type Principle = {
		principle_id: string;
		name: string;
		description: string | null;
	};
	type UserPrinciple = {
		principle_id: string;
		principle_rank: number;
	};
	type UserPersonalityTrait = {
		scale_name: string;
		trait_name: string;
		value: number;
		display_order: number;
	};

	// --- State ---
	let isLoading = $state(true);
	let errorMessage = $state('');
	let isSavingPersonality = $state(false);
	let isSavingPrinciples = $state(false);

	// Personality form state
	let personalityForm = $state([
		{ scale: 'Mind', name1: 'Introverted', name2: 'Extraverted', value: 50, order: 1 },
		{ scale: 'Energy', name1: 'Intuitive', name2: 'Observant', value: 50, order: 2 },
		{ scale: 'Nature', name1: 'Feeling', name2: 'Thinking', value: 50, order: 3 },
		{ scale: 'Tactics', name1: 'Judging', name2: 'Prospecting', value: 50, order: 4 },
		{ scale: 'Identity', name1: 'Turbulent', name2: 'Assertive', value: 50, order: 5 }
	]);

	// Principles form state
	let allPrinciples: Principle[] = $state([]);
	let selectedPrinciples: Map<string, number> = $state(new Map());

	// --- Data Loading ---
	onMount(async () => {
		isLoading = true;
		errorMessage = '';
		try {
			// Fetch all data in parallel
			const [allPrinciplesData, userPrinciplesData, userPersonalityData] = await Promise.all([
				api.get('/api/principles'),
				api.get('/api/settings/principles'),
				api.get('/api/settings/personality')
			]);

			// 1. Populate Principles
			allPrinciples = allPrinciplesData;
			const userPrinciplesMap = new Map(
				userPrinciplesData.map((p: UserPrinciple) => [p.principle_id, p.principle_rank])
			);
			selectedPrinciples = userPrinciplesMap as Map<string, number>;

			// 2. Populate Personality
			const newPersonalityForm = [...personalityForm];
			userPersonalityData.forEach((trait: UserPersonalityTrait) => {
				const formItem = newPersonalityForm.find(item => item.scale === trait.scale_name);
				if (formItem) {
					// The saved 'value' is the dominant percentage, and 'trait_name' is the dominant trait
					// We need to convert this back to the slider's 0-100 scale
					if (trait.trait_name === formItem.name1) {
						// e.g., Trait is 'Introverted' (name1)
						formItem.value = trait.value;
					} else if (trait.trait_name === formItem.name2) {
						// e.g., Trait is 'Extraverted' (name2)
						formItem.value = 100 - trait.value;
					}
				}
			});
			personalityForm = newPersonalityForm;

		} catch (error: any) {
			errorMessage = error.message || 'Failed to load settings.';
			console.error('Settings page load error:', error);
		} finally {
			isLoading = false;
		}
	});

	// --- Principles: Toggle Selection (Same as onboarding) ---
	function toggleSelection(principleId: string, checked: boolean) {
		const newSelected = new Map(selectedPrinciples);
		if (checked) {
			if (newSelected.size < 3) {
				newSelected.set(principleId, newSelected.size + 1);
			} else {
				// Prevent selecting more than 3
				const checkbox = document.getElementById(principleId) as HTMLInputElement;
				if (checkbox) checkbox.checked = false;
				alert('You can only select up to 3 principles.');
				return;
			}
		} else {
			newSelected.delete(principleId);
		}
		
		// Re-rank remaining items
		const sortedEntries = Array.from(newSelected.entries()).sort(([, a], [, b]) => a - b);
		const reRankedMap = new Map();
		sortedEntries.forEach(([id], index) => {
			reRankedMap.set(id, index + 1);
		});
		selectedPrinciples = reRankedMap;
	}

	// --- Submit Handlers ---
	async function handleSubmitPersonality() {
		isSavingPersonality = true;
		errorMessage = '';
		try {
			const payloadTraits = personalityForm.map((t) => ({
				scale_name: t.scale,
				trait_name: t.value >= 50 ? t.name1 : t.name2,
				value: t.value >= 50 ? t.value : 100 - t.value,
				display_order: t.order
			}));
			
			// We'll use api.put, assuming it exists in your api.ts service
			await api.put('/api/settings/personality', { traits: payloadTraits });
			alert('Personality traits saved!');
		} catch (error: any) {
			errorMessage = error.message || 'Failed to save personality.';
		} finally {
			isSavingPersonality = false;
		}
	}

	async function handleSubmitPrinciples() {
		isSavingPrinciples = true;
		errorMessage = '';
		try {
			const payloadPrinciples = Array.from(selectedPrinciples.entries()).map(([id, rank]) => ({
				principle_id: id,
				rank: rank
			}));

			// We'll use api.put
			await api.put('/api/settings/principles', { principles: payloadPrinciples });
			alert('Principles saved!');
		} catch (error: any) {
			errorMessage = error.message || 'Failed to save principles.';
		} finally {
			isSavingPrinciples = false;
		}
	}
</script>

<main>
	<h1>Settings</h1>

	{#if isLoading}
		<p>Loading your settings...</p>
	{:else if errorMessage}
		<p class="error">{errorMessage}</p>
	{:else}
		<!-- Personality Settings Card -->
		<Card>
			{#snippet header()}
				<h2>Personality Traits</h2>
			{/snippet}
			<form onsubmit={handleSubmitPersonality}>
				{#each personalityForm as trait, i}
					<div class="trait-slider">
						<label for="trait-{i}">{trait.name1} vs {trait.name2}</label>
						<input type="range" id="trait-{i}" bind:value={trait.value} min="0" max="100" step="1" />
						<span>{trait.value}% {trait.name1} / {100 - trait.value}% {trait.name2}</span>
					</div>
				{/each}
				<Button type="submit" loading={isSavingPersonality} fullWidth={true}>
					Save Personality
				</Button>
			</form>
		</Card>

		<!-- Principles Settings Card -->
		<Card>
			{#snippet header()}
				<h2>Your Principles</h2>
			{/snippet}
			<p class="subtitle">Select your top 3 guiding principles.</p>
			<form onsubmit={handleSubmitPrinciples}>
				{#each allPrinciples as principle (principle.principle_id)}
					<div class="principle-item">
						<input
							type="checkbox"
							id={principle.principle_id}
							onchange={(e) => toggleSelection(principle.principle_id, e.currentTarget.checked)}
							checked={selectedPrinciples.has(principle.principle_id)}
						/>
						<label for={principle.principle_id}>
							{#if selectedPrinciples.has(principle.principle_id)}
								<span class="rank">#{selectedPrinciples.get(principle.principle_id)}</span>
							{/if}
							{principle.name}
						</label>
						{#if principle.description}
							<p class="description">{principle.description}</p>
						{/if}
					</div>
				{/each}
				
				{#if allPrinciples.length > 0}
					<Button type="submit" loading={isSavingPrinciples} fullWidth={true}>
						Save Principles
					</Button>
				{/if}
			</form>
		</Card>
	{/if}
</main>

<style>
	h1 {
		text-align: center;
		color: #333;
	}
	/* Use :global to style the cards from this page */
	:global(main > .card) {
		margin-bottom: 2rem;
	}
	.error {
		color: red;
		text-align: center;
	}
	.subtitle {
		text-align: center;
		color: #555;
		margin-top: -0.5rem;
		margin-bottom: 1.5rem;
	}

	/* Personality Styles */
	.trait-slider {
		margin-bottom: 1.5rem;
	}
	.trait-slider label {
		display: block;
		font-weight: bold;
		margin-bottom: 0.5rem;
	}
	.trait-slider input[type='range'] {
		width: 100%;
	}
	.trait-slider span {
		display: block;
		text-align: center;
		margin-top: 0.3rem;
		font-size: 0.9em;
		color: #555;
	}

	/* Principles Styles */
	.principle-item {
		margin-bottom: 1rem;
		padding: 0.8rem;
		border: 1px solid #eee;
		border-radius: 4px;
		background-color: #fdfdfd;
	}
	.principle-item label {
		font-weight: bold;
		margin-left: 0.5rem;
		cursor: pointer;
	}
	.rank {
		display: inline-block;
		background-color: #eee;
		color: #333;
		padding: 2px 6px;
		border-radius: 3px;
		font-size: 0.8em;
		margin-right: 0.5rem;
	}
	.description {
		font-size: 0.9em;
		color: #666;
		margin-top: 0.3rem;
		margin-left: 1.8rem; /* Align with label text */
	}
</style>