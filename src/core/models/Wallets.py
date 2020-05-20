class Wallets:
    """
    class Ví
    :param id -> id của ví
        -> được generate từ mối liên hệ giữa public key và private key
        -> ví được khởi tạo cùng lúc với khi khởi tạo  p_k & pr_k
    :param utxo -> kiểu dữ liệu dạng mảng.
        -> mỗi utxo là class.
    """
    def __init__(self, id, utxo):
        self.id = id
        self.utxo = utxo