document.addEventListener('DOMContentLoaded', function() {
    generarOrdenCompra();

});

function enviarDatosLocalStorageAlServidor() {
    
    var confirmacion = confirm("¿Deseas confirmar la venta?");
    if (!confirmacion) {
        return;
    }

    var botonGuardarVenta = document.querySelector('.boton_vender button');
    botonGuardarVenta.disabled = true;

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
            cantidadLabel.textContent = (orden.medida === 'piezas' || orden.medida === 'gramos')? orden.cantidad + ' ' + orden.medida : orden.cantidad + ' Paquete de ' + orden.medida + ' gramos' ;
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

    if (select.value) {
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

    if (cantidad.includes('.')) {
        mensajeError.textContent = "Solo se aceptan números enteros en este campo.";
        mensajeError.style.display = 'block';
        boton.disabled = true;
        return;
    }

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
    var cantidad = input.value.trim(); 
    var medidaSelect = document.getElementById('medida_' + id);
    var mensajeError = document.getElementById('mensaje_error_' + id);
    var boton = document.getElementById('boton_' + id);
    var gramosPorPieza = parseFloat(gramos_por_pieza);

    if (isNaN(cantidad) || cantidad.includes('.')) {
        mensajeError.textContent = "Solo se aceptan números enteros en este campo.";
        mensajeError.style.display = 'block';
        boton.disabled = true;
        return;
    }

    cantidad = parseInt(cantidad);

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
            } else {
                
                var medidaEntera = parseInt(medida); 
                var cantidadPiezas = medidaEntera / gramos_por_galleta; 
                var costoPaquete = cantidadPiezas * costo_galleta * cantidad; 
                cantidadOrden[foundIndex].cantidad += cantidad; 
                cantidadOrden[foundIndex].costo += costoPaquete; 
            }
        } else {
            
            var nuevoCosto;
            if (medida === 'piezas') {
                nuevoCosto = cantidad * costo_galleta;
            } else if (medida === 'gramos') {
                nuevoCosto = (cantidad / gramos_por_galleta) * costo_galleta;
            } else {
                
                var medidaEntera = parseInt(medida); 
                var cantidadPiezas = medidaEntera / gramos_por_galleta; 
                nuevoCosto = cantidadPiezas * costo_galleta * cantidad; 
            }
            var nuevaOrden = {
                id_galleta: galletaId,
                nombre: galletaNombre,
                medida: medida,
                cantidad: cantidad,
                costo: nuevoCosto,
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
            div.innerHTML = (orden.medida === 'piezas' || orden.medida === 'gramos')? `<p>Cantidad: ${orden.cantidad} ${orden.medida}, Costo: $${orden.costo.toFixed(2)}</p>`: `<p>Cantidad: ${orden.cantidad}, Paquete de ${orden.medida} gramos, Costo: $${orden.costo.toFixed(2)}</p>`;
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

function habilitarConfirmarOrden(galletaId, disponible, nombre, gramosPorPieza) {
    console.log('id_galleta: ' + galletaId + '\n' + 'disponible: ' + disponible + '\n' + 'nombre: ' + nombre + '\n' + 'gramos_por_pieza: ' + gramosPorPieza);

    localStorage.removeItem('cantidad_orden');
    var botonConfirmarOrden = document.getElementById('boton_confirmar_orden_' + galletaId);
    botonConfirmarOrden.disabled = true;

    var ordenVenta = JSON.parse(localStorage.getItem('orden_venta'));
    var galletasTotales = 0;

    if (ordenVenta && ordenVenta.length > 0) {
        ordenVenta.forEach(function (item) {
            if (item.id_galleta === galletaId) {
                if (item.medida === "piezas") {
                    galletasTotales += item.cantidad;
                } else if (item.medida === "gramos") {
                    galletasTotales += item.cantidad / item.gramos_por_pieza;
                }
            }
        });
    }

    if (galletasTotales !== 0) {
        var disponibleActualizado = disponible - galletasTotales;
        var modalHeader = document.querySelector('.modal-title_' + galletaId);
        modalHeader.textContent = nombre + " Disponibles: " + disponibleActualizado;
    }

    var selectExistente = document.getElementById("medida_" + galletaId);
    if (!selectExistente) {
        var selectMedida = document.createElement("select");
        selectMedida.className = "form-select";
        selectMedida.id = "medida_" + galletaId;
        selectMedida.setAttribute("onchange", "showInputAndButton(this)");

        var optionSelecciona = document.createElement("option");
        optionSelecciona.value = "";
        optionSelecciona.text = "Selecciona una medida";
        selectMedida.appendChild(optionSelecciona);

        var optionPiezas = document.createElement("option");
        optionPiezas.value = "piezas";
        optionPiezas.text = "Piezas";
        selectMedida.appendChild(optionPiezas);

        var optionGramos = document.createElement("option");
        optionGramos.value = "gramos";
        optionGramos.text = "Gramos";
        selectMedida.appendChild(optionGramos);

        var gramosPorPiezaInt = parseInt(gramosPorPieza);

        var mayorA700 = 0;
        for (var i = gramosPorPiezaInt; i < 700; i += gramosPorPiezaInt) {
            mayorA700 = i;
        }

        if (mayorA700 < 700) {
            mayorA700 += gramosPorPiezaInt;
        }
        var optionPaquete1 = document.createElement("option");
        optionPaquete1.value = mayorA700;
        optionPaquete1.text = "Paquete de " + mayorA700 + " gramos";
        selectMedida.appendChild(optionPaquete1);

        var mayorA1000 = 0;
        for (var i = gramosPorPiezaInt; i < 1000; i += gramosPorPiezaInt) {
            mayorA1000 = i;
        }

        if (mayorA1000 < 1000) {
            mayorA1000 += gramosPorPiezaInt;
        }
        var optionPaquete2 = document.createElement("option");
        optionPaquete2.value = mayorA1000;
        optionPaquete2.text = "Paquete de " + mayorA1000 + " gramos";
        selectMedida.appendChild(optionPaquete2);

        var form = document.getElementById("form_" + galletaId);
        var firstDiv = form.querySelector('.mb-3');
        firstDiv.appendChild(document.createTextNode("Elige una opción"));
        firstDiv.appendChild(selectMedida);
    }
}



function sinDisponible(nombre){
    showAlert('warning', 'No hay ' + nombre + ' disponibles por el momento');
}

function validarMonto(dineroEnCaja) {
    
    dineroEnCaja = parseFloat(dineroEnCaja);

    var montoRetirar = parseFloat(document.getElementById('monto_retirar').value);
    var btnRecolecta = document.getElementById('btn_recolecta');
    var montoError = document.getElementById('monto_error');

    if (isNaN(montoRetirar)) {
        montoError.textContent = "El monto a retirar debe ser un número válido.";
        btnRecolecta.disabled = true;
        return;
    }

    if (montoRetirar > dineroEnCaja) {
        montoError.textContent = "No puedes retirar más de " + dineroEnCaja + " pesos.";
        btnRecolecta.disabled = true;
        return;
    }
    var resta = dineroEnCaja - montoRetirar;
    var monto_minimo = dineroEnCaja - 200; 
    if (resta > 200) {
        montoError.textContent = "No puedes dejar más de 200 pesos en caja, monto minimo: $"+monto_minimo+' pesos.';
        btnRecolecta.disabled = true;
        return;
    }

    montoError.textContent = "";
    btnRecolecta.disabled = false;
}

function validarUsuario(id_usuario) {
    console.log(id_usuario.value);
    var btnRecolecta = document.getElementById('btn_corte');
    var montoError = document.getElementById('error_corte');
    
    if (isNaN(id_usuario.value) || id_usuario.value ==='') {
        montoError.textContent = "Ingresa un número de empleado válido.";
        btnRecolecta.disabled = true;
        return;
    }

    montoError.textContent = "";
    btnRecolecta.disabled = false;

}

function finalizarCorte(id_corte_caja){
    alert(id_corte_caja);
}