from simulator.domain.model import Trade


class Portfolio:
    def __init__(self) -> None:
        self._tradelist: list[Trade] = []

    def __repr__(self) -> str:
        s = []
        for trade in self._tradelist:
            s.append(str(trade))
        return "".join(s)

    def record_trade(self, trade: Trade) -> None:
        self._tradelist.append(trade)
