const form = document.getElementById('downloadForm');
  const videoUrlInput = document.getElementById('videoUrl');
  const modeSelect = document.getElementById('mode');
  const qualityDiv = document.getElementById('qualityDiv');
  const qualitySelect = document.getElementById('quality');
  const loadingSpinner = document.getElementById('loadingSpinner');
  const errorAlert = document.getElementById('errorAlert');
  const successAlert = document.getElementById('successAlert');

  modeSelect.addEventListener('change', () => {
    qualityDiv.style.display = (modeSelect.value === 'audio') ? 'none' : 'block';
    if (modeSelect.value === 'video') {
      qualitySelect.value = 'best';
    }
  });

  function showLoading() { loadingSpinner.style.display = 'block'; }
  function hideLoading() { loadingSpinner.style.display = 'none'; }
  function showError(msg) {
    errorAlert.textContent = msg;
    errorAlert.style.display = 'block';
    successAlert.style.display = 'none';
  }
  function showSuccess(msg) {
    successAlert.textContent = msg;
    successAlert.style.display = 'block';
    errorAlert.style.display = 'none';
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const url = videoUrlInput.value.trim();
    if (!url) return showError('Please enter a YouTube URL');

    const mode = modeSelect.value;
    const quality = qualitySelect.value;

    showLoading();
    errorAlert.style.display = 'none';
    successAlert.style.display = 'none';

    try {
      const response = await fetch('/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, mode, quality })
      });

      if (!response.ok) {
        // Try to parse error message from JSON
        let errorMsg = 'Download failed: ' + response.statusText;
        try {
          const errorData = await response.json();
          if (errorData && errorData.error) errorMsg = errorData.error;
        } catch {}
        throw new Error(errorMsg);
      }

      const blob = await response.blob();
      let filename = mode === 'audio' ? 'audio.mp3' : 'video.mp4';
      const disposition = response.headers.get('Content-Disposition');
      if (disposition) {
        const match = disposition.match(/filename\s*=\s*"?([^;\"]+)/);
        if (match && match[1]) {
          filename = match[1].trim();
        }
      }

      const downloadUrl = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(downloadUrl);

      showSuccess('Download Complete!');
    } catch (err) {
      showError(err.message || 'An unexpected error occurred.');
    } finally {
      hideLoading();
    }
  });
