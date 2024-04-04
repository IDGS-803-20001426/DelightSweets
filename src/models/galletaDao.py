from .Models import db, Galleta, Receta, RecetaMateriaIntermedia, MateriaPrima, Equivalencia, Venta, DetalleVenta,InventarioProductoTerminado
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
                    (Galleta.porcentaje_ganacia * func.SUM(RecetaMateriaIntermedia.cantidad * MateriaPrima.costo)) + func.SUM(RecetaMateriaIntermedia.cantidad * MateriaPrima.costo),
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
                Galleta.id_galleta, Galleta.nombre, Galleta.imagen, Galleta.porcentaje_ganacia, Equivalencia.piezas, Equivalencia.gramaje
            ).all()

            return resultado
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