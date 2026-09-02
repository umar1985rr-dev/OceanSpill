class EarlyStopping:

    def __init__(
        self,
        patience=5,
        min_delta=0.0
    ):

        self.patience = patience
        self.min_delta = min_delta

        self.counter = 0
        self.best_loss = float("inf")

    def should_stop(
        self,
        val_loss
    ):

        if val_loss < self.best_loss - self.min_delta:

            self.best_loss = val_loss
            self.counter = 0

            return False

        self.counter += 1

        return self.counter >= self.patience