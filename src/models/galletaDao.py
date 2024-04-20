from .Models import db, Galleta, Receta, RecetaMateriaIntermedia, MateriaPrima, Equivalencia, Venta, DetalleVenta,InventarioProductoTerminado, CorteCaja, CorteCajaVenta, Retiro,EquivalenciaMedida,Proveedor
from sqlalchemy import func

class GalletaDAO:

    @classmethod
    def get_all(cls):
        try:
            return Galleta.query.all()
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_costo_galletas(cls):
        try:
            inventario_disponible_subquery = db.session.query(
                InventarioProductoTerminado.id_galleta,
                func.sum(InventarioProductoTerminado.cantidad).label("disponible")
            ).filter(InventarioProductoTerminado.estatus == 1).group_by(InventarioProductoTerminado.id_galleta).subquery()

            resultado = db.session.query(
                Galleta.id_galleta,
                Galleta.nombre,
                Galleta.imagen,
                func.ROUND(
                    ((Galleta.porcentaje_ganancia * func.SUM(RecetaMateriaIntermedia.cantidad * MateriaPrima.costo)) + func.SUM(RecetaMateriaIntermedia.cantidad * MateriaPrima.costo)) / Equivalencia.piezas,
                    1
                ).label('costo_galleta'),
                inventario_disponible_subquery.c.disponible.label('disponible'),
                Equivalencia.piezas,
                Equivalencia.gramaje,
                (Equivalencia.gramaje / Equivalencia.piezas).label('gramos_por_pieza')
            ).join(
                Receta, Galleta.id_galleta == Receta.id_galleta
            ).join(
                RecetaMateriaIntermedia, Receta.id_receta == RecetaMateriaIntermedia.id_receta
            ).join(
                MateriaPrima, RecetaMateriaIntermedia.id_materia == MateriaPrima.id_materia
            ).join(
                Equivalencia, Receta.id_receta == Equivalencia.id_receta
            ).outerjoin(
                inventario_disponible_subquery, Galleta.id_galleta == inventario_disponible_subquery.c.id_galleta
            ).group_by(
                Galleta.id_galleta, Galleta.nombre, Galleta.imagen, Galleta.porcentaje_ganancia, Equivalencia.piezas, Equivalencia.gramaje
            ).all()

            return resultado
        except Exception as ex:
            raise Exception(ex)
        
    def get_cantidad_necesaria(id_receta, id_materia):
        try:
            cantidad_necesaria = RecetaMateriaIntermedia.query.filter_by(id_receta=id_receta, id_materia=id_materia).first().cantidad
            return cantidad_necesaria
        except Exception as ex:
            raise Exception(ex)
    
class InventarioProductoTerminadoDAO:
    
    @classmethod
    def obtener_registros_mas_antiguos(cls, id_galleta):
        try:
            registros = InventarioProductoTerminado.query.filter_by(id_galleta=id_galleta, estatus=1).order_by(InventarioProductoTerminado.fecha_produccion.asc()).all()
            detalles_registros = []
            for registro in registros:
                detalles_registro = {
                    'id_inventario_prod_terminado': registro.id_inventario_prod_terminado,
                    'id_galleta': registro.id_galleta,
                    'fecha_produccion': registro.fecha_produccion.strftime("%Y-%m-%d %H:%M:%S"),
                    'cantidad': registro.cantidad,
                    'estatus': registro.estatus
                }
                detalles_registros.append(detalles_registro)
            return detalles_registros
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def actualizar_registro(cls, id_inventario_prod_terminado, nuevos_valores):
        try:
            registro = InventarioProductoTerminado.query.get(id_inventario_prod_terminado)
            registro.cantidad = nuevos_valores.get('cantidad', registro.cantidad)
            registro.estatus = nuevos_valores.get('estatus', registro.estatus)
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            raise Exception(ex)


