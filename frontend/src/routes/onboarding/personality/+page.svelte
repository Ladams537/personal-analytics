<script lang="ts">
	import { goto } from '$app/navigation';

	// Define the structure for Myers-Briggs traits
	let traits = [
		{ scale: 'Mind', name1: 'Introverted', name2: 'Extraverted', value: 50, order: 1 }, // value represents % Introverted
		{ scale: 'Energy', name1: 'Intuitive', name2: 'Observant', value: 50, order: 2 }, // value represents % Intuitive
		{ scale: 'Nature', name1: 'Feeling', name2: 'Thinking', value: 50, order: 3 }, // value represents % Feeling
		{ scale: 'Tactics', name1: 'Judging', name2: 'Prospecting', value: 50, order: 4 }, // value represents % Judging
		{ scale: 'Identity', name1: 'Turbulent', name2: 'Assertive', value: 50, order: 5 } // value represents % Turbulent
	];

	async function handleSubmit() {
		console.log('Submitting personality traits...');

		// Prepare data for the backend
		const payloadTraits = traits.map((t) => ({
			scale_name: t.scale,
			// Determine the trait name based on the percentage value
			trait_name: t.value >= 50 ? t.name1 : t.name2,
			// Send the dominant percentage (e.g., if 70% Introverted, send 70; if 30% Introverted -> 70% Extraverted, send 70)
			value: t.value >= 50 ? t.value : 100 - t.value,
			display_order: t.order
		}));

		const payload = {
			traits: payloadTraits
		};

		console.log('Personality Payload:', JSON.stringify(payload, null, 2));

		try {
			const token = localStorage.getItem('accessToken');
			if (!token) {
				goto('/login');
				return;
			}
			const response = await fetch('http://localhost:8000/api/onboarding/personality', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
				body: JSON.stringify(payload)
			});

			if (response.ok) {
				console.log('Personality traits saved.');
				goto('/onboarding/principles'); // Go to the next step
			} else {
				const errorResult = await response.json();
				alert(`Error saving personality: ${errorResult.detail || 'Unknown error'}`);
				console.error('Personality save error:', errorResult);
			}
		} catch (error) {
			alert('Network error saving personality.');
			console.error('Network error:', error);
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

		<button type="submit">Next: Select Principles</button>
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
	button {
		width: 100%;
		padding: 10px;
		background-color: #007bff;
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		font-size: 1rem;
		margin-top: 1rem;
	}
	button:hover {
		background-color: #0056b3;
	}
</style>