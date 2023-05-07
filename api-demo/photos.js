async function getPhotos() {
  try {
    console.log('Access token in submit:', accessToken);
    const response = await fetch('http://127.0.0.1:5000/photos', {
        method: 'POST',
        headers: {
            Authorization: `Bearer ${accessToken}`, // Use the accessToken variable instead of localStorage
        },
        body: formData,
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
};

document.getElementById('upload-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const photoInput = document.getElementById('photo');
  const formData = new FormData();
  formData.append('photo', photoInput.files[0]);

  // Retrieve the access token from localStorage
  const accessToken = localStorage.getItem('accessToken');

  console.log('Access token before sending:', accessToken); // Check the access token before sending

  try {
      console.log('Access token in submit:', accessToken);
      const response = await fetch('http://127.0.0.1:5000/photos', {
          method: 'POST',
          headers: {
              Authorization: `Bearer ${accessToken}`, // Use the accessToken variable instead of localStorage
          },
          body: formData,
          credentials: 'include',
      });

      if (!response.ok) {
          const serverError = await response.json();
          console.error('Server error:', serverError);
          throw new Error('Upload failed'); // Keep the error message to maintain the same console output format
      }

      const result = await response.json();
      console.log(result);

      const photosContainer = document.getElementById('photos-container');
      const img = document.createElement('img');
      img.src = result.server_photo_url;
      img.width = 200;
      img.height = 200;
      photosContainer.appendChild(img);
  } catch (error) {
      console.error('Error', error);
  }
});