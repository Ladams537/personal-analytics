<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte'; // Import onMount if not already there

	let email = '';
	let password = '';
	let errorMessage = ''; // To display errors on the page

	// Optional: Check if user is already logged in on page load
	onMount(() => {
		const token = localStorage.getItem('accessToken');
		if (token) {
			// Optional: Verify token validity here if needed
			console.log('User already logged in, redirecting...');
			goto('/'); // Redirect to dashboard if already logged in
		}
	});

	async function handleSubmit() {
		errorMessage = ''; // Clear previous errors
		const credentials = { email, password };

		try {
			const response = await fetch('http://localhost:8000/api/login', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(credentials)
			});

			if (response.ok) {
				const result = await response.json();
				console.log('Login Success:', result);

				// --- STORE THE TOKEN ---
				if (result.access_token) {
					localStorage.setItem('accessToken', result.access_token);
					console.log('Token stored in localStorage');
					alert('Login successful!');
					goto('/'); // Redirect to the dashboard
				} else {
					console.error('Token not found in response');
					errorMessage = 'Login succeeded but token was missing.';
				}
				// -----------------------

			} else {
				let errorMsg = 'Login failed.';
				try {
					const errorResult = await response.json();
					errorMsg = errorResult.detail || JSON.stringify(errorResult);
				} catch (parseError) {
					errorMsg = await response.text() || `HTTP Error ${response.status}`;
				}
				console.error('Login Error:', errorMsg);
				errorMessage = `Login failed: ${errorMsg}`; // Show error on page
				// alert(`Login failed: ${errorMsg}`); // Can remove alert if showing on page
			}
		} catch (error) {
			console.error('Network error:', error);
			errorMessage = 'A network error occurred. Please try again.';
			// alert('A network error occurred. Please try again.'); // Can remove alert
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

		<button type="submit">Login</button>
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