const verticalDiv = document.querySelector('.vertical');

if (verticalDiv) {
      verticalDiv.addEventListener('click', () => {
      verticalDiv.classList.toggle('mt-32'); 
    });
}
document.getElementById('paste-icon').addEventListener('click', async () => {
  try {
      const text = await navigator.clipboard.readText();
      document.getElementById('admin_token').value = text;
  } catch (err) {
      console.error('Error al acceder al portapapeles: ', err);
  }
}); 