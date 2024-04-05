document.addEventListener('DOMContentLoaded', function() {
    generarOrdenCompra();

});

function enviarDatosLocalStorageAlServidor() {
    
    var confirmacion = confirm("¿Deseas confirmar la venta?");
    if (!confirmacion) {
        return;
    }

    var ordenVenta = JSON.parse(localStorage.getItem('orden_venta')) || [];
    console.log('Datos del Local Storage:', ordenVenta);

    var csrfToken = document.querySelector('input[name="csrf_token"]').value;
    console.log('CSRF Token:', csrfToken);

    fetch('/ventas', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ orden_venta: ordenVenta })
    })
    .then(function(response) {
        if (!response.ok) {
            throw new Error('Error al enviar los datos del localStorage al servidor');
        }
        return response.json();
    })
    .then(function(data) {
        console.log('Datos del servidor (JSON):', data);
        if (data.success) {
            showAlert('success', data.message);
            setTimeout(function() {
                localStorage.clear();
                window.location.reload();
                if (data.pdf_base64) {
                    var pdfWindow = window.open("");
                    pdfWindow.document.write(
                        "<iframe width='100%' height='100%' src='data:application/pdf;base64, " + 
                        encodeURI(data.pdf_base64) + "'></iframe>"
                    );
                }
            }, 1500);
        } else {
            showAlert('error', data.message);
        }
    })
    .catch(function(error) {
        console.error('Error:', error);
        showAlert('danger', 'Error al registrar la venta, intente nuevamente');
    });
}


function showAlert(type, message) {
    var alertDiv = document.createElement('div');
    alertDiv.classList.add('alert', 'alert-' + type, 'alert-dismissible', 'fade', 'show');
    alertDiv.setAttribute('role', 'alert');

    var closeButton = document.createElement('button');
    closeButton.classList.add('btn-close');
    closeButton.setAttribute('type', 'button');
    closeButton.setAttribute('data-bs-dismiss', 'alert');
    closeButton.setAttribute('aria-label', 'Close');

    var messageText = document.createTextNode(message);

    alertDiv.appendChild(messageText);
    alertDiv.appendChild(closeButton);

    var container = document.getElementById('alert-container');
    container.appendChild(alertDiv);
    setTimeout(function() {
        alertDiv.remove();
    }, 2000);
}

function generarOrdenCompra() {
    var ordenVenta = JSON.parse(localStorage.getItem('orden_venta')) || [];
    console.log('Datos del Local Storage:', ordenVenta);

    var ventasContainer = document.querySelector('.ventas_orden');
    ventasContainer.innerHTML = '';

    var subtotal = 0; 

    if (ordenVenta.length === 0) {
        var mensaje = document.createElement('p');
        mensaje.classList.add('mensaje_orden_venta');
        mensaje.textContent = 'Añade galletas a tu orden de venta';
        ventasContainer.appendChild(mensaje);

        document.querySelector('.boton_vender').style.display = 'none';
    } else {
        document.querySelector('.boton_vender').style.display = 'block';

        ordenVenta.forEach(function(orden, index) {
            var divRow = document.createElement('div');
            divRow.classList.add('row');

            var divNombre = document.createElement('div');
            divNombre.classList.add('col-sm-6', 'col-lg-3');
            var nombreLabel = document.createElement('label');
            nombreLabel.textContent = orden.nombre;
            divNombre.appendChild(nombreLabel);
            divRow.appendChild(divNombre);

            var divCantidad = document.createElement('div');
            divCantidad.classList.add('col-sm-6', 'col-lg-3');
            var cantidadLabel = document.createElement('label');
            cantidadLabel.textContent = orden.cantidad + ' ' + orden.medida;
            divCantidad.appendChild(cantidadLabel);
            divRow.appendChild(divCantidad);
            
            var divMedida = document.createElement('div');
            divMedida.classList.add('col-sm-6', 'col-lg-3');
            var medidaLabel = document.createElement('label');
            medidaLabel.textContent = '$' + orden.costo.toFixed(2);
            divMedida.appendChild(medidaLabel);
            divRow.appendChild(divMedida);

            var divQuitar = document.createElement('div');
            divQuitar.classList.add('col-sm-6', 'col-lg-3');
            var quitarButton = document.createElement('button');
            quitarButton.textContent = 'Quitar';
            quitarButton.classList.add('btn', 'btn-danger');
            quitarButton.onclick = function() {
                eliminarRegistro(orden.id_galleta, orden.medida);
            };
            divQuitar.appendChild(quitarButton);
            divRow.appendChild(divQuitar);

            ventasContainer.appendChild(divRow);
            subtotal += orden.costo;
        });
        
        var impuestos = subtotal * 0.16;
        var total = subtotal + impuestos;

        var divSubtotal = document.createElement('div');
        divSubtotal.classList.add('subtotal');
        divSubtotal.textContent = 'Subtotal: $' + subtotal.toFixed(2);
        ventasContainer.appendChild(divSubtotal);

        var divTotal = document.createElement('div');
        divTotal.classList.add('total');
        divTotal.textContent = 'Total (incluyendo impuestos): $' + total.toFixed(2);
        ventasContainer.appendChild(divTotal);

    }
}

