<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import Button from '$lib/components/atomic/Button.svelte';
	import { api } from '$lib/services/api';

	let email = '';
	let password = '';
	let errorMessage = '';
	let isLoading = false;

	onMount(() => {
		const token = localStorage.getItem('accessToken');
		if (token) {
			goto('/'); // Redirect to dashboard if already logged in
		}
	});

	async function handleSubmit() {
		errorMessage = '';
		isLoading = true;
		const credentials = { email, password };

		try {
			// Use the new api.post function
			const result = await api.post('/api/login', credentials);
			console.log('Login Success:', result);

			if (result.access_token) {
				localStorage.setItem('accessToken', result.access_token);
				console.log('Token stored in localStorage');

				// Redirect based on onboarding status
				if (result.onboarding_complete) {
					goto('/'); // Redirect to the dashboard
				} else {
					goto('/onboarding/personality');
				}
			} else {
				errorMessage = 'Login succeeded but token was missing.';
			}
		} catch (error: any) {
			console.error('Login Error:', error);
			errorMessage = `Login failed: ${error.message}`;
		} finally {
			isLoading = false;
		}
	}
</script>

<main>
    <h1>Login</h1>
	<form on:submit|preventDefault={handleSubmit}>
		<div>
			<label for="email">Email</label>
			<input type="email" id="email" bind:value={email} required />
		</div>
		<div>
			<label for="password">Password</label>
			<input type="password" id="password" bind:value={password} required />
		</div>

		{#if errorMessage}
			<p class="error">{errorMessage}</p>
		{/if}

		<Button type="submit" fullWidth={true}>Login</Button>
	</form>
	<p>Don't have an account? <a href="/register">Register here</a></p>
</main>

<style>
    /* You can reuse the styles from your register page */
    main { max-width: 400px; margin: 2rem auto; text-align: center; }
    div { margin-bottom: 1rem; text-align: left; }
    label { display: block; }
    input { width: 100%; padding: 8px; box-sizing: border-box; }
    .error {
		color: red;
		margin-top: 1rem;
	}
	p { /* Style for the register link */
		margin-top: 1rem;
	}
	a {
		color: #007bff;
		text-decoration: none;
	}
	a:hover {
		text-decoration: underline;
	}
</style>