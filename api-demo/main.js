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

        // Handle successful login, e.g., navigate to a different page or show a success message

    } catch (error) {
        console.error("Error:", error);
        // Handle error in a user-friendly manner
    }
}

async function sendPhoto() {
    const photoInput = document.getElementById('photo-upload');
    const photo = photoInput.files[0];

    if (!photo) {
        alert('No photo selected');
        return;
    }

    const formData = new FormData();
    formData.append('photo', photo);

    try {
        const response = await fetch('http://127.0.0.1:5000/photos', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            },
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }

        const data = await response.json();
        console.log('Photo uploaded:', data);
        alert('Photo uploaded successfully');
    } catch (error) {
        console.error('Error:', error);
    }
}

async function getPhotos() {
    try {
      const response = await fetch('http://127.0.0.1:5000/photos', {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
  
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
  
      const data = await response.json();
      const photoList = document.getElementById('photo-list');
      photoList.innerHTML = ''; // Clear the photo list
  
      data.forEach((photo) => {
        const img = document.createElement('img');
        img.src = `http://127.0.0.1:5000${photo.photo_url}`;
        img.alt = photo.filename; // Set the alt attribute of the image
        img.width = 200; // Set the width of the image, adjust as needed
        img.height = 200; // Set the height of the image, adjust as needed
        img.style.margin = '10px'; // Add some margin around the images
  
        photoList.appendChild(img);
      });
    } catch (error) {
      console.error('Error:', error);
    }
}


