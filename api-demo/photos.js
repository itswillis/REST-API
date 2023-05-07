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
      const photoItem = document.createElement('div');
      photoItem.className = 'photo-item';

      const img = document.createElement('img');
      img.src = result.server_photo_url;
      img.width = 200;
      img.height = 200;
      photoItem.appendChild(img);

      const photoUUID = document.createElement('span');
      photoUUID.textContent = `UUID: ${result.photo_uuid}`;
      photoItem.appendChild(photoUUID);

      photosContainer.appendChild(photoItem);
  } catch (error) {
      console.error('Error', error);
  }
});

document.getElementById('retrieve-photos').addEventListener('click', retrieveAllPhotos);

async function retrieveAllPhotos() {
  const accessToken = localStorage.getItem('accessToken'); // Retrieve the access token from localStorage

  try {
      const response = await fetch('http://127.0.0.1:5000/photos', {
          method: 'GET',
          headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${accessToken}`,
          },
      });

      if (!response.ok) {
          throw new Error(`Error: ${response.status}`);
      }

      const photos = await response.json();
      const photosContainer = document.getElementById('photos-container');
      photosContainer.innerHTML = ''; // Clear existing photos

      photos.forEach(photo => {
          const photoItem = document.createElement('div');
          photoItem.className = 'photo-item';

          const img = document.createElement('img');
          img.src = photo.photo_url;
          img.width = 200;
          img.height = 200;
          photoItem.appendChild(img);

          const photoUUID = document.createElement('span');
          photoUUID.textContent = `UUID: ${photo.photo_uuid}`;
          photoItem.appendChild(photoUUID);

          photosContainer.appendChild(photoItem);
      });

  } catch (error) {
      console.error('Error:', error);
  }
}
