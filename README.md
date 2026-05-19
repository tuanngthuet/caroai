# Caro AI

Chuyển thể từ game gomoku 5, game này là biến thể khi người chơi sẽ thắng khi có hàng 4 theo chiều ngang, dọc và chéo.
Bài toán sử dụng các thuật toán: Minimax, Alpha-beta pruning và một số thuật toán để tăng hiệu năng (Move ordering, iterative deepening, v.v)

---

## Khởi động nhanh

```bash
pip install pygame
python main.py
```

---

## Cấu trúc dự án

| Đường dẫn | Vai trò |
|-----------|---------|
| `main.py` | Điểm khởi chạy — chạy `python main.py` từ thư mục gốc |
| `core/` | Hằng số toàn cục (`constants.py`) và trạng thái ván đấu (`game_state.py`) |
| `game/` | Luật chơi (`rules.py`) và quản lý ván đấu (`game_manager.py`) |
| `ai/agents/` | Agent Easy (Minimax) và Medium (Alpha-Beta) |
| `ai/algorithms/` | Cài đặt thuật toán minimax và alphabeta |
| `ai/evaluation/` | Hàm đánh giá bàn cờ toàn cục |
| `ai/heuristics/` | Sắp xếp nước đi (move ordering) |
| `ui/menu/` | Menu chính |
| `ui/screens/` | Màn hình chơi, benchmark, phân tích |
| `ui/renderer/` | Vẽ bàn cờ |
| `ui/hud/` | Bảng thông tin bên phải |
| `ui/components/` | Popup kết thúc ván |
| `ui/animations/` | Hiệu ứng đặt quân, thắng |
| `benchmark/` | Chạy trận AI vs AI và xuất kết quả |

---

## Tính năng

| Tính năng | Chi tiết |
|-----------|---------|
| Bàn cờ | 15×15, thắng khi có 4 quân liên tiếp |
| Chế độ Easy | Minimax, độ sâu 3 |
| Chế độ Medium | Alpha-Beta Pruning, độ sâu 4 |
| Hoàn tác | Nút **Undo** lùi lại 1 lượt (cả nước AI lẫn người chơi) |
| Benchmark | Chọn thuật toán, độ sâu, số ván — xem kết quả từng nước theo thời gian thực |
| Phân tích | Tự đặt trạng thái bàn cờ, chọn AI, nhấn **Move** để AI tính nước |
| Giao diện | Chủ đề tối hiện đại, hiệu ứng hover, animation đặt quân, đường thắng |

---

## Điều khiển

### Chơi thường
- **Click chuột trái** vào ô để đặt quân (X)
- AI (O) tự động đi sau
- **← Menu** — quay về menu chính
- **↩ Restart** — chơi lại từ đầu
- **⎌ Undo** — hoàn tác nước vừa đi (lùi 1 lượt đầy đủ)

![Chơi thường](https://github.com/tuanngthuet/24020347_23021237_CaroAI/blob/main/image/Play1.png)

![Chơi thường]([https://github.com/tuanngthuet/24020347_23021237_CaroAI/blob/main/image/play2.png)

### Benchmark
1. Từ menu chính chọn **BENCHMARK**
2. Cấu hình Agent X và Agent O (thuật toán + độ sâu)
3. Chọn số ván đấu (1 / 3 / 5 / 10)
4. Nhấn **▶ Run Benchmark**
5. Xem bàn cờ trực tiếp từng nước, kết quả xuất theo định dạng:

```
completion_index=1
game_seq=1
match_id=minimax_d3_vs_alphabeta_d4__game_1
winner=alphabeta_d4
agent_x={...}
agent_o={...}
result_for_agent_x=loss
result_for_agent_o=win
Final board:
. . X O ...
```
![Benchmark](https://github.com/tuanngthuet/24020347_23021237_CaroAI/blob/main/image/Benchmark2.png)
![Benchmark](https://github.com/tuanngthuet/24020347_23021237_CaroAI/blob/main/image/Benchmark1.png)

### Phân tích (Analysis)
1. Từ menu chính chọn **ANALYSIS**
2. **Click trái** vào ô để đặt quân (lần lượt: trống → X → O → trống)
3. **Click phải** để xóa ô
4. Chọn AI đi bên nào (X hoặc O), thuật toán và độ sâu ở thanh bên phải
5. Nhấn **▶ Move** để AI tính và đi một nước
6. Nhấn **Clear** để xóa toàn bộ bàn cờ

---

![Analyst](https://github.com/tuanngthuet/24020347_23021237_CaroAI/blob/main/image/Analyst.png)

## Kiến trúc AI

### Easy — Minimax (độ sâu 3)
Minimax thuần túy có sắp xếp nước đi. Duyệt toàn bộ cây tìm kiếm không cắt tỉa.

### Medium — Alpha-Beta (độ sâu 4)
Alpha-Beta Pruning kết hợp **iterative deepening** — tìm kiếm từ độ sâu 1 đến độ sâu đích, dùng nước tốt nhất của vòng trước để sắp xếp nước đi ở vòng sau, giúp cắt tỉa hiệu quả hơn.

### Sắp xếp nước đi (Move Ordering)
Ưu tiên theo thứ tự:
1. Nước thắng ngay lập tức của AI
2. Nước chặn thắng ngay của đối thủ
3. Điểm tấn công + phòng thủ kết hợp

### Hàm đánh giá
Quét toàn bộ bàn cờ theo 4 hướng, đếm từng chuỗi quân một lần duy nhất, phân biệt **đầu mở** và **đầu bị chặn**:

| Mẫu | Điểm AI | Điểm đối thủ |
|-----|---------|--------------|
| 4 quân, 2 đầu mở | +100,000 (thắng) | −100,000 |
| 4 quân, 1 đầu mở | +50,000 | −45,000 |
| 3 quân, 2 đầu mở | +5,000 | −4,000 |
| 3 quân, 1 đầu mở | +500 | −400 |
| 2 quân, 2 đầu mở | +200 | −150 |

---

## Yêu cầu

- Python 3.10+
- pygame

```bash
pip install -r requirements.txt
```

---

## Tags

#Caro #CaroAI #Python #Pygame #Minimax #AlphaBeta #TTNT
