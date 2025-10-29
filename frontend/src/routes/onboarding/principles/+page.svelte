<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	type Principle = {
		principle_id: string;
		name: string;
		description: string | null;
	};

	let allPrinciples: Principle[] = [];
	let selectedPrinciples: Map<string, number> = new Map(); // Map<principle_id, rank>
	let isLoading = true;
	let errorMessage = '';

	// Fetch available principles when the page loads
    onMount(async () => {
		const token = localStorage.getItem('accessToken');
		if (!token) {
			goto('/login');
			return;
		}
        try {
            const response = await fetch('http://localhost:8000/api/principles',
				{ headers: { Authorization: `Bearer ${token}` } }
			);
            if (response.ok) {
                allPrinciples = await response.json();
                console.log('Fetched Principles:', allPrinciples); // <-- ADD THIS LINE
            } else {
                errorMessage = 'Failed to load principles.';
            }
        } catch (error) {
            errorMessage = 'Network error loading principles.';
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

		const payloadPrinciples = Array.from(selectedPrinciples.entries()).map(([id, rank]) => ({
			principle_id: id,
			rank: rank
		}));

		const payload = {
			principles: payloadPrinciples
		};

		console.log('Principles Payload:', JSON.stringify(payload, null, 2));

		try {
			const token = localStorage.getItem('accessToken');
			const response = await fetch('http://localhost:8000/api/onboarding/principles', {
				method: 'POST',
				headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
				body: JSON.stringify(payload)
			});

			if (response.ok) {
				console.log('User principles saved.');
				alert('Onboarding complete!');
				// Optionally update user onboarding status here or on backend
				goto('/'); // Go to the main dashboard
			} else {
				const errorResult = await response.json();
				alert(`Error saving principles: ${errorResult.detail || 'Unknown error'}`);
				console.error('Principle save error:', errorResult);
			}
		} catch (error) {
			alert('Network error saving principles.');
			console.error('Network error:', error);
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
				<button type="submit">Complete Onboarding</button>
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
	button {
		width: 100%;
		padding: 10px;
		background-color: #5cb85c;
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		font-size: 1rem;
		margin-top: 1.5rem;
	}
	button:hover {
		background-color: #4cae4c;
	}
</style>