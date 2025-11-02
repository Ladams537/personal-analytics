<script lang="ts">
	import { onMount } from 'svelte';
	import type { ChartData, ChartOptions } from 'chart.js';
	import { Chart } from 'chart.js'; // We already registered components in LineChart.svelte

	// Define the props
	type Props = {
		chartData: ChartData<'doughnut'>;
	};
	const { chartData } = $props<Props>();

	let canvas: HTMLCanvasElement; // The <canvas> element
	let chart: Chart; // The Chart.js instance

	onMount(() => {
		const ctx = canvas.getContext('2d');
		if (ctx) {
			chart = new Chart(ctx, {
				type: 'doughnut',
				data: chartData,
				options: {
					responsive: true,
					maintainAspectRatio: false,
					plugins: {
						legend: {
							position: 'top' // Place legend at the top
						}
					}
				}
			});
		}

		// Cleanup function
		return () => {
			chart?.destroy();
		};
	});

	// Update chart when data changes
	$effect(() => {
		if (chart && chartData) {
			chart.data = chartData;
			chart.update();
		}
	});
</script>

<div class="chart-container">
	<canvas bind:this={canvas}></canvas>
</div>

<style>
	.chart-container {
		position: relative;
		height: 300px; /* Same height as line chart */
		width: 100%;
	}
</style>