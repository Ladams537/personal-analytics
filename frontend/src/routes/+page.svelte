<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import Button from '$lib/components/atomic/Button.svelte';
	import Card from '$lib/components/atomic/Card.svelte';
	import { api } from '$lib/services/api'; // <-- IMPORT YOUR NEW API SERVICE

	let dashboardData: any = null;
	let isLoading = true;
	let errorMessage = '';

	onMount(async () => {
		isLoading = true;
		errorMessage = '';
		try {
			// --- THIS IS THE NEW, CLEANER FETCH ---
			dashboardData = await api.get('/api/dashboard');
			console.log('Dashboard Data:', dashboardData);
			// --- ALL ERROR HANDLING (401, etc.) IS NOW IN THE SERVICE ---
		} catch (error: any) {
			errorMessage = error.message || 'Failed to load dashboard data.';
		} finally {
			isLoading = false;
		}
	});

	async function updateGoalStatus(event: Event) {
		if (!dashboardData?.top_goal) return;
		
		const target = event.target as HTMLInputElement;
		const newStatus = target.checked;
		const originalStatus = dashboardData.top_goal.is_completed;
		
		dashboardData.top_goal.is_completed = newStatus; // Optimistic update
		dashboardData = dashboardData;

		try {
			// --- NEW, CLEANER PATCH REQUEST ---
			await api.patch('/api/goals/today', { is_completed: newStatus });
			console.log('Goal status updated successfully.');
			errorMessage = '';
		} catch (error: any) {
			// Revert optimistic update on error
			dashboardData.top_goal.is_completed = originalStatus;
			dashboardData = dashboardData;
			errorMessage = `Failed to update goal: ${error.message}`;
			alert(errorMessage);
		}
	}

	// Helper function (no change)
	function getMetricsByType(type: string) {
		if (!dashboardData || !dashboardData.daily_metrics) return [];
		return dashboardData.daily_metrics.filter((m: any) => m.metric_type === type);
	}

	// Logout function (no change)
	function logout() {
		localStorage.removeItem('accessToken');
		console.log('Token removed, logging out.');
		goto('/login');
	}
</script>

<main>
	<h1>Your Dashboard</h1>
	<Button type="button" variant="danger" onclick={logout}>Logout</Button> 
	{#if isLoading}
		<p>Loading...</p>
	{:else if errorMessage}
		<p class="error">{errorMessage}</p>
	{:else if dashboardData}
		{#if dashboardData.latest_insight}
            <Card>
                {#snippet header()}
                    <h2>💡 Daily Tidbit</h2>
                {/snippet}
                <p class="insight-content">"{dashboardData.latest_insight.content}"</p>
                </Card>
        {/if}
		
		<Card>
			{#snippet header()}
				<h2>Today's Top Goal</h2>
			{/snippet}

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
		</Card>

		<Card>
			{#snippet header()}
				<h2>Latest Gratitude Entry</h2>
			{/snippet}

			{#if dashboardData.latest_checkin && dashboardData.latest_checkin.gratitude_entry}
				<p>"{dashboardData.latest_checkin.gratitude_entry}"</p>
				<small>From: {dashboardData.latest_checkin.checkin_date}</small>
			{:else if dashboardData.latest_checkin}
				<p>No gratitude entry for {dashboardData.latest_checkin.checkin_date}.</p>
			{:else}
				<p>No check-in data found yet.</p>
			{/if}
		</Card>

		<Card>
			{#snippet header()}
				<h2>Latest Principle Alignment</h2>
			{/snippet}

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
		</Card>

        <Card>
			{#snippet header()}
				<h2>Latest Time Allocation</h2>
			{/snippet}

			{#if dashboardData.latest_checkin}
				<ul>
					{#each getMetricsByType('Time Allocation') as metric (metric.metric_name)}
						<li>{metric.metric_name}: {metric.value}%</li>
					{:else}
						<li>No time allocation data recorded for this day.</li>
					{/each}
				</ul>
				<small>From: {dashboardData.latest_checkin.checkin_date}</small>
			{:else}
				<p>No check-in data found yet.</p>
			{/if}
		</Card>

		<Card>
			{#snippet header()}
				<h2>Latest Daily Ratings</h2>
			{/snippet}

			{#if dashboardData.latest_checkin}
				<ul>
					{#each getMetricsByType('Daily Rating') as rating (rating.metric_name)}
						<li>{rating.metric_name}: {rating.value} / 10</li>
					{:else}
						<li>No daily ratings recorded for this day.</li>
					{/each}
				</ul>
				<small>From: {dashboardData.latest_checkin.checkin_date}</small>
			{:else}
				<p>No check-in data found yet.</p>
			{/if}
		</Card>
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
	.insight-content {
        font-style: italic;
        font-size: 1.1em;
        line-height: 1.6;
        color: #333;
    }
</style>