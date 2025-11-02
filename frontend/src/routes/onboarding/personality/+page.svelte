<script lang="ts">
	import { goto } from '$app/navigation';
	import Button from '$lib/components/atomic/Button.svelte';
	import { api } from '$lib/services/api';

	let traits = [
		{ scale: 'Mind', name1: 'Introverted', name2: 'Extraverted', value: 50, order: 1 },
		{ scale: 'Energy', name1: 'Intuitive', name2: 'Observant', value: 50, order: 2 },
		{ scale: 'Nature', name1: 'Feeling', name2: 'Thinking', value: 50, order: 3 },
		{ scale: 'Tactics', name1: 'Judging', name2: 'Prospecting', value: 50, order: 4 },
		{ scale: 'Identity', name1: 'Turbulent', name2: 'Assertive', value: 50, order: 5 }
	];

	let errorMessage = '';
	let isLoading = false;

	async function handleSubmit() {
		console.log('Submitting personality traits...');
		isLoading = true;
		errorMessage = '';

		const payloadTraits = traits.map((t) => ({
			scale_name: t.scale,
			trait_name: t.value >= 50 ? t.name1 : t.name2,
			value: t.value >= 50 ? t.value : 100 - t.value,
			display_order: t.order
		}));

		// We no longer send user_id, the token handles it
		const payload = {
			traits: payloadTraits
		};

		try {
			// Use the new api.put function
			await api.put('/api/settings/personality', payload);
			console.log('Personality traits saved.');
			goto('/onboarding/principles'); // Go to the next step
		} catch (error: any) {
			errorMessage = `Error saving personality: ${error.message}`;
			console.error('Personality save error:', error);
		} finally {
			isLoading = false;
		}
	}
</script>

<main>
	<h1>Onboarding: Your Personality</h1>
	<p>Enter your Myers-Briggs percentages (if unsure, estimate or use 50%).</p>

	<form on:submit|preventDefault={handleSubmit}>
		{#each traits as trait, i}
			<div class="trait-slider">
				<label for="trait-{i}">{trait.name1} vs {trait.name2}</label>
				<input type="range" id="trait-{i}" bind:value={trait.value} min="0" max="100" step="1" />
				<span>{trait.value}% {trait.name1} / {100 - trait.value}% {trait.name2}</span>
			</div>
		{/each}

		<Button type="submit" fullWidth={true}>Next: Select Principles</Button>
	</form>
</main>

<style>
	main {
		max-width: 500px;
		margin: 2rem auto;
		padding: 1.5rem;
		border: 1px solid #ddd;
		border-radius: 8px;
	}
	.trait-slider {
		margin-bottom: 1.5rem;
	}
	label {
		display: block;
		font-weight: bold;
		margin-bottom: 0.5rem;
	}
	input[type='range'] {
		width: 100%;
	}
	span {
		display: block;
		text-align: center;
		margin-top: 0.3rem;
		font-size: 0.9em;
		color: #555;
	}
</style>