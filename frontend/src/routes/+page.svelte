<script lang="ts">
	import { onMount } from 'svelte';
	import Card from '$lib/components/atomic/Card.svelte';
	import LineChart from '$lib/components/charts/LineChart.svelte';
	import DoughnutChart from '$lib/components/charts/DoughnutChart.svelte';
	import BarChart from '$lib/components/charts/BarChart.svelte';
	import { api } from '$lib/services/api';

	let dashboardData: any = null;
	let isLoading = true;
	let errorMessage = '';
	let alignmentChartData: any = null;
	let timeChartData: any = null;
	let dailyRatingChartData: any = null;

	onMount(async () => {
		isLoading = true;
		errorMessage = '';
		try {
			// --- THIS IS THE NEW, CLEANER FETCH ---
			dashboardData = await api.get('/api/dashboard');
			console.log('Dashboard Data:', dashboardData);
			// --- ALL ERROR HANDLING (401, etc.) IS NOW IN THE SERVICE ---
			const chartData = await api.get('/api/charts/principle-alignment');
			console.log('Chart Data:', chartData);

			// Format the data for Chart.js
			alignmentChartData = {
				labels: chartData.labels, // The dates
				datasets: [
					{
						label: 'Principle Alignment',
						data: chartData.data, // The scores
						fill: false,
						borderColor: 'rgb(75, 192, 192)',
						tension: 0.1
					}
				]
			};

			// --- 3. Format data for Time Allocation Chart ---
			if (dashboardData?.daily_metrics) {
				const timeMetrics = getMetricsByType('Time Allocation');
				if (timeMetrics.length > 0) {
					timeChartData = {
						labels: timeMetrics.map((m: any) => m.metric_name), // e.g., ['Work', 'Family', ...]
						datasets: [
							{
								label: 'Time Allocation',
								data: timeMetrics.map((m: any) => m.value), // e.g., [50, 10, ...]
								backgroundColor: [
									'rgba(255, 99, 132, 0.8)',
									'rgba(54, 162, 235, 0.8)',
									'rgba(255, 206, 86, 0.8)',
									'rgba(75, 192, 192, 0.8)',
									'rgba(153, 102, 255, 0.8)',
									'rgba(255, 159, 64, 0.8)'
								],
								hoverOffset: 4
							}
						]
					};
				}
			}
			// --- NEW: Daily Ratings (Bar) ---
				const ratingMetrics = getMetricsByType('Daily Rating');
				if (ratingMetrics.length > 0) {
					dailyRatingChartData = {
						labels: ratingMetrics.map((r: any) => r.metric_name), // e.g., ['Productivity', 'Focus', 'Fun']
						datasets: [
							{
								label: 'Rating (1-10)',
								data: ratingMetrics.map((r: any) => r.value), // e.g., [8, 7, 5]
								backgroundColor: [
									'rgba(75, 192, 192, 0.7)',
									'rgba(153, 102, 255, 0.7)',
									'rgba(255, 159, 64, 0.7)'
								],
								borderColor: [
									'rgb(75, 192, 192)',
									'rgb(153, 102, 255)',
									'rgb(255, 159, 64)'
								],
								borderWidth: 1
							}
						]
					};
				}
			// ------------------------------------------------
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
</script>

<main>
	<h1>Your Dashboard</h1>
	{#if isLoading}
		<p>Loading...</p>
	{:else if errorMessage}
		<p class="error">{errorMessage}</p>
	{:else if dashboardData}
		<Card>
			{#snippet header()}
				<h2>Principle Alignment (Last 60 Days)</h2>
			{/snippet}

			{#if alignmentChartData}
				<LineChart chartData={alignmentChartData} />
			{:else}
				<p>Not enough data to display chart.</p>
			{/if}
		</Card>

		<Card>
			{#snippet header()}
				<h2>Latest Time Allocation</h2>
			{/snippet}
			{#if timeChartData}
				<DoughnutChart chartData={timeChartData} />
			{:else if dashboardData.latest_checkin}
				<p>No time allocation data recorded for this day.</p>
			{:else}
				<p>No check-in data found yet.</p>
			{/if}
		</Card>

		<Card>
			{#snippet header()}
				<h2>Latest Daily Ratings</h2>
			{/snippet}
			{#if dailyRatingChartData}
				<BarChart chartData={dailyRatingChartData} />
			{:else if dashboardData.latest_checkin}
				<p>No daily ratings recorded for this day.</p>
			{:else}
				<p>No check-in data found yet.</p>
			{/if}
		</Card>

		<!-- {#if dashboardData.latest_insight}
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
		</Card> -->

		<Card>
			{#snippet header()}
				<h2>A Past Gratitude</h2>
			{/snippet}

			{#if dashboardData.random_gratitude}
				<p>"{dashboardData.random_gratitude.gratitude_entry}"</p>
				<small>From: {dashboardData.random_gratitude.checkin_date}</small>
			{:else}
				<p>No gratitude entries found yet. Add one in your next check-in!</p>
			{/if}
		</Card> 

		<!-- <Card>
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
		</Card> -->
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