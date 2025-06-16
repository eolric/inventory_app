// Manejar eliminación con confirmación
document.addEventListener('DOMContentLoaded', function() {

    // Manejar eliminación con confirmación
    document.querySelectorAll('form[method="POST"]').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('¿Estás seguro de que quieres eliminar este item?')) {
                e.preventDefault();
            }
        });
    });

    // Validación para precio_venta > precio_compra
    const itemForms = document.querySelectorAll('form[action^="/items/"]');
    itemForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const precioCompra = parseFloat(form.querySelector('#precio_compra').value);
            const precioVenta = parseFloat(form.querySelector('#precio_venta').value);
            
            if (precioVenta <= precioCompra) {
                e.preventDefault();
                alert('El precio de venta debe ser mayor al precio de compra');
                form.querySelector('#precio_venta').focus();
            }
        });
    });

    // Validación en tiempo real para campos numéricos
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('input', function() {
            if (this.value < 0) {
                this.value = 0;
            }
        });
    });

    // Validación en tiempo real de precios
    function validatePrices() {
        const precioCompra = parseFloat(document.getElementById('precio_compra').value);
        const precioVenta = parseFloat(document.getElementById('precio_venta').value);
        const errorElement = document.getElementById('precio_venta_error');
        const submitButton = document.querySelector('form button[type="submit"]');

        if (precioVenta <= precioCompra) {
            document.getElementById('precio_venta').classList.add('is-invalid');
            submitButton.disabled = true;
        } else {
            document.getElementById('precio_venta').classList.remove('is-invalid');
            submitButton.disabled = false;
        }
    }

    // Asignar eventos a los campos
    document.getElementById('precio_compra').addEventListener('input', validatePrices);
    document.getElementById('precio_venta').addEventListener('input', validatePrices);
});