function eliminarRegistro(idGalleta, medida) {

    var confirmacion = confirm('¿Deseas eliminar este registro de la orden de venta?');

    if (confirmacion) {
        var cantidadOrden = JSON.parse(localStorage.getItem('orden_venta')) || [];

        cantidadOrden = cantidadOrden.filter(function(orden) {
            return !(orden.id_galleta === idGalleta && orden.medida === medida);
        });

        localStorage.setItem('orden_venta', JSON.stringify(cantidadOrden));

        generarOrdenCompra();
        
    }
}

function showInputAndButton(select) {
    var id = select.id.split('_').pop();
    var cantidadButtonDiv = document.getElementById('cantidad_button_' + id);
    var input = document.getElementById('cantidad_' + id);
    var boton = document.getElementById('boton_' + id);
    var mensajeError = document.getElementById('mensaje_error_' + id);

    mensajeError.textContent = "";
    mensajeError.style.display = 'none';

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

function handleInputChange(input) {
    var id = input.id.split('_').pop();
    var cantidad = input.value.trim();
    var medidaSelect = document.getElementById('medida_' + id);
    var boton = document.getElementById('boton_' + id);
    var mensajeError = document.getElementById('mensaje_error_' + id);

    if (isNaN(cantidad) || cantidad === '') {
        mensajeError.textContent = "Solo puedes ingresar números en este campo.";
        mensajeError.style.display = 'block';
        boton.disabled = true;
        return;
    }

    cantidad = parseInt(cantidad);

    if (cantidad <= 0) {
        cantidad = 1;
        input.value = cantidad;
    }

    if (medidaSelect.value === 'piezas' && cantidad < 1) {
        mensajeError.textContent = "La cantidad debe ser mayor o igual a 1.";
        mensajeError.style.display = 'block';
        boton.disabled = true;
        return;
    }

    mensajeError.style.display = 'none';
    boton.disabled = false;
}

function validateAndRoundQuantity(input, gramos_por_pieza, nombre_galleta) {
    var id = input.id.split('_').pop();
    var cantidad = parseInt(input.value);
    var medidaSelect = document.getElementById('medida_' + id);
    var mensajeError = document.getElementById('mensaje_error_' + id);
    var boton = document.getElementById('boton_' + id);
    var gramosPorPieza = parseFloat(gramos_por_pieza);

    if (isNaN(cantidad)) {
        mensajeError.textContent = "Solo puedes ingresar números en este campo.";
        mensajeError.style.display = 'block';
        boton.disabled = true;
        return;
    }

    if (medidaSelect.value === 'gramos') {
        if (cantidad % gramosPorPieza !== 0) {
            var cantidadRedondeada = Math.round(cantidad / gramosPorPieza) * gramosPorPieza;
            
            if (cantidadRedondeada === 0) {
                cantidadRedondeada = gramosPorPieza;
            }
            
            mensajeError.textContent = "No es posible vender " + cantidad + " gramos de esta galleta. La galleta de " + nombre_galleta + " pesa " + gramosPorPieza + " gramos por cada pieza.";
            mensajeError.style.display = 'block';
            input.value = cantidadRedondeada;
            boton.disabled = false;
            return;
        } else {
            mensajeError.style.display = 'none';
        }
    }
    boton.disabled = false;
}

function agregarCantidad(event, galletaId, galletaNombre, costo_galleta, gramos_por_galleta, disponible) {
    event.preventDefault();
    
    var ordenVenta = JSON.parse(localStorage.getItem('orden_venta'));
    var cantidadOrden = JSON.parse(localStorage.getItem('cantidad_orden'));

    var galletasTotales = 0;

    if (cantidadOrden && cantidadOrden.length > 0) {
        cantidadOrden.forEach(function(item) {
            if (item.id_galleta === galletaId) {
                if (item.medida === "piezas") {
                    galletasTotales += item.cantidad;
                } else if (item.medida === "gramos") {
                    galletasTotales += item.cantidad / gramos_por_galleta;
                }
            }
        });
    }

    if (ordenVenta && ordenVenta.length > 0) {
        ordenVenta.forEach(function(item) {
            if (item.id_galleta === galletaId) {
                if (item.medida === "piezas") {
                    galletasTotales += item.cantidad;
                } else if (item.medida === "gramos") {
                    galletasTotales += item.cantidad / gramos_por_galleta;
                }
            }
        });
    }

    var cantidadInput = document.getElementById('cantidad_' + galletaId);
    var cantidadSuma = parseInt(cantidadInput.value);

    var medidaSelect = document.getElementById('medida_' + galletaId);
    var medida = medidaSelect.value;

    if (medida === "gramos") {
        cantidadSuma = cantidadSuma / gramos_por_galleta;
    }

    if (galletasTotales + cantidadSuma > disponible) {
        alert("No puedes ingresar " + cantidadSuma + "galletas ya que superas el límite del producto disponible.");
        return;
    }

    var cantidadInput = document.getElementById('cantidad_' + galletaId);
    var cantidad = parseInt(cantidadInput.value);

    if (medida && !isNaN(cantidad) && cantidad > 0) {
        var cantidadOrden = JSON.parse(localStorage.getItem('cantidad_orden')) || [];

        var foundIndex = -1;
        cantidadOrden.forEach(function(orden, index) {
            if (orden.medida === medida) {
                foundIndex = index;
            }
        });

        if (foundIndex !== -1) {
            if (medida === 'piezas') {
                cantidadOrden[foundIndex].cantidad += cantidad;
                cantidadOrden[foundIndex].costo += cantidad * costo_galleta;
            } else if (medida === 'gramos') {
                cantidadOrden[foundIndex].cantidad += cantidad;
                cantidadOrden[foundIndex].costo += (cantidad / gramos_por_galleta) * costo_galleta;
            }
        } else {
            var nuevaOrden = {
                id_galleta: galletaId,
                nombre: galletaNombre,
                medida: medida,
                cantidad: medida === 'piezas' ? cantidad : cantidad,
                costo: medida === 'piezas' ? cantidad * costo_galleta : (cantidad / gramos_por_galleta) * costo_galleta,
                gramos_por_pieza: gramos_por_galleta
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

    var botonConfirmarOrden = document.getElementById('boton_confirmar_orden_' + galletaId);
    botonConfirmarOrden.disabled = false;
    mostrarCantidades(galletaId);
}

function mostrarCantidades(galletaId) {
    var cantidadOrden = JSON.parse(localStorage.getItem('cantidad_orden')) || [];
    var container = document.getElementById('cantidades-container_'+galletaId);

    container.innerHTML = ''; 

    if (cantidadOrden.length === 0) {
        container.innerHTML = '<p id="mensaje-vacio">Añade tus galletas</p>';
    } else {
        cantidadOrden.forEach(function(orden) {
            var div = document.createElement('div');
            div.innerHTML = `<p>Cantidad: ${orden.cantidad} ${orden.medida}, Costo: $${orden.costo.toFixed(2)}</p>`;
            container.appendChild(div);
        });
    }
}

function confirmarCancelar(galletaId) {
    var confirmacion = confirm('¿Estás seguro de que deseas cancelar la operación?');

    if (confirmacion) {
        limpiarFormulario(galletaId);
        var botonConfirmarOrden = document.getElementById('boton_confirmar_orden_' + galletaId);
        botonConfirmarOrden.disabled = true;
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

    mostrarCantidades(galletaId);
}

function confirmarOrden(galletaId) {
    var confirmacion = confirm('¿Deseas agregar este producto a la venta?');

    if (confirmacion) {
        var botonConfirmarOrden = document.getElementById('boton_confirmar_orden_' + galletaId);
        botonConfirmarOrden.disabled = true;

        var cantidadOrden = JSON.parse(localStorage.getItem('cantidad_orden')) || [];
        
        var ordenVenta = JSON.parse(localStorage.getItem('orden_venta')) || [];

        cantidadOrden.forEach(function(nuevaOrden) {
            var encontrado = false;

            for (var i = 0; i < ordenVenta.length; i++) {
                var ordenExistente = ordenVenta[i];
                if (ordenExistente.id_galleta === nuevaOrden.id_galleta &&
                    ordenExistente.nombre === nuevaOrden.nombre &&
                    ordenExistente.medida === nuevaOrden.medida) {
                    ordenExistente.cantidad += nuevaOrden.cantidad;
                    ordenExistente.costo += nuevaOrden.costo;
                    ordenExistente.gramos_por_pieza = nuevaOrden.gramos_por_pieza;
                    encontrado = true;
                    break;
                }
            }

            if (!encontrado) {
                ordenVenta.push(nuevaOrden);
            }
        });

        localStorage.setItem('orden_venta', JSON.stringify(ordenVenta));

        localStorage.removeItem('cantidad_orden');

        var modal = document.getElementById('staticBackdrop' + galletaId);
        var modalInstance = bootstrap.Modal.getInstance(modal);
        modalInstance.hide();
        
    }
    mostrarCantidades(galletaId);
    generarOrdenCompra();
}

function habilitarConfirmarOrden(galletaId, disponible,nombre) {
    var botonConfirmarOrden = document.getElementById('boton_confirmar_orden_' + galletaId);
    botonConfirmarOrden.disabled = true;

    var ordenVenta = JSON.parse(localStorage.getItem('orden_venta'));
    var galletasTotales = 0;

    if (ordenVenta && ordenVenta.length > 0) {
        ordenVenta.forEach(function(item) {
            if (item.id_galleta === galletaId) {
                if (item.medida === "piezas") {
                    galletasTotales += item.cantidad;
                } else if (item.medida === "gramos") {
                    galletasTotales += item.cantidad / item.gramos_por_pieza;
                }
            }
        });
    }

    if (galletasTotales !== 0){
        var disponibleActualizado = disponible - galletasTotales;
        var modalHeader = document.querySelector('.modal-title_' + galletaId );
        modalHeader.textContent = nombre +" Disponibles: " + disponibleActualizado;
    }

}

function sinDisponible(nombre){
    showAlert('warning', 'No hay ' + nombre + ' disponibles por el momento');
}

