<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { onMount } from 'svelte';

	import type { Snippet } from 'svelte';

	// Get the 'children' snippet, which is the page content
	const { children } = $props<{ children: Snippet }>();

	let token: string | null = null;
	let currentPath = $state(page); 

	// Check for token on mount
	onMount(() => {
		token = localStorage.getItem('accessToken');
		// We don't need to redirect here; individual pages can handle that.
		// This just determines if we show the sidebar.
	});

	// A $effect to update the currentPath when the page changes
	$effect(() => {
		currentPath = page;
	});

	function logout() {
		localStorage.removeItem('accessToken');
		token = null;
		goto('/login');
	}
</script>

<div class="app-layout">
	{#if !currentPath.url.pathname.startsWith('/login') && !currentPath.url.pathname.startsWith('/register')}
		<nav class="sidebar">
			<div class="sidebar-header">
				<h2>My App</h2>
			</div>
			<ul class="nav-links">
				<li>
					<a href="/" class:active={currentPath.url.pathname.startsWith('/')}>Dashboard</a>
				</li>
				<li>
					<a href="/checkin" class:active={currentPath.url.pathname.startsWith('/checkin')}>Check-in</a>
				</li>
				<li>
					<a href="/journal" class:active={currentPath.url.pathname.startsWith('/journal')}>Journal</a>
				</li>
				<li>
					<a href="/routines" class:active={currentPath.url.pathname.startsWith('/routines')}>Routines</a>
				</li>
				<li>
					<a href="/settings" class:active={currentPath.url.pathname.startsWith('/settings')}>Settings</a>
				</li>
			</ul>
			<div class="sidebar-footer">
				<button onclick={logout} class="logout-btn">Logout</button>
			</div>
		</nav>
	{/if}

	<main class="main-content">
		{@render children()}
	</main>
</div>

<style>
	/* A simple global reset for consistency */
	:global(body) {
		margin: 0;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
		background-color: #f4f7f6;
		color: #333;
	}

	.app-layout {
		display: flex;
		height: 100vh;
	}

	.sidebar {
		width: 240px;
		background-color: #ffffff;
		border-right: 1px solid #e0e0e0;
		display: flex;
		flex-direction: column;
		box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
	}

	.sidebar-header {
		padding: 1.5rem 1.25rem;
		text-align: center;
		border-bottom: 1px solid #eee;
	}

	.sidebar-header h2 {
		margin: 0;
		font-size: 1.5rem;
		color: #007bff;
	}

	.nav-links {
		list-style: none;
		padding: 0;
		margin: 1rem 0;
		flex-grow: 1; /* Pushes the footer down */
	}

	.nav-links a {
		display: block;
		padding: 1rem 1.5rem;
		text-decoration: none;
		color: #555;
		font-weight: 500;
		transition:
			background-color 0.2s ease,
			color 0.2s ease;
	}

	.nav-links a:hover {
		background-color: #f4f7f6;
	}

	.nav-links a.active {
		background-color: #007bff;
		color: white;
		border-right: 3px solid #0056b3;
	}

	.sidebar-footer {
		padding: 1.5rem;
		border-top: 1px solid #eee;
	}

	.logout-btn {
		/* Re-using your button styles, but simplified for layout */
		width: 100%;
		padding: 10px 15px;
		background-color: #dc3545;
		color: white;
		border: none;
		border-radius: 4px;
		font-size: 1rem;
		cursor: pointer;
	}
	.logout-btn:hover {
		background-color: #c82333;
	}

	.main-content {
		flex-grow: 1; /* Takes up the remaining space */
		overflow-y: auto; /* Allows content to scroll */
		padding: 2rem;
		height: 100vh;
		box-sizing: border-box; /* Ensures padding is included in height */
	}

	/* Cleanup: Remove any full-page margin from your individual pages */
	:global(main) {
		margin: 0; /* Reset margins from individual pages */
		max-width: 100%;
	}
</style>