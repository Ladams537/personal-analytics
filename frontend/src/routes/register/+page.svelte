<script>
	import { goto } from "$app/navigation";

    let displayName = '';
    let email = '';
    let password = '';

    async function handleSubmit() {
        // The data to send to the backend
        const userData = {
            display_name: displayName,
            email: email,
            password: password
        };

        try {
            // Use the browser's fetch API to make the request
            const response = await fetch('http://localhost:8000/api/users', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            });

            if (response.ok) {
                const result = await response.json();
                console.log('Success:', result);
                alert('User created successfully!');
                goto('/login');
            } else {
                // Handle server errors (e.g., 500 Internal Server Error)
                const errorResult = await response.json();
                console.error('Error:', errorResult);
                alert(`Error creating user: ${errorResult.message}`);
            }
        } catch (error) {
            // Handle network errors
            console.error('Network error:', error);
            alert('A network error occurred. Please try again.');
        }
    }
</script>

<main>
    <h1>Create an Account</h1>
    <form on:submit|preventDefault={handleSubmit}>
        <div>
            <label for="displayName">Display Name</label>
            <input type="text" id="displayName" bind:value={displayName} required />
        </div>
        <div>
            <label for="email">Email</label>
            <input type="email" id="email" bind:value={email} required />
        </div>
        <div>
            <label for="password">Password</label>
            <input type="password" id="password" bind:value={password} required />
        </div>
        <button type="submit">Register</button>
    </form>
</main>

<style>
    main {
        max-width: 400px;
        margin: 2rem auto;
        text-align: center;
    }
    div {
        margin-bottom: 1rem;
        text-align: left;
    }
    label {
        display: block;
    }
    input {
        width: 100%;
        padding: 8px;
        box-sizing: border-box;
    }
</style>