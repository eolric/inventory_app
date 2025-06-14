// Manejar eliminación con confirmación
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('form[method="POST"]').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('¿Estás seguro de que quieres eliminar este item?')) {
                e.preventDefault();
            }
        });
    });
});