class VentaDAO:

    @classmethod
    def insert_venta(cls, fecha_venta, hora_venta, subtotal, total):
        try:
            nueva_venta = Venta(
                fecha_venta=fecha_venta,
                hora_venta=hora_venta,
                subtotal=subtotal,
                total=total
            )
            db.session.add(nueva_venta)
            db.session.commit()
            return nueva_venta.id_venta
        except Exception as ex:
            db.session.rollback()
            raise Exception(ex)
        
    @classmethod
    def obtener_total_por_id_venta(cls, id_venta):
        try:
            venta = Venta.query.filter_by(id_venta=id_venta).first()
            if venta:
                return venta.total
            else:
                raise ValueError("No se encontró una venta con el id especificado.")
        except Exception as ex:
            raise Exception(ex)

class DetalleVentaDAO:

    @classmethod
    def insert_detalle_venta(cls, id_venta, id_galleta, medida, cantidad, total):
        try:
            nuevo_detalle_venta = DetalleVenta(
                id_venta=id_venta,
                id_galleta=id_galleta,
                medida=medida,
                cantidad=cantidad,
                total=total
            )
            db.session.add(nuevo_detalle_venta)
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            raise Exception(ex)
        
class CorteCajaDAO:
    
    @classmethod
    def insertar_corte_caja(cls, fecha_de_inicio, hora_inicio, fecha_de_termino, hora_termino, estatus, id_usuario):
        try:
            nuevo_corte_caja = CorteCaja(
                fecha_de_inicio=fecha_de_inicio,
                hora_inicio=hora_inicio,
                fecha_de_termino=fecha_de_termino,
                hora_termino=hora_termino,
                estatus=estatus,
                id_usuario=id_usuario
            )
            db.session.add(nuevo_corte_caja)
            db.session.commit()
            return nuevo_corte_caja.id_corte_caja
        except Exception as ex:
            db.session.rollback()
            raise Exception(ex)
    
    @classmethod
    def consultar_primer_registro_descendente(cls):
        try:
            primer_registro = CorteCaja.query.order_by(CorteCaja.id_corte_caja.desc()).first()
            if primer_registro:
                resultado = {
                    'id_corte_caja': primer_registro.id_corte_caja,
                    'fecha_de_inicio': primer_registro.fecha_de_inicio.strftime("%Y-%m-%d") if primer_registro.fecha_de_inicio is not None else None,
                    'hora_inicio': primer_registro.hora_inicio.strftime("%H:%M:%S") if primer_registro.hora_inicio is not None else None,
                    'fecha_de_termino': primer_registro.fecha_de_termino.strftime("%Y-%m-%d") if primer_registro.fecha_de_termino is not None else None,
                    'hora_termino': primer_registro.hora_termino.strftime("%H:%M:%S") if primer_registro.hora_termino is not None else None,
                    'estatus': primer_registro.estatus,
                    'id_usuario': primer_registro.id_usuario
                }
                return resultado
            else:
                return None
        except Exception as ex:
            raise Exception(ex)
    
    @classmethod
    def finalizar_corte(cls, id_corte_caja, fecha_de_termino, hora_termino):
        try:
            corte_caja = CorteCaja.query.get(id_corte_caja)
            if corte_caja:
                corte_caja.fecha_de_termino = fecha_de_termino
                corte_caja.hora_termino = hora_termino
                corte_caja.estatus = 1
                db.session.commit()
            else:
                raise ValueError("No se encontró el registro de corte de caja con el ID especificado.")
        except Exception as ex:
            db.session.rollback()
            raise Exception(ex)

