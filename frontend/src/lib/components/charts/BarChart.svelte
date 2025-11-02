<script lang="ts">
	import { onMount } from 'svelte';
	import type { ChartData, ChartOptions } from 'chart.js';
	import { Chart } from 'chart.js'; // Components are already registered

	// Define the props
	type Props = {
		chartData: ChartData<'bar'>;
	};
	const { chartData } = $props<Props>();

	let canvas: HTMLCanvasElement;
	let chart: Chart;

	onMount(() => {
		const ctx = canvas.getContext('2d');
		if (ctx) {
			chart = new Chart(ctx, {
				type: 'bar', // Set chart type to 'bar'
				data: chartData,
				options: {
					responsive: true,
					maintainAspectRatio: false,
					scales: {
						y: {
							beginAtZero: true,
							max: 10 // Set max for 1-10 rating
						}
					},
					plugins: {
						legend: {
							display: false // Hide legend for a cleaner look
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
		height: 300px;
		width: 100%;
	}
</style>