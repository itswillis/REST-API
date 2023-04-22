let accessToken = null;

async function register() {
    console.log('Register function called');

    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;

    console.log(`Email: ${email}, Password: ${password}`);

    try {
        const response = await fetch('http://127.0.0.1:5000/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        if (response.status === 400) {
            const data = await response.json();
            console.error('Registration failed:', data.message);
            // You can display the error message to the user using the DOM or alert
            alert(data.message);
            return;
        }

        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }

        const data = await response.json();
        console.log('Registration successful:', data);
        alert('Registration successful');
    } catch (error) {
        console.error('Error:', error);
    }
}

async function login() {
    console.log("Login function called")
    try {
        const email = document.getElementById("login-email").value;
        const password = document.getElementById("login-password").value;
        console.log("Email:", email, "Password:", password);

        const response = await fetch("http://127.0.0.1:5000/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ email, password }),
        });

        if (response.status === 401) {
            const data = await response.json();
            console.error("Login failed:", data.message);
            // Display the error message to the user using the DOM
            const errorElement = document.getElementById("error");
            errorElement.innerText = data.message;
            errorElement.style.display = "block";
            return;
        }

        const data = await response.json();
        console.log("Login successful:", data);

        // Store the access token
        accessToken = data.access_token;

        // Redirect to the photos page
        window.location.href = "photos.html";

    } catch (error) {
        console.error("Error:", error);
        // Handle error in a user-friendly manner
    }
}