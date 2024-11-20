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
let profilePic = document.getElementById('profile-pic');
let inputfile = document.getElementById('insertimg');

inputfile.onchange = function () {
    if (inputfile.files && inputfile.files[0]) {
        profilePic.src = URL.createObjectURL(inputfile.files[0]);
    }
};

/* 
    /**Scroll Boton
*/
window.onscroll = function() {
    const button = document.getElementById("scrollToTop");
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        button.style.display = "block";
    } else {
        button.style.display = "none";
    }
};

// Función para subir al principio de la página
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth' // Desplazamiento suave
    });
}


