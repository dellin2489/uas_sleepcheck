from sqlmodel import Session, select

from app.models.prediction import Prediction


def get_all(session: Session):
    """Ambil semua prediksi, urut terbaru di atas."""
    statement = select(Prediction).order_by(Prediction.created_at.desc())
    return session.exec(statement).all()


def delete_prediction(session: Session, prediction_id: int) -> bool:
    """Hapus satu prediksi. Return True jika data ada dan terhapus."""
    item = session.get(Prediction, prediction_id)
    if item is None:
        return False
    session.delete(item)
    session.commit()
    return True