class CorteCajaVentaDAO:

    @classmethod
    def insertar_corte_caja_venta(cls, id_venta, id_corte_caja, estatus):
        try:
            nuevo_corte_caja_venta = CorteCajaVenta(
                id_venta=id_venta,
                id_corte_caja=id_corte_caja,
                estatus=estatus
            )
            print(nuevo_corte_caja_venta)
            db.session.add(nuevo_corte_caja_venta)
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            raise Exception(ex)

    @classmethod
    def consultar_por_id_corte_caja(cls, id_corte_caja):
        try:
            corte_caja_ventas = CorteCajaVenta.query.filter_by(id_corte_caja=id_corte_caja, estatus=1).all()
            resultados = []
            for corte_caja_venta in corte_caja_ventas:
                resultado = {
                    'id_corte_caja_venta': corte_caja_venta.id_corte_caja_venta,
                    'id_venta': corte_caja_venta.id_venta,
                    'id_corte_caja': corte_caja_venta.id_corte_caja,
                    'estatus': corte_caja_venta.estatus
                }
                resultados.append(resultado)
            return resultados
        except Exception as ex:
            raise Exception(ex)
        
    @classmethod
    def consultar_para_generar_corte(cls, id_corte_caja):
        try:
            corte_caja_ventas = CorteCajaVenta.query.filter_by(id_corte_caja=id_corte_caja).all()
            resultados = []
            for corte_caja_venta in corte_caja_ventas:
                # print(corte_caja_venta)
                resultado = {
                    'id_corte_caja_venta': corte_caja_venta.id_corte_caja_venta,
                    'id_venta': corte_caja_venta.id_venta,
                    'id_corte_caja': corte_caja_venta.id_corte_caja,
                    'estatus': corte_caja_venta.estatus
                }
                resultados.append(resultado)
            return resultados
        except Exception as ex:
            raise Exception(ex)
        
    @classmethod
    def actualizar_estatus(cls, id_corte_caja):
        try:
            corte_caja_ventas = CorteCajaVenta.query.filter_by(id_corte_caja=id_corte_caja, estatus=1).all()

            for corte_caja_venta in corte_caja_ventas:
                corte_caja_venta.estatus = 0
                db.session.commit()

        except Exception as ex:
            db.session.rollback()

class RetiroDAO:

    @classmethod
    def insertar_retiro(cls, fecha_hora, monto, motivo, id_corte_caja, id_usuario):
        try:
            nuevo_retiro = Retiro(
                fecha_hora=fecha_hora,
                monto=monto,
                motivo=motivo,
                id_corte_caja=id_corte_caja,
                id_usuario=id_usuario
            )
            db.session.add(nuevo_retiro)
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            raise Exception(ex)

    @classmethod
    def consultar_retiros_recolecta_por_id_corte_caja(cls, id_corte_caja):
        try:
            retiros = Retiro.query.filter_by(id_corte_caja=id_corte_caja, motivo='recolecta').all()
            resultados = []
            for retiro in retiros:
                resultado = {
                    'id_retiro': retiro.id_retiro,
                    'fecha_hora': retiro.fecha_hora.strftime("%Y-%m-%d %H:%M:%S"),
                    'monto': retiro.monto,
                    'motivo': retiro.motivo,
                    'id_corte_caja': retiro.id_corte_caja,
                    'id_usuario': retiro.id_usuario
                }
                resultados.append(resultado)
            return resultados
        except Exception as ex:
            raise Exception(ex)
    @classmethod
    def consultar_retiros_no_recolecta_por_id_corte_caja(cls, id_corte_caja):
        try:
            retiros = Retiro.query.filter(Retiro.id_corte_caja == id_corte_caja, Retiro.motivo != 'recolecta').all()
            resultados = []
            for retiro in retiros:
                resultado = {
                    'id_retiro': retiro.id_retiro,
                    'fecha_hora': retiro.fecha_hora.strftime("%Y-%m-%d %H:%M:%S"),
                    'monto': retiro.monto,
                    'motivo': retiro.motivo,
                    'id_corte_caja': retiro.id_corte_caja,
                    'id_usuario': retiro.id_usuario
                }
                resultados.append(resultado)
            return resultados
        except Exception as ex:
            raise Exception(ex)


class MateriaPrimaDAO:
    
    @classmethod
    def obtener_unidad_medida(cls, id_materia):
        try:
            unidad = db.session.query(EquivalenciaMedida.unidad).\
                join(MateriaPrima, MateriaPrima.tipo_medida == EquivalenciaMedida.id_equivalencia).\
                filter(MateriaPrima.id_materia == id_materia).scalar()
            return unidad
        except Exception as ex:
            # Maneja las excepciones de la consulta
            print(f"Error al obtener la unidad de medida: {ex}")
            return None

class ProveedorDAO:

    @classmethod
    def consultar_id_nombre_proveedores(cls):
        try:
            proveedores = Proveedor.query.all()
            resultados = []
            for proveedor in proveedores:
                resultado = {
                    'id_proveedor': proveedor.id_proveedor,
                    'nombre': proveedor.nombre
                }
                resultados.append(resultado)
            return resultados
        except Exception as ex:
            raise Exception(ex)
