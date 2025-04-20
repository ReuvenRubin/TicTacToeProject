from flask import Flask, render_template, request, jsonify
from tic_tac_toe import TicTacToe
from ai_player import QLearningTicTacToe
from threading import Thread, Event
import time, atexit, signal, sys, os
from werkzeug.serving import is_running_from_reloader

app = Flask(__name__)
ai = QLearningTicTacToe()

INITIAL_TRAINING = 10000
CONTINUOUS_BATCH = 500
TRAINING_INTERVAL = 30
Q_TABLE_FILE = "q_table.json"

training_active = True
shutdown_event = Event()
initialized = False

def initialize_ai():
    """Initialize AI only once"""
    global initialized
    if initialized:
        return
        
    initialized = True
    print("\n=== AI INITIALIZATION ===")
    
    try:
        if os.path.exists(Q_TABLE_FILE):
            print("🔍 Loading Q-table...")
            ai.load_q_table(Q_TABLE_FILE)
            print(f"📊 Loaded {len(ai.q_table)} Q-values")
        else:
            print("🆕 No Q-table found")
        
        if not ai.q_table or len(ai.q_table) < 100:
            print(f"🏋️ Training {INITIAL_TRAINING} episodes...")
            ai.train(INITIAL_TRAINING)
            ai.save_q_table(Q_TABLE_FILE)
            print("✅ Training complete!")
            
        trainer_thread = Thread(target=background_trainer, daemon=True)
        trainer_thread.start()
        
    except Exception as e:
        print(f"❌ Initialization failed: {str(e)}")
        raise

def background_trainer():
    """Continuous training thread"""
    batch_count = 0
    print("\n🔄 Background trainer started")
    
    while training_active and not shutdown_event.is_set():
        try:
            batch_count += 1
            print(f"\n🏋️ Batch #{batch_count} - {CONTINUOUS_BATCH} episodes")
            start_time = time.time()
            
            ai.train(CONTINUOUS_BATCH)
            ai.save_q_table(Q_TABLE_FILE)
            
            elapsed = time.time() - start_time
            print(f"⏱️ Completed in {elapsed:.2f}s")
            print(f"💾 Saved {len(ai.q_table)} Q-values")
            
            wait_time = max(0, TRAINING_INTERVAL - elapsed)
            if wait_time > 0 and not shutdown_event.is_set():
                shutdown_event.wait(wait_time)
                
        except Exception as e:
            print(f"⚠️ Training error: {str(e)}")
            time.sleep(5)

def cleanup():
    """Guaranteed clean shutdown"""
    global training_active
    
    if not training_active:
        return
        
    print("\n=== SHUTDOWN ===")
    training_active = False
    shutdown_event.set()
    
    try:
        print("💾 Final Q-table save...")
        ai.save_q_table(Q_TABLE_FILE)
        print(f"✅ Saved {len(ai.q_table)} Q-values")
    except Exception as e:
        print(f"❌ Save failed: {str(e)}")
    
    time.sleep(0.5)
    print("🛑 Server stopped")
    sys.exit(0)

atexit.register(cleanup)
signal.signal(signal.SIGINT, lambda s, f: cleanup())
signal.signal(signal.SIGTERM, lambda s, f: cleanup())

@app.route("/")
def index():
    if not initialized:
        initialize_ai()
    board = [" "] * 9  
    return render_template("index.html", board=board)

@app.route("/move", methods=["POST"])
def make_move():
    data = request.get_json()
    board = data.get("board", [])
    ai_symbol = data.get("aiSymbol", "O")
    human_symbol = "X" if ai_symbol == "O" else "O"

    if check_winner(board, human_symbol):
        return jsonify({"board": board, "message": f"Player {human_symbol} wins!"})

    if check_winner(board, ai_symbol) or all(cell != ' ' for cell in board):
        return jsonify({"board": board, "message": "The game has ended!"})

    game = TicTacToe()
    game.board = board.copy()
    ai.play_ai_move(game, ai_symbol)

    if check_winner(game.board, ai_symbol):
        return jsonify({"board": game.board, "message": f"Player {ai_symbol} wins!"})
    elif all(cell != ' ' for cell in game.board):
        return jsonify({"board": game.board, "message": "It's a draw!"})

    return jsonify({"board": game.board})

def check_winner(board, player):
    win_patterns = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    return any(all(board[i] == player for i in pattern) for pattern in win_patterns)

if __name__ == "__main__":
    print("\n=== SERVER STARTING ===")
    try:
        if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
            initialize_ai()
        
        app.run(debug=True, use_reloader=False)
    except Exception as e:
        print(f"❌ Server error: {str(e)}")
        cleanup()