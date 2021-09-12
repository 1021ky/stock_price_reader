from dataclasses import dataclass

from datetime import datetime


@dataclass(init=True, repr=True, frozon=True)
class StockInfo:
    code: str  # 銘柄コード
    unit: int  # 売買単位


@dataclass(init=True, repr=True, frozon=True)
class StockPrice:
    open: float
    close: float
    high: float
    low: float
    volume: float


@dataclass(init=True, repr=True, frozon=True)
class StockMarketPrice:
    # ある時点の株価
    datetime: datetime
    info: StockInfo
    price: StockPrice


@dataclass(init=True, repr=True, frozon=True)
class Order:
    datetime: datetime
    order_stock: StockMarketPrice
    stockprice: StockPrice
    unit_count: int  # 購入単位数

    @property
    def total_number(self) -> int:
        return self.order_stock.info.unit * self.unit_count

    @property
    def total_amount(self) -> int:
        return int(self.order_stock.price.close * self.total_number)


@dataclass(init=True, repr=True, frozon=True)
class Trade:
    balance: int  # 購入前の残高
    order: Order

    @property
    def fee(self) -> int:
        """約定手数料計算(楽天証券の場合）"""
        total = self.order.total_amount
        if total <= 50000:
            return 54
        elif total <= 100000:
            return 97
        elif total <= 200000:
            return 113
        elif total <= 500000:
            return 270
        elif total <= 1000000:
            return 525
        elif total <= 1500000:
            return 628
        elif total <= 30000000:
            return 994
        else:
            return 1050

    @property
    def rest_balance(self) -> int:
        return self.balance - self.order.total_amount - self.fee


@dataclass(init=True, repr=True, frozon=True)
class TradeParam:
    trade_range: range
    deposit: int
    minimumStockPrice: int
    minimumStockVolume: int
