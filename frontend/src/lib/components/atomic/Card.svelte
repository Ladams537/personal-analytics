<script lang="ts">
	import type { Snippet } from 'svelte';
	
	type Props = {
		padding?: 'none' | 'small' | 'medium' | 'large';
		header?: Snippet;
		children?: Snippet;
		[key: string]: any;
	};

	const {
		padding = 'large',
		header,
		children,
		...restProps
	} = $props<Props>();
</script>

<div
	{...restProps}
	class="card"
	class:padding-none={padding === 'none'}
	class:padding-small={padding === 'small'}
	class:padding-medium={padding === 'medium'}
	class:padding-large={padding === 'large'}
>
	{#if header}
		<div class="card-header">
			{@render header()}
		</div>
	{/if}

	{#if children}
		<div class="card-content">
			{@render children()}
		</div>
	{/if}
</div>

<style>
	.card {
		background-color: #ffffff;
		border: 1px solid #eee;
		border-radius: 8px;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
		overflow: hidden; /* Ensures content respects border radius */
	}

	.card-header {
		padding: 1rem 1.5rem;
		border-bottom: 1px solid #eee;
		background-color: #fcfcfc;
	}

	/* --- Padding Variants --- */
	.padding-small {
		padding: 1rem;
	}
	.padding-medium {
		padding: 1.5rem;
	}
	.padding-large {
		padding: 2rem;
	}
	.padding-none {
		padding: 0;
	}

	/* If no header, apply padding directly to content */
	.card-content {
		padding: 0; /* Handled by the parent's padding class by default */
	}
	
	/* Special handling if there's a header */
	:global(.card:has(.card-header) .card-content.padding-small) {
		padding: 1rem;
	}
	:global(.card:has(.card-header) .card-content.padding-medium) {
		padding: 1.5rem;
	}
	:global(.card:has(.card-header) .card-content.padding-large) {
		padding: 2rem;
	}

	/* If a header exists, we apply padding to the content instead of the card */
	.card:has(.card-header) {
		padding: 0;
	}
</style>