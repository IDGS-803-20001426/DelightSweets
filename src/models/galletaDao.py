from .Models import Galleta

class GalletaDAO:

    @classmethod
    def get_all(cls):
        try:
            return Galleta.query.all()
        except Exception as ex:
            raise Exception(ex)
