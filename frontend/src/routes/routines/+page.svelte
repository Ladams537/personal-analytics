<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import Button from '$lib/components/atomic/Button.svelte';
	import Card from '$lib/components/atomic/Card.svelte';
	import { api } from '$lib/services/api';

	// --- Define Types ---
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
		is_active: boolean;
		created_at: string;
		steps: RoutineStep[];
	};

	let routines: Routine[] = [];
	let isLoading = true;
	let errorMessage = '';
	let newRoutineName = '';
	let newStepNames: { [key: string]: string } = {};
	let newStepDurations: { [key: string]: number } = {};

	onMount(async () => {
		await fetchRoutines();
	});

	async function fetchRoutines() {
		isLoading = true;
		errorMessage = '';
		try {
			// Use the new api.get function
			routines = await api.get('/api/routines');
			
			// Initialize input fields
			routines.forEach((r) => {
				newStepNames[r.routine_id] = '';
				newStepDurations[r.routine_id] = 0;
			});
		} catch (error: any) {
			errorMessage = error.message || 'Failed to load routines.';
		} finally {
			isLoading = false;
		}
	}

	async function handleCreateRoutine() {
		if (!newRoutineName.trim()) {
			alert('Please enter a routine name.');
			return;
		}

		try {
			// Use the new api.post function
			const newRoutine = await api.post('/api/routines', {
				routine_name: newRoutineName
			});

			routines = [...routines, { ...newRoutine, steps: [] }];
			newStepNames[newRoutine.routine_id] = '';
			newStepDurations[newRoutine.routine_id] = 0;
			newRoutineName = ''; // Clear input
		} catch (error: any) {
			alert(`Error creating routine: ${error.message}`);
		}
	}

	async function handleAddStep(routineId: string) {
		const stepName = newStepNames[routineId];
		const duration = newStepDurations[routineId];

		if (!stepName.trim()) {
			alert('Please enter a step name.');
			return;
		}

		const routine = routines.find((r) => r.routine_id === routineId);
		if (!routine) return;
		const nextStepOrder = routine.steps.length + 1;

		try {
			// Use the new api.post function
			const newStep = await api.post(`/api/routines/${routineId}/steps`, {
				step_name: stepName,
				target_duration: duration || null,
				step_order: nextStepOrder
			});

			routine.steps = [...routine.steps, newStep];
			routines = routines; // Trigger reactivity
			newStepNames[routineId] = '';
			newStepDurations[routineId] = 0;
		} catch (error: any) {
			alert(`Error adding step: ${error.message}`);
		}
	}
</script>

<main>
	<h1>Manage Routines</h1>

	<section class="form-section">
		<h2>Create a New Routine</h2>
		<form on:submit|preventDefault={handleCreateRoutine}>
			<input
				type="text"
				bind:value={newRoutineName}
				placeholder="e.g., 'Morning Routine'"
				required
			/>
			<button type="submit">Create</button>
		</form>
	</section>

	<hr />

	<section class="routines-list">
		<h2>Your Routines</h2>
		{#if isLoading}
			<p>Loading routines...</p>
		{:else if errorMessage}
			<p class="error">{errorMessage}</p>
		{:else if routines.length === 0}
			<p>You haven't created any routines yet.</p>
		{:else}
			{#each routines as routine (routine.routine_id)}
				<div class="routine-card">
					<h3>{routine.routine_name}</h3>
					<ul>
						{#each routine.steps as step (step.step_id)}
							<li>
								{step.step_order}. {step.step_name}
								{#if step.target_duration}
									<span>({step.target_duration} mins)</span>
								{/if}
							</li>
						{:else}
							<li>No steps added yet.</li>
						{/each}
					</ul>
					<form
						class="add-step-form"
						on:submit|preventDefault={() => handleAddStep(routine.routine_id)}
					>
						<input
							type="text"
							bind:value={newStepNames[routine.routine_id]}
							placeholder="New step name"
						/>
						<input
							type="number"
							bind:value={newStepDurations[routine.routine_id]}
							placeholder="Duration (mins)"
							min="0"
						/>
						<button type="submit">Add Step</button>
					</form>
				</div>
			{/each}
		{/if}
	</section>
</main>

<style>
	main {
		max-width: 700px;
		margin: 2rem auto;
		padding: 1rem;
	}
	h1,
	h2 {
		text-align: center;
	}
	.form-section {
		background-color: #f9f9f9;
		padding: 1.5rem;
		border-radius: 8px;
		margin-bottom: 2rem;
	}
	.form-section form {
		display: flex;
		gap: 10px;
	}
	input[type='text'],
	input[type='number'] {
		flex-grow: 1;
		padding: 8px;
		border: 1px solid #ccc;
		border-radius: 4px;
	}
	button {
		padding: 8px 15px;
		background-color: #007bff;
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
	}
	button:hover {
		background-color: #0056b3;
	}
	.routines-list {
		margin-top: 1rem;
	}
	.routine-card {
		border: 1px solid #eee;
		border-radius: 8px;
		padding: 1.5rem;
		margin-bottom: 1.5rem;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
	}
	.routine-card h3 {
		margin-top: 0;
		border-bottom: 1px solid #f0f0f0;
		padding-bottom: 0.5rem;
	}
	ul {
		list-style: none;
		padding-left: 0;
		margin-bottom: 1.5rem;
	}
	li {
		padding: 0.3rem 0;
	}
	li span {
		color: #777;
		font-size: 0.9em;
		margin-left: 0.5rem;
	}
	.add-step-form {
		display: flex;
		gap: 10px;
		border-top: 1px dashed #ccc;
		padding-top: 1rem;
		margin-top: 1rem;
	}
	.add-step-form input[type='text'] {
		flex-basis: 50%;
	}
	.add-step-form input[type='number'] {
		flex-basis: 30%;
	}
	.add-step-form button {
		flex-basis: 20%;
		background-color: #28a745;
	}
	.add-step-form button:hover {
		background-color: #218838;
	}
	.error {
		color: red;
		text-align: center;
	}
</style>