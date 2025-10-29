<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let dashboardData: any = null; // To store the fetched data
	let isLoading = true;
	let errorMessage = '';

	onMount(async () => {
		isLoading = true;
		errorMessage = '';

		// --- Get the token from localStorage ---
		const token = localStorage.getItem('accessToken');

		if (!token) {
			// If no token, redirect to login
			console.log('No token found, redirecting to login.');
			goto('/login');
			return; // Stop execution
		}
		// ------------------------------------

		try {
			// --- Include the token in the fetch request ---
			const response = await fetch('http://localhost:8000/api', { // Removed user ID from URL
				method: 'GET',
				headers: {
					// Add the Authorization header
					'Authorization': `Bearer ${token}`
				}
			});
			// ------------------------------------------

			if (response.ok) {
				dashboardData = await response.json();
				console.log('Dashboard Data:', dashboardData);
			} else if (response.status === 401) {
				// Handle unauthorized error (e.g., expired token)
				errorMessage = 'Your session has expired. Please log in again.';
				console.error('Authorization failed (401)');
				// Optional: Clear the invalid token
				localStorage.removeItem('accessToken');
				// Redirect to login after a short delay
				setTimeout(() => goto('/login'), 2000);
			} else {
				// Handle other server errors
				const errorResult = await response.json();
				errorMessage = errorResult.detail || 'Failed to load dashboard data.';
				console.error('Error fetching dashboard:', response.status, errorResult);
			}
		} catch (error) {
			errorMessage = 'A network error occurred while loading dashboard data.';
			console.error('Network error:', error);
		} finally {
			isLoading = false;
		}
	});

	// --- NEW: Function to update goal status ---
	async function updateGoalStatus(event: Event) {
		if (!dashboardData?.top_goal) return; // Should not happen if checkbox is shown

		const target = event.target as HTMLInputElement;
		const newStatus = target.checked;
		const originalStatus = dashboardData.top_goal.is_completed; // Store original status

		// Optimistically update UI
		dashboardData.top_goal.is_completed = newStatus;
        dashboardData = dashboardData; // Trigger Svelte reactivity

		const token = localStorage.getItem('accessToken');
		if (!token) {
			errorMessage = 'Not logged in.';
			goto('/login');
			return;
		}

		console.log(`Attempting to update goal status to: ${newStatus}`);

		try {
			const response = await fetch('http://localhost:8000/api/goals/today', {
				method: 'PATCH',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${token}`
				},
				body: JSON.stringify({ is_completed: newStatus })
			});

			if (!response.ok) {
				// Revert optimistic update on error
				dashboardData.top_goal.is_completed = originalStatus;
                dashboardData = dashboardData; // Trigger reactivity
                const errorResult = await response.json();
                errorMessage = `Failed to update goal: ${errorResult.detail || response.statusText}`;
				console.error('Goal update error:', errorResult);
                alert(errorMessage); // Notify user
			} else {
                console.log('Goal status updated successfully on backend.');
                errorMessage = ''; // Clear any previous errors
            }
		} catch (error) {
            // Revert optimistic update on network error
            dashboardData.top_goal.is_completed = originalStatus;
            dashboardData = dashboardData; // Trigger reactivity
			errorMessage = 'Network error updating goal status.';
			console.error('Network error:', error);
            alert(errorMessage); // Notify user
		}
	}

    // Helper function to filter metrics by type (optional but clean)
	function getMetricsByType(type: string) {
		if (!dashboardData || !dashboardData.daily_metrics) return [];
		return dashboardData.daily_metrics.filter((m: any) => m.metric_type === type);
	}

	// --- NEW: Logout Function ---
	function logout() { 
		localStorage.removeItem('accessToken');
		console.log('Token removed, logging out.');
		goto('/login');
	}
</script>

<main>
	<h1>Your Dashboard</h1>

	<button on:click={logout} class="logout-button">Logout</button> {#if isLoading}
		<p>Loading...</p>
	{:else if errorMessage}
		<p class="error">{errorMessage}</p>
	{:else if dashboardData}
		<section class="widget">
			<h2>Today's Top Goal</h2>
			{#if dashboardData.top_goal}
				<p>{dashboardData.top_goal.goal_description}</p>
				<label class="goal-status">
					<input
						type="checkbox"
						checked={dashboardData.top_goal.is_completed}
						on:change={updateGoalStatus}
					/>
					{dashboardData.top_goal.is_completed ? '✅ Completed' : '⏳ Pending'}
				</label>
			{:else}
				<p>No top goal set for today.</p>
			{/if}
		</section>

		<section class="widget">
			<h2>Latest Gratitude Entry</h2>
			{#if dashboardData.latest_checkin && dashboardData.latest_checkin.gratitude_entry}
				<p>"{dashboardData.latest_checkin.gratitude_entry}"</p>
				<small>From: {dashboardData.latest_checkin.checkin_date}</small>
			{:else if dashboardData.latest_checkin}
				<p>No gratitude entry for {dashboardData.latest_checkin.checkin_date}.</p>
			{:else}
				<p>No check-in data found yet.</p>
			{/if}
		</section>

		<section class="widget">
			<h2>Latest Principle Alignment</h2>
			{#if dashboardData.latest_checkin && dashboardData.latest_checkin.principle_alignment}
				<p>Rating: {dashboardData.latest_checkin.principle_alignment} / 10</p>
				{#if dashboardData.latest_checkin.principle_alignment_note}
					<p>Note: "{dashboardData.latest_checkin.principle_alignment_note}"</p>
				{/if}
				<small>From: {dashboardData.latest_checkin.checkin_date}</small>
			{:else if dashboardData.latest_checkin}
				<p>No alignment rating for {dashboardData.latest_checkin.checkin_date}.</p>
			{:else}
				<p>No check-in data found yet.</p>
			{/if}
		</section>

        <section class="widget">
			<h2>Latest Time Allocation</h2>
			{#if dashboardData.latest_checkin}
				<small>From: {dashboardData.latest_checkin.checkin_date}</small>
				<ul>
					{#each getMetricsByType('Time Allocation') as metric (metric.metric_name)}
						<li>{metric.metric_name}: {metric.value}%</li>
					{:else}
						<li>No time allocation data recorded for this day.</li>
					{/each}
				</ul>
			{:else}
				<p>No check-in data found yet.</p>
			{/if}
		</section>

		<section class="widget">
			<h2>Latest Daily Ratings</h2>
			{#if dashboardData.latest_checkin}
				<small>From: {dashboardData.latest_checkin.checkin_date}</small>
				<ul>
					{#each getMetricsByType('Daily Rating') as rating (rating.metric_name)}
						<li>{rating.metric_name}: {rating.value} / 10</li>
					{:else}
						<li>No daily ratings recorded for this day.</li>
					{/each}
				</ul>
			{:else}
				<p>No check-in data found yet.</p>
			{/if}
		</section>
	{:else}
		<p>No dashboard data available.</p>
	{/if}

	<a href="/checkin" class="checkin-link">Go to Daily Check-in</a>
</main>

<style>
	main {
		max-width: 800px;
		margin: 2rem auto;
		padding: 1rem;
	}
	h1 {
		text-align: center;
		margin-bottom: 2rem;
	}
	.widget {
		background-color: #f9f9f9;
		border: 1px solid #eee;
		border-radius: 8px;
		padding: 1.5rem;
		margin-bottom: 1.5rem;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
	}
	.widget h2 {
		margin-top: 0;
		margin-bottom: 1rem;
		color: #555;
		border-bottom: 1px solid #eee;
		padding-bottom: 0.5rem;
	}
	.widget p {
		margin-bottom: 0.5rem;
		line-height: 1.6;
	}
	.widget small {
		color: #888;
		font-style: italic;
	}
	.checkin-link {
		display: block;
		text-align: center;
		margin-top: 2rem;
		padding: 10px 15px;
		background-color: #007bff;
		color: white;
		text-decoration: none;
		border-radius: 4px;
	}
	.checkin-link:hover {
		background-color: #0056b3;
	}

    ul {
		list-style: none;
		padding-left: 0;
	}
	li {
		padding: 0.3rem 0;
	}
	.error { 
		color: red;
		text-align: center;
		margin-top: 1rem;
	}
    .logout-button { 
        position: absolute;
        top: 1rem;
        right: 1rem;
        padding: 8px 12px;
        background-color: #dc3545;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
    .logout-button:hover {
        background-color: #c82333;
    }
	.goal-status {
		display: inline-flex;
		align-items: center;
		cursor: pointer;
		font-size: 1rem;
	}
    .goal-status input[type="checkbox"] {
        margin-right: 0.5rem;
        width: 1.2em;
        height: 1.2em;
    }
</style>