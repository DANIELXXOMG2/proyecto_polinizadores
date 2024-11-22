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

document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('insertimg');
    const profilePic = document.getElementById('profile-pic');

    if (fileInput && profilePic) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                if (file.size > 5 * 1024 * 1024) { // 5MB limit
                    alert('La imagen es demasiado grande. Por favor selecciona una imagen menor a 5MB.');
                    fileInput.value = '';
                    return;
                }
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    profilePic.src = e.target.result;
                }
                reader.readAsDataURL(file);
            }
        });
    }
});

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


