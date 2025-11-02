<script lang="ts">
	import type { Snippet } from 'svelte';

	type Props = {
		variant?: 'primary' | 'secondary' | 'danger';
		size?: 'small' | 'medium' | 'large';
		loading?: boolean;
		disabled?: boolean;
		fullWidth?: boolean;
		type?: 'button' | 'submit' | 'reset';
		children?: Snippet;
		onclick?: (event: MouseEvent) => void;
		[key: string]: any;
	};

	const { 
		variant = 'primary', 
		size = 'medium', 
		loading = false, 
		disabled = false, 
		fullWidth = false, 
		type = 'button', 
		children, 
		onclick,
		...restProps 
	} = $props<Props>();
</script>

<button
	{type}
	{disabled}
    class="btn"
    class:variant-primary={variant === 'primary'}
    class:variant-secondary={variant === 'secondary'}
    class:variant-danger={variant === 'danger'}
    class:size-small={size === 'small'}
    class:size-medium={size === 'medium'}
    class:size-large={size === 'large'}
    class:loading
    class:full-width={fullWidth}
	onclick={onclick}
    {...restProps}
>
    {#if loading}
        <span class="spinner" aria-hidden="true"></span>
    {/if}
    	{@render children?.()}
</button>

<style>
	/* All style rules remain exactly the same */
	.btn {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		border: 1px solid transparent;
		border-radius: 4px;
		font-weight: 600;
		cursor: pointer;
		transition:
			background-color 0.2s ease,
			border-color 0.2s ease;
		white-space: nowrap;
	}

	.btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	/* --- Variants --- */
	.variant-primary {
		background-color: #007bff;
		color: white;
		border-color: #007bff;
	}
	.variant-primary:hover:not(:disabled) {
		background-color: #0056b3;
	}

	.variant-secondary {
		background-color: #6c757d;
		color: white;
		border-color: #6c757d;
	}
	.variant-secondary:hover:not(:disabled) {
		background-color: #5a6268;
	}
    
    .variant-danger {
		background-color: #dc3545;
		color: white;
		border-color: #dc3545;
	}
	.variant-danger:hover:not(:disabled) {
		background-color: #c82333;
	}

	/* --- Sizes --- */
	.size-small {
		padding: 5px 10px;
		font-size: 0.8rem;
	}
	.size-medium {
		padding: 10px 15px;
		font-size: 1rem;
	}
	.size-large {
		padding: 12px 20px;
		font-size: 1.1rem;
	}

	.full-width {
		width: 100%;
	}

	/* --- Loading Spinner --- */
	.spinner {
		width: 1em;
		height: 1em;
		border: 2px solid rgba(255, 255, 255, 0.3);
		border-radius: 50%;
		border-top-color: #ffffff;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>