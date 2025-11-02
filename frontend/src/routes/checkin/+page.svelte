<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import Button from '$lib/components/atomic/Button.svelte';
	import { api } from '$lib/services/api';

	// --- Types ---
	type RoutineStep = {
		step_id: string;
		routine_id: string;
		step_name: string;
		target_duration: number | null;
		step_order: number;
	};

	type Routine = {
		routine_id: string;
		routine_name: string;
		steps: RoutineStep[];
	};

	// Type for our form's input state
	type StepInput = {
		is_completed: boolean;
		actual_duration: number | null;
	};

	// --- State ---
	let routines: Routine[] = [];
	let stepInputs: Map<string, StepInput> = new Map();
	let isLoading = true;
	let errorMessage = '';
	let isSubmitting = false;

	// Other form fields
	let gratitudeEntry = '';
	let principleAlignment = 5;
	let principleAlignmentNote = '';
	let topGoalDescription = '';
	let topGoalCompleted = false;
	let timeMetrics = [
		{ name: 'Work', value: 0 },
		{ name: 'Family', value: 0 },
		{ name: 'Social', value: 0 },
		{ name: 'Exercise', value: 0 },
		{ name: 'Sleep', value: 0 },
		{ name: 'Maintenance', value: 0 }
	];
	let dailyRatings = [
		{ name: 'Productivity', value: 5 },
		{ name: 'Focus', value: 5 },
		{ name: 'Fun', value: 5 }
	];

	// --- Data Loading ---
	onMount(async () => {
		isLoading = true;
		errorMessage = '';
		try {
			// Fetch routines first to build the form
			await fetchRoutines();
			// Then check if data already exists for today
			await fetchTodaysCheckin();
		} catch (error: any) {
			errorMessage = error.message;
		} finally {
			isLoading = false;
		}
	});

	async function fetchRoutines() {
		try {
			routines = await api.get('/api/routines');
			console.log('Fetched routines:', routines);
			
			// Initialize stepInputs map
			const newStepInputs = new Map<string, StepInput>();
			for (const routine of routines) {
				for (const step of routine.steps) {
					newStepInputs.set(step.step_id, {
						is_completed: false,
						actual_duration: null
					});
				}
			}
			stepInputs = newStepInputs;
		} catch (error: any) {
			console.error('Failed to fetch routines:', error);
			errorMessage = 'Could not load your routines.';
		}
	}

	async function fetchTodaysCheckin() {
		try {
			// Use the new api.get function
			const todaysCheckinData = await api.get('/api/checkins/today');
			
			// --- Check-in FOUND: Pre-fill the form ---
			console.log("Today's Check-in Data:", todaysCheckinData);
			gratitudeEntry = todaysCheckinData.gratitude_entry || '';
			principleAlignment = todaysCheckinData.principle_alignment || 5;
			principleAlignmentNote = todaysCheckinData.principle_alignment_note || '';
			topGoalDescription = todaysCheckinData.top_goal?.goal_description || '';
			topGoalCompleted = todaysCheckinData.top_goal?.is_completed || false;

			// Pre-fill metrics
			timeMetrics.forEach((m) => {
				const found = todaysCheckinData.metrics.find(
					(dm: any) => dm.metric_type === 'Time Allocation' && dm.metric_name === m.name
				);
				if (found) m.value = found.value;
			});
			dailyRatings.forEach((r) => {
				const found = todaysCheckinData.metrics.find(
					(dm: any) => dm.metric_type === 'Daily Rating' && dm.metric_name === r.name
				);
				if (found) r.value = found.value;
			});

			// Pre-fill routine step inputs
			const newStepInputs = new Map(stepInputs);
			todaysCheckinData.completed_steps.forEach((step: any) => {
				if (newStepInputs.has(step.step_id)) {
					newStepInputs.set(step.step_id, {
						is_completed: step.is_completed,
						actual_duration: step.actual_duration
					});
				}
			});
			stepInputs = newStepInputs;

		} catch (error: any) {
			if (error.message.includes('No check-in found')) {
				console.log('No check-in found for today. Showing blank form.');
			} else {
				errorMessage = error.message;
			}
		}
	}

	// --- Form Submission ---
	async function handleSubmit() {
		isSubmitting = true;
		errorMessage = '';

		// ... (Build completed_steps and metrics arrays - this logic is the same) ...
		const completed_steps = Array.from(stepInputs.entries())
			.filter(([, data]) => data.is_completed)
			.map(([step_id, data]) => ({ step_id, ...data }));
		
		const metrics = [
			...timeMetrics.map((m) => ({ /* ... */ })),
			...dailyRatings.map((r) => ({ /* ... */ }))
		];

		const checkinPayload = {
			gratitude_entry: gratitudeEntry || null,
			principle_alignment: principleAlignment,
			principle_alignment_note: principleAlignmentNote || null,
			metrics: metrics,
			completed_steps: completed_steps,
			top_goal: topGoalDescription ? { goal_description: topGoalDescription, is_completed: topGoalCompleted } : null
		};
		
		try {
			// Use the new api.post function
			await api.post('/api/checkins', checkinPayload);
			alert('Check-in saved successfully!');
			goto('/'); // Redirect to dashboard
		} catch (error: any) {
			errorMessage = `Error saving check-in: ${error.message}`;
		} finally {
			isSubmitting = false;
		}
	}

	// --- NEW: Helper Function for Auto-Tick ---
	function handleDurationInput(stepId: string, event: Event) {
		const target = event.target as HTMLInputElement;
		const newValue = parseInt(target.value, 10); // Get the number entered

		// Get the current state for this step
		const currentInputData = stepInputs.get(stepId);

		if (currentInputData) {
			// Update the duration
			currentInputData.actual_duration = isNaN(newValue) || newValue <= 0 ? null : newValue; // Store null if 0 or invalid

			// Auto-tick if duration is positive and box isn't already checked
			if (currentInputData.actual_duration && currentInputData.actual_duration > 0 && !currentInputData.is_completed) {
				currentInputData.is_completed = true;
			}

			// Update the map to trigger reactivity
			stepInputs = new Map(stepInputs.set(stepId, currentInputData));
		}
	}

	// --- NEW: Helper Function for Select All ---
	function selectAllSteps(routineId: string) {
		const routine = routines.find(r => r.routine_id === routineId);
		if (!routine) return;

		const updatedInputs = new Map(stepInputs); // Create a new map for reactivity
		routine.steps.forEach(step => {
			const currentData = updatedInputs.get(step.step_id);
			if (currentData) {
				currentData.is_completed = true;
				// Optional: Set default duration if needed when selecting all
				// if (step.target_duration && !currentData.actual_duration) {
				//     currentData.actual_duration = step.target_duration;
				// }
			}
		});
		stepInputs = updatedInputs; // Assign the new map to trigger update
	}
