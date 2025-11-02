<script lang="ts">
	import { goto } from '$app/navigation';
	import Button from '$lib/components/atomic/Button.svelte';
	import { api } from '$lib/services/api';

	let displayName = '';
	let email = '';
	let password = '';
	let errorMessage = '';
	let isLoading = false;

	async function handleSubmit() {
		errorMessage = '';
		isLoading = true;
		const userData = {
			display_name: displayName,
			email: email,
			password: password
		};

		try {
			// Use the new api.post function
			const result = await api.post('/api/users', userData);
			console.log('Success:', result);

			if (result.access_token) {
				// 1. Store the new token
				localStorage.setItem('accessToken', result.access_token);
				console.log('Token stored in localStorage');
				
				// 2. Redirect to onboarding
				goto('/onboarding/personality');
			} else {
				errorMessage = 'Registration succeeded but no token was returned.';
			}
		} catch (error: any) {
			// Errors (including 401, 500, etc.) are now caught here
			console.error('Registration error:', error);
			errorMessage = error.message || 'Failed to create user.';
		} finally {
			isLoading = false;
		}
	}
</script>

<main>
    <h1>Create an Account</h1>
    <form on:submit|preventDefault={handleSubmit}>
        {#if errorMessage}
            <p class="error">{errorMessage}</p>
        {/if}

        <div>
            <label for="displayName">Display Name</label>
            <input type="text" id="displayName" bind:value={displayName} required />
        </div>
        <div>
            <label for="email">Email</label>
            <input type="email" id="email" bind:value={email} required />
        </div>
        <div>
            <label for="password">Password</label>
            <input type="password" id="password" bind:value={password} required />
        </div>
        <Button type="submit" fullWidth={true}>Register</Button>
    </form>
    <p>Already have an account? <a href="/login">Login here</a></p>
</main>

<style>
    main {
        max-width: 400px;
        margin: 2rem auto;
        text-align: center;
    }
    div {
        margin-bottom: 1rem;
        text-align: left;
    }
    label {
        display: block;
    }
    input {
        width: 100%;
        padding: 8px;
        box-sizing: border-box;
    }
    .error {
        color: red;
        margin-top: 1rem;
    }
    p {
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