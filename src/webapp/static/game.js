// Infinite Connections — Game Logic

let state = {
    puzzleId: null,
    words: [],           // remaining unsolved words
    selected: new Set(),
    solvedGroups: [],
    mistakesLeft: 4,
    gameOver: false,
};

// ── Initialization ─────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', loadNewPuzzle);

async function loadNewPuzzle() {
    // Reset state
    state = {
        puzzleId: null,
        words: [],
        selected: new Set(),
        solvedGroups: [],
        mistakesLeft: 4,
        gameOver: false,
    };

    hideMessage();
    document.getElementById('solved-groups').innerHTML = '';
    document.getElementById('game-over').classList.add('hidden');
    document.getElementById('mistakes-count').textContent = '4';
    document.getElementById('mistake-dots').innerHTML = '&#9679; &#9679; &#9679; &#9679;';

    try {
        const resp = await fetch('/api/puzzle/random');
        const data = await resp.json();
        if (data.error) {
            showMessage('No puzzles available. Generate some first!', 'wrong');
            return;
        }
        state.puzzleId = data.id;
        state.words = [...data.words];
        renderGrid();
    } catch (e) {
        showMessage('Failed to load puzzle', 'wrong');
    }
}

// ── Rendering ──────────────────────────────────────────────────────────────

function renderGrid() {
    const grid = document.getElementById('grid');
    grid.innerHTML = '';

    state.words.forEach(word => {
        const tile = document.createElement('div');
        tile.className = 'tile' + (state.selected.has(word) ? ' selected' : '');
        tile.textContent = word;
        tile.onclick = () => toggleWord(word);
        if (state.gameOver) tile.classList.add('disabled');
        grid.appendChild(tile);
    });

    updateSubmitButton();
}

function updateSubmitButton() {
    document.getElementById('btn-submit').disabled =
        state.selected.size !== 4 || state.gameOver;
}

// ── Interactions ───────────────────────────────────────────────────────────

function toggleWord(word) {
    if (state.gameOver) return;

    if (state.selected.has(word)) {
        state.selected.delete(word);
    } else if (state.selected.size < 4) {
        state.selected.add(word);
    }
    renderGrid();
}

function deselectAll() {
    state.selected.clear();
    renderGrid();
    hideMessage();
}

function shuffleWords() {
    for (let i = state.words.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [state.words[i], state.words[j]] = [state.words[j], state.words[i]];
    }
    renderGrid();
    hideMessage();
}

// ── Guessing ───────────────────────────────────────────────────────────────

async function submitGuess() {
    if (state.selected.size !== 4 || state.gameOver) return;

    const guess = [...state.selected];

    try {
        const resp = await fetch(`/api/puzzle/${state.puzzleId}/check`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ words: guess }),
        });
        const data = await resp.json();

        if (data.correct) {
            handleCorrectGuess(data);
        } else if (data.one_away) {
            showMessage('One away!', 'one-away');
            handleWrongGuess();
        } else {
            showMessage('Incorrect', 'wrong');
            handleWrongGuess();
        }
    } catch (e) {
        showMessage('Error checking guess', 'wrong');
    }
}

function handleCorrectGuess(data) {
    showMessage(`${data.category}!`, 'correct');

    // Remove solved words from the grid
    const solvedWords = new Set(data.words.map(w => w.toUpperCase()));
    state.words = state.words.filter(w => !solvedWords.has(w.toUpperCase()));
    state.selected.clear();

    // Add solved group display
    state.solvedGroups.push(data);
    renderSolvedGroup(data);
    renderGrid();

    // Check for win
    if (state.solvedGroups.length === 4) {
        setTimeout(() => endGame(true), 600);
    }
}

function handleWrongGuess() {
    state.mistakesLeft--;
    document.getElementById('mistakes-count').textContent = state.mistakesLeft;

    const dots = [];
    for (let i = 0; i < state.mistakesLeft; i++) dots.push('&#9679;');
    document.getElementById('mistake-dots').innerHTML = dots.join(' ');

    if (state.mistakesLeft <= 0) {
        endGame(false);
    }
}

function renderSolvedGroup(data) {
    const container = document.getElementById('solved-groups');
    const div = document.createElement('div');
    div.className = `solved-group ${data.color}`;
    div.innerHTML = `
        <div class="category">${data.category}</div>
        <div class="words">${data.words.join(', ')}</div>
    `;
    container.appendChild(div);
}

// ── Game Over ──────────────────────────────────────────────────────────────

function endGame(won) {
    state.gameOver = true;
    renderGrid();

    if (won) {
        document.getElementById('game-over-text').textContent = 'Congratulations!';
    } else {
        document.getElementById('game-over-text').textContent = 'Better luck next time!';
        revealAnswer();
    }
    document.getElementById('game-over').classList.remove('hidden');
}

async function revealAnswer() {
    if (!state.puzzleId) return;

    try {
        const resp = await fetch(`/api/puzzle/${state.puzzleId}/reveal`);
        const data = await resp.json();

        // Show all unsolved groups
        const solvedCats = new Set(state.solvedGroups.map(g => g.category));
        for (const group of data.groups) {
            if (!solvedCats.has(group.category)) {
                renderSolvedGroup(group);
            }
        }

        // Clear remaining grid
        state.words = [];
        state.gameOver = true;
        renderGrid();
    } catch (e) {
        showMessage('Failed to reveal answer', 'wrong');
    }
}

// ── Messages ───────────────────────────────────────────────────────────────

function showMessage(text, type) {
    const bar = document.getElementById('message-bar');
    bar.textContent = text;
    bar.className = `message-bar ${type}`;
    setTimeout(() => hideMessage(), 2500);
}

function hideMessage() {
    document.getElementById('message-bar').classList.add('hidden');
}
