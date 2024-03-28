from .Models import Receta

class RecetaDAO:
    @staticmethod
    def obtener_todas_las_recetas():
        return Receta.query.all()
