class EmaFilter:
    """Simple exponential moving average (EMA) filter for smoothing scalar signals.

    y_t = alpha * x_t + (1 - alpha) * y_{t-1}
    where alpha in (0, 1]; higher alpha follows input faster.
    """

    def __init__(self, alpha: float = 0.3):
        self.alpha = max(0.001, min(1.0, alpha))
        self._y = None

    def reset(self):
        self._y = None

    def update(self, x: float) -> float:
        if self._y is None:
            self._y = x
        else:
            a = self.alpha
            self._y = a * x + (1.0 - a) * self._y
        return self._y