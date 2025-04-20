        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const cellSize = 100;
        let board = [" ", " ", " ", " ", " ", " ", " ", " ", " "];
        let gameOverFlag = false;
        let playerSymbol = 'X';
        let startingPlayer = 'player';
        let currentTurn;
        let animating = false;
        let gameStartTime;
        let gameDuration = 0;
        let timerInterval;
        let moveHistory = [];

        function startGame() {
            playerSymbol = document.getElementById('playerSymbol').value;
            startingPlayer = document.getElementById('startingPlayer').value;

            document.getElementById('gameSettings').style.display = 'none';
            document.getElementById('gameContainer').style.display = 'flex';
            resetGame();
        }

        function drawGrid() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.strokeStyle = currentTurn === "player" ? "#3498db" : "#e74c3c";
            ctx.lineWidth = 2;
            
            ctx.beginPath();
            ctx.moveTo(cellSize, 0);
            ctx.lineTo(cellSize, canvas.height);
            ctx.moveTo(cellSize * 2, 0);
            ctx.lineTo(cellSize * 2, canvas.height);
            ctx.moveTo(0, cellSize);
            ctx.lineTo(canvas.width, cellSize);
            ctx.moveTo(0, cellSize * 2);
            ctx.lineTo(canvas.width, cellSize * 2);
            ctx.stroke();
            
            ctx.strokeStyle = "black";
        }

        function drawStaticMarkers() {
            for (let i = 0; i < 9; i++) {
                const x = (i % 3) * cellSize + cellSize / 2;
                const y = Math.floor(i / 3) * cellSize + cellSize / 2;
                const marker = board[i];

                ctx.lineWidth = 4;
                ctx.strokeStyle = marker === "X" ? "#3498db" : "#e74c3c";

                if (marker === "X") {
                    ctx.beginPath();
                    ctx.moveTo(x - 30, y - 30);
                    ctx.lineTo(x + 30, y + 30);
                    ctx.moveTo(x + 30, y - 30);
                    ctx.lineTo(x - 30, y + 30);
                    ctx.stroke();
                } else if (marker === "O") {
                    ctx.beginPath();
                    ctx.arc(x, y, 30, 0, Math.PI * 2);
                    ctx.stroke();
                }
            }
        }

        function animateMarker(index, symbol) {
            if (animating) return;
            animating = true;
            
            const x = (index % 3) * cellSize + cellSize / 2;
            const y = Math.floor(index / 3) * cellSize + cellSize / 2;
            const duration = 300;
            const startTime = Date.now();
            
            const backgroundCanvas = document.createElement('canvas');
            backgroundCanvas.width = canvas.width;
            backgroundCanvas.height = canvas.height;
            const backgroundCtx = backgroundCanvas.getContext('2d');
            backgroundCtx.drawImage(canvas, 0, 0);
            
            const animate = () => {
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / duration, 1);
                
                ctx.clearRect(x-35, y-35, 70, 70);
                ctx.drawImage(backgroundCanvas, 0, 0);
                
                ctx.lineWidth = 4;
                ctx.strokeStyle = symbol === "X" ? "#3498db" : "#e74c3c";
                
                if (symbol === "X") {
                    ctx.beginPath();
                    ctx.moveTo(x - 30, y - 30);
                    ctx.lineTo(x - 30 + (60 * progress), y - 30 + (60 * progress));
                    ctx.moveTo(x + 30, y - 30);
                    ctx.lineTo(x + 30 - (60 * progress), y - 30 + (60 * progress));
                } else {
                    ctx.beginPath();
                    ctx.arc(x, y, 30 * progress, 0, Math.PI * 2);
                }
                ctx.stroke();
                
                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    animating = false;
                    board[index] = symbol;
                    updateBoard();
                }
            };
            
            animate();
        }

        function celebrate() {
            confetti({
                particleCount: 150,
                spread: 70,
                origin: { y: 0.6 },
                colors: ['#ff0000', '#00ff00', '#0000ff'],
                disableForReducedMotion: true
            });
        }

        function recordMove(player, position) {
            const row = Math.floor(position / 3) + 1;
            const col = (position % 3) + 1;
            const timestamp = new Date().toLocaleTimeString();
            
            moveHistory.push({
                player,
                position,
                notation: `${player} at (${row},${col})`,
                timestamp
            });
            
            updateHistoryUI();
        }

        function updateHistoryUI() {
            const historyList = document.getElementById('historyList');
            historyList.innerHTML = '';
            
            moveHistory.forEach((move, index) => {
                const entry = document.createElement('div');
                entry.className = `move-entry ${move.player === playerSymbol ? 'player' : 'ai'}`;
                entry.textContent = `#${index+1}: ${move.notation}`;
                historyList.appendChild(entry);
            });
            
            historyList.scrollTop = historyList.scrollHeight;
        }

        function startTimer() {
            gameStartTime = Date.now();
            timerInterval = setInterval(updateTimer, 1000);
        }

        function updateTimer() {
            gameDuration = Math.floor((Date.now() - gameStartTime) / 1000);
            document.getElementById('gameTimer').innerText = `Time: ${gameDuration}s`;
        }

        function stopTimer() {
            clearInterval(timerInterval);
        }

        canvas.addEventListener('click', function(event) {
            if (gameOverFlag || currentTurn !== "player" || animating) return;

            const x = event.offsetX;
            const y = event.offsetY;
            const row = Math.floor(y / cellSize);
            const col = Math.floor(x / cellSize);
            const index = row * 3 + col;

            if (board[index] === " ") {
                recordMove(playerSymbol, index);
                animateMarker(index, playerSymbol);
                setTimeout(() => {
                    checkGameStatus();
                    if (!gameOverFlag) {
                        currentTurn = "ai";
                        updateBoard();
                        setTimeout(aiMove, 1000);
                    }
                }, 350);
            }
        });

        function updateBoard() {
            drawGrid();
            drawStaticMarkers();
        }

        function aiMove() {
            const aiSymbol = playerSymbol === "X" ? "O" : "X";
            document.getElementById('ai-thinking').style.display = 'block';
            
            fetch('/move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ board: board, aiSymbol: aiSymbol })
            })
            .then(response => response.json())
            .then(data => {
                let moveIndex = -1;
                for (let i = 0; i < 9; i++) {
                    if (board[i] !== data.board[i]) {
                        moveIndex = i;
                        break;
                    }
                }
                
                board = data.board;
                document.getElementById('ai-thinking').style.display = 'none';
                
                if (moveIndex !== -1) {
                    recordMove(aiSymbol, moveIndex);
                    animateMarker(moveIndex, aiSymbol);
                    setTimeout(() => {
                        checkGameStatus();
                        if (!gameOverFlag) {
                            currentTurn = "player";
                            updateBoard();
                        }
                    }, 350);
                } else {
                    updateBoard();
                    checkGameStatus();
                }
            })
            .catch(error => {
                console.error("Error with AI move:", error);
                document.getElementById('ai-thinking').style.display = 'none';
            });
        }

        function checkGameStatus() {
            if (gameOverFlag) return;
            
            if (checkWinner(playerSymbol)) {
                gameOverFlag = true;
                setTimeout(() => {
                    celebrate();
                    alert(`Player ${playerSymbol} wins!`);
                    document.getElementById('resetButton').style.display = 'inline-block';
                    stopTimer();
                }, 500);
            } 
            else if (checkWinner(playerSymbol === "X" ? "O" : "X")) {
                gameOverFlag = true;
                setTimeout(() => {
                    alert(`Player ${playerSymbol === "X" ? "O" : "X"} wins!`);
                    document.getElementById('resetButton').style.display = 'inline-block';
                    stopTimer();
                }, 500);
            } 
            else if (board.every(cell => cell !== " ")) {
                gameOverFlag = true;
                setTimeout(() => {
                    alert("It's a draw!");
                    document.getElementById('resetButton').style.display = 'inline-block';
                    stopTimer();
                }, 500);
            }
        }

        function checkWinner(player) {
            const winPatterns = [
                [0, 1, 2], [3, 4, 5], [6, 7, 8],
                [0, 3, 6], [1, 4, 7], [2, 5, 8],
                [0, 4, 8], [2, 4, 6]
            ];
            for (let pattern of winPatterns) {
                if (pattern.every(index => board[index] === player)) {
                    highlightWinningPattern(pattern);
                    return true;
                }
            }
            return false;
        }

        function highlightWinningPattern(pattern) {
            ctx.strokeStyle = "gold";
            ctx.lineWidth = 6;
            ctx.beginPath();
            const start = pattern[0];
            const end = pattern[2];
            ctx.moveTo((start % 3) * cellSize + cellSize / 2, Math.floor(start / 3) * cellSize + cellSize / 2);
            ctx.lineTo((end % 3) * cellSize + cellSize / 2, Math.floor(end / 3) * cellSize + cellSize / 2);
            ctx.stroke();
        }

        function resetGame() {
            board = [" ", " ", " ", " ", " ", " ", " ", " ", " "];
            gameOverFlag = false;
            currentTurn = startingPlayer;
            moveHistory = [];
            document.getElementById('resetButton').style.display = 'none';
            stopTimer();
            startTimer();
            updateBoard();
            updateHistoryUI();

            if (currentTurn === "ai") {
                setTimeout(aiMove, 500);
            }
        }

        updateBoard();