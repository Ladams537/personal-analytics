<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import Button from '$lib/components/atomic/Button.svelte';
	import { api } from '$lib/services/api';

	type Principle = {
		principle_id: string;
		name: string;
		description: string | null;
	};

	let allPrinciples: Principle[] = [];
	let selectedPrinciples: Map<string, number> = new Map();
	let isLoading = true;
	let errorMessage = '';
	let isSubmitting = false;

	onMount(async () => {
		isLoading = true;
		errorMessage = '';
		try {
			// Use the new api.get function
			allPrinciples = await api.get('/api/principles');
		} catch (error: any) {
			errorMessage = error.message || 'Network error loading principles.';
		} finally {
			isLoading = false;
		}
	});

	// Handle checkbox changes
	function toggleSelection(principleId: string, checked: boolean) {
		if (checked) {
			if (selectedPrinciples.size < 3) {
				selectedPrinciples.set(principleId, selectedPrinciples.size + 1); // Assign next available rank
				selectedPrinciples = selectedPrinciples; // Trigger reactivity
			} else {
				// Prevent selecting more than 3 - uncheck the box visually
				const checkbox = document.getElementById(principleId) as HTMLInputElement;
				if (checkbox) checkbox.checked = false;
				alert('You can only select up to 3 principles.');
			}
		} else {
			const oldRank = selectedPrinciples.get(principleId);
			selectedPrinciples.delete(principleId);
			// Re-rank remaining items
			if (oldRank !== undefined) {
				const sortedEntries = Array.from(selectedPrinciples.entries()).sort(([, a], [, b]) => a - b);
				selectedPrinciples.clear();
				sortedEntries.forEach(([id], index) => {
					selectedPrinciples.set(id, index + 1);
				});
			}
			selectedPrinciples = selectedPrinciples; // Trigger reactivity
		}
	}

	async function handleSubmit() {
		console.log('Submitting selected principles...');
		isSubmitting = true;
		errorMessage = '';

		const payloadPrinciples = Array.from(selectedPrinciples.entries()).map(([id, rank]) => ({
			principle_id: id,
			rank: rank
		}));

		// We no longer send user_id, the token handles it
		const payload = {
			principles: payloadPrinciples
		};

		try {
			// Use the new api.post function
			await api.post('/api/onboarding/principles', payload);
			
			console.log('User principles saved.');
			alert('Onboarding complete!');
			goto('/'); // Go to the main dashboard
		} catch (error: any) {
			errorMessage = `Error saving principles: ${error.message}`;
			console.error('Principle save error:', error);
		} finally {
			isSubmitting = false;
		}
	}
</script>

<main>
	<h1>Onboarding: Your Principles</h1>
	<p>Select your top 3 guiding principles. They will be ranked automatically.</p>

	{#if isLoading}
		<p>Loading principles...</p>
	{:else if errorMessage}
		<p style="color: red;">{errorMessage}</p>
	{:else}
		<form on:submit|preventDefault={handleSubmit}>
			{#each allPrinciples as principle (principle.principle_id)}
				<div class="principle-item">
					<input
						type="checkbox"
						id={principle.principle_id}
						on:change={(e) => toggleSelection(principle.principle_id, e.currentTarget.checked)}
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

			{#if selectedPrinciples.size > 0}
				<Button type="submit" fullWidth={true}>Complete Onboarding</Button>
			{/if}
		</form>
	{/if}
</main>

<style>
	main {
		max-width: 600px;
		margin: 2rem auto;
		padding: 1.5rem;
		border: 1px solid #ddd;
		border-radius: 8px;
	}
	.principle-item {
		margin-bottom: 1rem;
		padding: 0.8rem;
		border: 1px solid #eee;
		border-radius: 4px;
		background-color: #fdfdfd;
	}
	label {
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