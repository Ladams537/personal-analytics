<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import Button from '$lib/components/atomic/Button.svelte';
	import Card from '$lib/components/atomic/Card.svelte';

	// --- Types ---
	type Reflection = {
		reflection_id: string;
		user_id: string;
		title: string;
		body: string;
		created_at: string;
	};

	// --- State ---
	let reflections: Reflection[] = [];
	let isLoading = true;
	let errorMessage = '';

	// --- Form State ---
	let newTitle = '';
	let newBody = '';
	let isSubmitting = false;

	// --- Data Loading ---
	onMount(async () => {
		await fetchReflections();
	});

	async function fetchReflections() {
		isLoading = true;
		errorMessage = '';
		const token = localStorage.getItem('accessToken');
		if (!token) {
			goto('/login');
			return;
		}

		try {
			const response = await fetch('http://localhost:8000/api/reflections', {
				headers: { Authorization: `Bearer ${token}` }
			});

			if (response.ok) {
				reflections = await response.json();
				console.log('Fetched reflections:', reflections);
			} else if (response.status === 401) {
				goto('/login');
			} else {
				const err = await response.json();
				errorMessage = err.detail || 'Failed to load reflections.';
			}
		} catch (error) {
			errorMessage = 'Network error. Please try again.';
		} finally {
			isLoading = false;
		}
	}

	// --- Form Submission ---
	async function handleSubmit() {
		if (!newTitle.trim() || !newBody.trim()) {
			errorMessage = 'Title and body cannot be empty.';
			return;
		}
		isSubmitting = true;
		errorMessage = '';

		const token = localStorage.getItem('accessToken');
		if (!token) {
			goto('/login');
			return;
		}

		try {
			const response = await fetch('http://localhost:8000/api/reflections', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${token}`
				},
				body: JSON.stringify({
					title: newTitle,
					body: newBody
				})
			});

			if (response.status === 201) {
				const newReflection = await response.json();
				// Add the new reflection to the top of the list
				reflections = [newReflection, ...reflections];
				// Clear the form
				newTitle = '';
				newBody = '';
			} else {
				const err = await response.json();
				errorMessage = err.detail || 'Failed to save reflection.';
			}
		} catch (error) {
			errorMessage = 'Network error. Please try again.';
		} finally {
			isSubmitting = false;
		}
	}

	// Helper to format dates
	function formatDate(dateString: string) {
		return new Date(dateString).toLocaleString('en-US', {
			dateStyle: 'medium',
			timeStyle: 'short'
		});
	}
</script>

<main>
	<h1>Reflections</h1>
	<p>A place for fleeting thoughts and brief reflections.</p>

	<Card>
		{#snippet header()}
			<h2>New Reflection</h2>
		{/snippet}
		<form on:submit|preventDefault={handleSubmit}>
			<div class="form-group">
				<label for="title">Title</label>
				<input
					id="title"
					type="text"
					bind:value={newTitle}
					placeholder="e.g., 'Idea for work'"
					required
					disabled={isSubmitting}
				/>
			</div>
			<div class="form-group">
				<label for="body">Body</label>
				<textarea
					id="body"
					bind:value={newBody}
					placeholder="What's on your mind?"
					rows="3"
					required
					disabled={isSubmitting}
				></textarea>
			</div>
			{#if errorMessage}
				<p class="error">{errorMessage}</p>
			{/if}
			<Button type="submit" loading={isSubmitting} fullWidth={true}>Save Reflection</Button>
		</form>
	</Card>

	<section class="reflection-list">
		<h2>Past Entries</h2>
		{#if isLoading}
			<p>Loading reflections...</p>
		{:else if reflections.length === 0}
			<p>You haven't saved any reflections yet.</p>
		{:else}
			{#each reflections as reflection (reflection.reflection_id)}
				<Card>
					{#snippet header()}
						<h3>{reflection.title}</h3>
					{/snippet}
					<p class="reflection-body">{reflection.body}</p>
					<small class="timestamp">{formatDate(reflection.created_at)}</small>
				</Card>
			{/each}
		{/if}
	</section>
</main>

<style>
	main {
		max-width: 700px;
		margin: 2rem auto;
		padding: 1rem;
	}
	h1,
	h2 {
		text-align: center;
	}
	.form-group {
		margin-bottom: 1rem;
	}
	.form-group label {
		display: block;
		font-weight: bold;
		margin-bottom: 0.5rem;
	}
	input,
	textarea {
		width: 100%;
		padding: 8px;
		box-sizing: border-box;
		border: 1px solid #ccc;
		border-radius: 4px;
	}
	.reflection-list {
		margin-top: 2rem;
	}
	.reflection-list :global(.card) {
		margin-bottom: 1rem;
	}
	.reflection-body {
		white-space: pre-wrap; /* Preserves line breaks in the text */
		font-size: 1rem;
		line-height: 1.6;
	}
	.timestamp {
		display: block;
		text-align: right;
		font-style: italic;
		color: #777;
		font-size: 0.9em;
		margin-top: 1rem;
	}
	.error {
		color: red;
		text-align: center;
		margin-bottom: 1rem;
	}
</style>