</script>

<main>
	<h1>Daily Check-in</h1>

	{#if isLoading}
		<p>Loading check-in...</p>
	{:else if errorMessage}
		<p class="error">{errorMessage}</p>
	{:else}
		<form on:submit|preventDefault={handleSubmit}>
			<section>
				<h2>Routines</h2>
				{#if routines.length === 0}
					<p>
						You haven't set up any routines yet. <a href="/routines">Manage routines</a>
					</p>
				{:else}
					{#each routines as routine (routine.routine_id)}
						<div class="routine-block">
							<h3>
								{routine.routine_name}
								<Button onclick={() => selectAllSteps(routine.routine_id)}>Select All</Button>
							</h3>
							{#each routine.steps as step (step.step_id)}
								{@const inputData = stepInputs.get(step.step_id)}
								{#if inputData}
									<div class="step-item">
										<label>
											<input type="checkbox" bind:checked={inputData.is_completed} />
											{step.step_name}
										</label>
										{#if step.target_duration !== null && step.target_duration !== undefined}
											<div class="duration-input">
												<input
													type="number"
													value={inputData.actual_duration ?? ''}
													on:input={(e) => handleDurationInput(step.step_id, e)}
													placeholder="mins"
													min="0"  
												/>
												<span>/ {step.target_duration} mins</span>
											</div>
										{/if}
									</div>
								{/if}
							{/each}
						</div>
					{/each}
				{/if}
			</section>
			<section>
				<h2>Gratitude</h2>
				<textarea bind:value={gratitudeEntry} placeholder="What are you grateful for today?"></textarea>
			</section>

			<section>
				<h2>Principle Alignment</h2>
				<label for="principle-alignment">Rating (1-10): {principleAlignment}</label>
				<input
					type="range"
					id="principle-alignment"
					bind:value={principleAlignment}
					min="1"
					max="10"
					step="1"
				/>
				<textarea bind:value={principleAlignmentNote} placeholder="Why this rating?"></textarea>
			</section>

			<section>
				<h2>Today's Top Goal</h2>
				<input type="text" bind:value={topGoalDescription} placeholder="What's your main goal?" />
				<label class="checkbox-label">
					<input type="checkbox" bind:checked={topGoalCompleted} />
					Completed?
				</label>
			</section>

			<section>
				<h2>Time Allocation (%)</h2>
				{#each timeMetrics as metric, i}
					<div class="metric-item">
						<label for="time-{i}">{metric.name}</label>
						<input type="number" id="time-{i}" bind:value={metric.value} min="0" max="100" /> %
					</div>
				{/each}
			</section>

			<section>
				<h2>Daily Ratings (1-10)</h2>
				{#each dailyRatings as rating, i}
					<div class="metric-item">
						<label for="rating-{i}">{rating.name}: {rating.value}</label>
						<input
							type="range"
							id="rating-{i}"
							bind:value={rating.value}
							min="1"
							max="10"
							step="1"
						/>
					</div>
				{/each}
			</section>

			<Button type="submit" fullWidth={true}>Save Check-in</Button>
		</form>
	{/if}
</main>

<style>
	main {
		max-width: 600px;
		margin: 2rem auto;
		padding: 1rem;
		border: 1px solid #ccc;
		border-radius: 8px;
	}
	h1,
	h2,
	h3 {
		text-align: center;
		color: #333;
	}
	h3 {
		text-align: left;
		border-bottom: 1px solid #eee;
		padding-bottom: 5px;
		margin-top: 0;
	}
	section {
		margin-bottom: 1.5rem;
		padding: 1rem;
		border-radius: 4px;
		background-color: #fcfcfc;
		border: 1px solid #f0f0f0;
	}
	label {
		font-weight: bold;
	}
	input[type='text'],
	input[type='number'],
	textarea {
		width: 100%;
		padding: 8px;
		box-sizing: border-box;
		border: 1px solid #ccc;
		border-radius: 4px;
	}
	textarea {
		min-height: 60px;
		margin-top: 0.5rem;
	}
	input[type='range'] {
		width: 100%;
	}
	.checkbox-label {
		display: block;
		margin-top: 0.5rem;
		font-weight: normal;
	}
	.routine-block {
		margin-bottom: 1rem;
	}
	.step-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0.5rem 0;
	}
	.step-item label {
		font-weight: normal;
	}
	.duration-input {
		display: flex;
		align-items: center;
		gap: 5px;
	}
	.duration-input input {
		width: 60px;
		padding: 5px;
	}
	.duration-input span {
		font-size: 0.9em;
		color: #666;
	}
	.metric-item {
		margin-bottom: 0.8rem;
	}
	.error {
		color: red;
		text-align: center;
	}
	.routine-block h3 {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}
</style>