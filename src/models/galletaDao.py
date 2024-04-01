from .Models import db, Galleta, Receta, RecetaMateriaIntermedia, MateriaPrima, Equivalencia
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
            resultado = db.session.query(
                Galleta.id_galleta,
                Galleta.nombre,
                Galleta.imagen,
                func.ROUND((Galleta.porcentaje_ganacia * func.SUM(RecetaMateriaIntermedia.cantidad * MateriaPrima.costo)) + func.SUM(RecetaMateriaIntermedia.cantidad * MateriaPrima.costo), 1).label('costo_galleta'),
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
            ).group_by(
                Galleta.id_galleta, Galleta.nombre, Galleta.porcentaje_ganacia, Equivalencia.piezas, Equivalencia.gramaje
            ).all()

            return resultado
        except Exception as ex:
            raise Exception(ex)
