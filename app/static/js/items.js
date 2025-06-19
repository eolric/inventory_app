// app/static/js/items.js
class ItemFormValidator {
    constructor(formId) {
        this.form = document.getElementById(formId);
        if (this.form) {
            this.init();
        }
    }

    init() {
        this.form.addEventListener('submit', this.validate.bind(this));
        this.setupPriceValidation();
        this.setupNumberValidation();
        this.setupFormValidation();
    }

    setupPriceValidation() {
        const precioCompra = this.form.querySelector('#precio_compra');
        const precioVenta = this.form.querySelector('#precio_venta');
        
        if (precioCompra && precioVenta) {
            [precioCompra, precioVenta].forEach(input => {
                input.addEventListener('input', this.validatePrices.bind(this));
            });
        }
    }

    setupNumberValidation() {
        this.form.querySelectorAll('input[type="number"]').forEach(input => {
            input.addEventListener('input', this.validateNumber.bind(this));
        });
    }

    setupFormValidation() {
        // Validación para campos requeridos
        this.form.querySelectorAll('[required]').forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
        });
    }

    validateNumber(e) {
        if (e.target.value < 0) {
            e.target.value = 0;
        }
    }

    validateField(input) {
        if (input.required && !input.value) {
            input.classList.add('is-invalid');
        } else {
            input.classList.remove('is-invalid');
        }
    }

    validatePrices() {
        const precioCompra = parseFloat(this.form.querySelector('#precio_compra').value) || 0;
        const precioVenta = parseFloat(this.form.querySelector('#precio_venta').value) || 0;
        const precioVentaInput = this.form.querySelector('#precio_venta');
        const submitButton = this.form.querySelector('button[type="submit"]');

        if (precioVenta <= precioCompra) {
            precioVentaInput.classList.add('is-invalid');
            if (submitButton) submitButton.disabled = true;
        } else {
            precioVentaInput.classList.remove('is-invalid');
            if (submitButton) submitButton.disabled = false;
        }
    }

    validate(e) {
        let isValid = true;
        
        // Validar campos requeridos
        this.form.querySelectorAll('[required]').forEach(input => {
            if (!input.value) {
                input.classList.add('is-invalid');
                isValid = false;
            }
        });

        // Validar precios
        const precioCompra = parseFloat(this.form.querySelector('#precio_compra').value) || 0;
        const precioVenta = parseFloat(this.form.querySelector('#precio_venta').value) || 0;
        const precioVentaInput = this.form.querySelector('#precio_venta');
        
        if (precioVenta <= precioCompra) {
            precioVentaInput.classList.add('is-invalid');
            isValid = false;
        }

        if (!isValid) {
            e.preventDefault();
            // Mostrar mensaje de error más visible
            const errorMessage = document.createElement('div');
            errorMessage.className = 'alert alert-danger mt-3';
            errorMessage.innerHTML = 'Por favor corrige los errores en el formulario';
            
            // Insertar después del formulario
            this.form.parentNode.insertBefore(errorMessage, this.form.nextSibling);
            
            // Hacer scroll al primer error
            const firstInvalid = this.form.querySelector('.is-invalid');
            if (firstInvalid) {
                firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstInvalid.focus();
            }
            
            return false;
        }
        
        return true;
    }
}

// Inicialización general
document.addEventListener('DOMContentLoaded', () => {
    // Inicializar validadores para todos los formularios de items
    new ItemFormValidator('create-item-form');
    new ItemFormValidator('edit-item-form');
    
    // Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Confirmación para eliminación
    document.querySelectorAll('form[method="POST"]').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (this.querySelector('input[name="_method"][value="DELETE"]') && 
                !confirm('¿Estás seguro de que quieres eliminar este item?')) {
                e.preventDefault();
            }
        });
    });

    // Validación global para campos numéricos
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('input', function() {
            if (this.value < 0) {
                this.value = 0;
            }
        });
    });
});