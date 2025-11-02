<script lang="ts">
	import { onMount } from 'svelte';
	import type { ChartData, ChartOptions } from 'chart.js';
	// Import Chart.js and the components we need
	import {
		Chart,
		Title,
		Tooltip,
		Legend,
		LineElement,
		LinearScale,
		PointElement,
		CategoryScale,
		LineController,
        DoughnutController,
        ArcElement,
        BarController, 
        BarElement
	} from 'chart.js';

	// Register the components we're using
	Chart.register(
		Title,
		Tooltip,
		Legend,
		LineElement,
		LinearScale,
		PointElement,
		CategoryScale,
		LineController,
		DoughnutController,
		ArcElement,
        BarController,
        BarElement
	);

	// Define the props
	type Props = {
		chartData: ChartData<'line'>;
	};
	const { chartData } = $props<Props>();

	let canvas: HTMLCanvasElement; // The <canvas> element
	let chart: Chart; // The Chart.js instance

	// onMount runs when the component is added to the page
	onMount(() => {
		const ctx = canvas.getContext('2d');
		if (ctx) {
			// Create the new chart
			chart = new Chart(ctx, {
				type: 'line',
				data: chartData,
				options: {
					responsive: true,
					maintainAspectRatio: false,
					scales: {
						y: {
							beginAtZero: true,
							ticks: {
								// Ensure y-axis shows whole numbers if data is all integers
								precision: 0
							}
						}
					}
				}
			});
		}

		// Return a cleanup function
		return () => {
			// Destroy the chart instance when the component is removed
			chart?.destroy();
		};
	});

	// Use an $effect to update the chart when chartData prop changes
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