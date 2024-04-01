from .Models import Receta,SolicitudProduccion,InventarioProductoTerminado,Equivalencia,Inventario
from datetime import datetime
from sqlalchemy import text

class ProduccionDAO:
    def obtenerRecetasConSolicitudes(db):
        query = db.session.query(SolicitudProduccion.id_solicitud,Receta.nombre_receta,Receta.id_galleta, SolicitudProduccion.fecha_solicitud, SolicitudProduccion.estatus)\
            .join(SolicitudProduccion, Receta.id_receta == SolicitudProduccion.id_receta)
        results = query.all()
        return results
    
    def obtenerEstatusPorId(db, id_solicitud):
        query = db.session.query(SolicitudProduccion.estatus).filter(SolicitudProduccion.id_solicitud == id_solicitud).first()
        if query:
            return query[0]
        else:
            return None  

    def obtenerSolicitudPorID(db, id_solicitud):
        solicitud = db.session.query(SolicitudProduccion, Receta)\
                            .join(Receta, SolicitudProduccion.id_receta == Receta.id_receta)\
                            .filter(SolicitudProduccion.id_solicitud == id_solicitud)\
                            .first()
        return solicitud

    def actualizarEstatusYFecha(db, id_solicitud,estatus):
        try:
            solicitud = SolicitudProduccion.query.filter_by(id_solicitud=id_solicitud).first()
            if solicitud:
                # Actualizar estatus y fecha
                solicitud.estatus = estatus
                solicitud.fecha_terminacion = datetime.now()  # Actualizar la fecha a la actual
                db.session.commit()
                return True
            else:
                return False  # Si no se encuentra la solicitud
        except Exception as e:
            print(f"Error al actualizar estatus y fecha: {e}")
            db.session.rollback()
            return False
        
    def insertarRegistroInventarioProductoTerminado(db, id_galleta, cantidad,estatus):
        try:
            # Crear una nueva instancia de InventarioProductoTerminado con los valores proporcionados
            nuevo_registro = InventarioProductoTerminado(
                id_galleta=id_galleta,
                fecha_produccion=datetime.now(),  # Obtener la fecha y hora actual
                cantidad=cantidad,
                estatus=estatus
            )
            # Agregar el nuevo registro a la sesión y confirmar los cambios
            db.session.add(nuevo_registro)
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error al insertar registro en el inventario de producto terminado: {e}")
            db.session.rollback()
            return False
        
    def obtenerNumeroPiezasPorReceta(db, id_receta):
        query = db.session.query(Equivalencia.piezas).filter(Equivalencia.id_receta == id_receta).first()
        if query:
            return query[0]  # Devuelve el número de piezas
        else:
            return None  # Retorna None si no se encuentra la receta con el ID dado

    def obtenerMateriasPrimasPorReceta(db, id_receta):
        query = text("""
                SELECT r.id_materia, r.cantidad 
                FROM proyectGalleta.receta_materia_intermedia r
                JOIN proyectGalleta.materia_prima m ON m.id_materia = r.id_materia
                WHERE r.id_receta = :id_receta
                """)
        result = db.session.execute(query, {'id_receta': id_receta})
        materias = result.fetchall()
        return materias
    
    def obtenerMateriasPrimasInventario(db, id_materia):
        query = db.session.query(Inventario)\
                .filter_by(id_materia=id_materia)\
                .order_by(Inventario.fecha_caducidad)
        inventario = query.all()
        return inventario
    
    