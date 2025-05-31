from datetime import date, time
from sqlalchemy import String, Date, Time, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Daily(Base):
    __tablename__ = "daily"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    ticker: Mapped[str] = mapped_column(String)
    per: Mapped[str] = mapped_column(String)
    date_: Mapped[date] = mapped_column(Date, name="date")
    time_: Mapped[time] = mapped_column(Time, name="time")
    open_: Mapped[float] = mapped_column(Float, name="open")
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close_: Mapped[float] = mapped_column(Float, name="close")
    vol: Mapped[str] = mapped_column(String)

    def __repr__(self) -> str:
        return f"Daily Entry(ticker={self.ticker!r}, date={self.date_!r}, open={self.open_!r}, close={self.close_!r})"
