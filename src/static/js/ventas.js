function showInputAndButton(select) {
    var id = select.id.split('_').pop();
    var cantidadButtonDiv = document.getElementById('cantidad_button_' + id);
    var input = document.getElementById('cantidad_' + id);
    var boton = document.getElementById('boton_' + id);

    if (select.value === 'gramos' || select.value === 'piezas') {
        cantidadButtonDiv.style.display = 'block';
        input.value = '';
        boton.disabled = true;
    } else {
        cantidadButtonDiv.style.display = 'none';
        input.value = '';
        boton.disabled = true;
    }
}

function validateInput(input) {
    var id = input.id.split('_').pop();
    var cantidad = input.value;
    var medidaSelect = document.getElementById('medida_' + id);
    var boton = document.getElementById('boton_' + id);

    if (medidaSelect.value === 'gramos' && cantidad < 50) {
        boton.disabled = true;
    } else if (medidaSelect.value === 'piezas' && cantidad < 1) {
        boton.disabled = true;
    } else {
        boton.disabled = false;
    }
}

function agregarCantidad(event, galletaId) {
    event.preventDefault();

    var cantidadInput = document.getElementById('cantidad_' + galletaId);
    var cantidad = parseInt(cantidadInput.value);

    var medidaSelect = document.getElementById('medida_' + galletaId);
    var medida = medidaSelect.value;

    if (medida && !isNaN(cantidad) && cantidad > 0) {
        var cantidadOrden = JSON.parse(localStorage.getItem('cantidad_orden')) || [];

        var foundIndex = -1;
        cantidadOrden.forEach(function(orden, index) {
            if (orden.tipo === medida) {
                foundIndex = index;
            }
        });

        if (foundIndex !== -1) {
            cantidadOrden[foundIndex].cantidad += cantidad;
        } else {
            var nuevaOrden = {
                id_galleta: galletaId,
                tipo: medida,
                cantidad: cantidad
            };
            cantidadOrden.push(nuevaOrden);
        }

        localStorage.setItem('cantidad_orden', JSON.stringify(cantidadOrden));

        cantidadInput.value = '';

        var boton = document.getElementById('boton_' + galletaId);
        boton.disabled = true;

        medidaSelect.value = '';

        var contenedor = document.getElementById('cantidad_button_' + galletaId);
        contenedor.style.display = 'none';
    }
    mostrarCantidades();
}

function mostrarCantidades() {
    var cantidadOrden = JSON.parse(localStorage.getItem('cantidad_orden')) || [];
    var container = document.getElementById('cantidades-container');

    container.innerHTML = ''; 

    if (cantidadOrden.length === 0) {
        container.innerHTML = '<p id="mensaje-vacio">Añade tus galletas</p>';
    } else {
        cantidadOrden.forEach(function(orden) {
            var div = document.createElement('div');
            // div.innerHTML = `<p>Tipo: ${orden.tipo}, Cantidad: ${orden.cantidad}</p>`;
            div.innerHTML = `<p>Cantidad: ${orden.cantidad} ${orden.tipo}</p>`;
            container.appendChild(div);
        });
    }
}

function confirmarCancelar(galletaId) {
    var confirmacion = confirm('¿Estás seguro de que deseas cancelar la operación?');

    if (confirmacion) {
        limpiarFormulario(galletaId);
    }
}


function limpiarFormulario(galletaId) {
    var select = document.getElementById('medida_' + galletaId);
    select.value = '';

    var cantidadButtonDiv = document.getElementById('cantidad_button_' + galletaId);
    cantidadButtonDiv.style.display = 'none';

    var input = document.getElementById('cantidad_' + galletaId);
    input.value = '';

    var boton = document.getElementById('boton_' + galletaId);
    boton.disabled = true;

    localStorage.removeItem('cantidad_orden');

    mostrarCantidades();
}