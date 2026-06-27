/**
 * ПОКЕМОН-БАТТЛ 2.0: Клиентское приложение (Oracle RPG)
 * Регистрация, Профиль, Редактор, Пасхалка таблицы умножения, Ловля, Эволюция, Elo
 */

const state = {
    user: null,
    profile: null,
    battleId: null,
    battleState: null,
    selectedAttackerId: null,
    selectedTargetId: null,
    pollingTimer: null,
    mathNum1: 7,
    mathNum2: 8,
    mathStreak: 0
};

const ELEMENT_META = {
    FIRE: { icon: '🔥', name: 'Огонь', class: 'avatar-fire' },
    GRASS: { icon: '🌿', name: 'Трава', class: 'avatar-grass' },
    WATER: { icon: '💧', name: 'Вода', class: 'avatar-water' },
    EARTH: { icon: '⛰️', name: 'Земля', class: 'avatar-earth' }
};

const CREATURE_ICONS = {
    'Игнизавр': '🦎', 'Инфернозавр': '🐉', 'Дракопир': '🐲',
    'Пироликс': '🦊', 'Вулканикс': '🔥',
    'Листокрыл': '🦋', 'Флораптерикс': '🦅', 'Сильванозавр': '🦕',
    'Флоразавр': '🦏', 'Древозавр': '🌳',
    'Аквадонт': '🐢', 'Левиадон': '🐍', 'Океанор': '🐋',
    'Гидрошторм': '🐬', 'Цунамикс': '🌊',
    'Террагот': '🗿', 'Титанорок': '🦣', 'Геоколосс': '⛰️',
    'Сейсморог': '🦬', 'Магмарог': '🌋'
};

function getCreatureIcon(name, element) {
    for (const [key, icon] of Object.entries(CREATURE_ICONS)) {
        if (name.includes(key)) return icon;
    }
    return ELEMENT_META[element]?.icon || '👾';
}

// =========================================================================
// ИНИЦИАЛИЗАЦИЯ
// =========================================================================
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    checkStoredSession();
});

function initEventListeners() {
    // Вход и регистрация
    document.getElementById('form-login').addEventListener('submit', handleLogin);
    document.getElementById('form-register').addEventListener('submit', handleRegister);
    document.getElementById('btn-logout').addEventListener('click', handleLogout);

    // Навигация по вкладкам
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const targetScreen = tab.getAttribute('data-tab');
            switchNavTab(targetScreen);
        });
    });

    // Стартовый покемон в регистрации (стили радиокнопок)
    document.querySelectorAll('.starter-choice input').forEach(input => {
        input.addEventListener('change', () => {
            document.querySelectorAll('.starter-choice').forEach(c => c.classList.remove('selected'));
            input.closest('.starter-choice').classList.add('selected');
        });
    });

    // Лобби
    document.getElementById('btn-create-battle').addEventListener('click', createBattle);
    document.getElementById('btn-bot-battle').addEventListener('click', createBotBattle);
    document.getElementById('btn-refresh-battles').addEventListener('click', loadBattlesList);

    // Боевая арена
    document.getElementById('btn-action-attack').addEventListener('click', executeAttack);
    document.getElementById('btn-action-heal').addEventListener('click', useHealItem);
    const btnSurrenderHeader = document.getElementById('btn-surrender-battle');
    if (btnSurrenderHeader) btnSurrenderHeader.addEventListener('click', surrenderBattle);
    const btnSurrenderAction = document.getElementById('btn-action-surrender');
    if (btnSurrenderAction) btnSurrenderAction.addEventListener('click', surrenderBattle);
    document.getElementById('btn-leave-battle').addEventListener('click', leaveBattle);
    document.getElementById('btn-gameover-return').addEventListener('click', returnToLobby);

    // Алтарь ловли
    document.getElementById('btn-do-catch').addEventListener('click', doCatchCreature);

    // Пасхалка: таблица умножения
    document.getElementById('form-math').addEventListener('submit', handleMathSubmit);
}

// Переключение Вход / Регистрация
function switchAuthTab(tab) {
    const tabLogin = document.getElementById('tab-auth-login');
    const tabReg = document.getElementById('tab-auth-register');
    const paneLogin = document.getElementById('pane-login');
    const paneReg = document.getElementById('pane-register');
    const statusBox = document.getElementById('login-status-box');
    statusBox.classList.add('hidden');

    if (tab === 'login') {
        tabLogin.classList.add('active');
        tabReg.classList.remove('active');
        paneLogin.classList.add('active');
        paneReg.classList.remove('active');
    } else {
        tabLogin.classList.remove('active');
        tabReg.classList.add('active');
        paneLogin.classList.remove('active');
        paneReg.classList.add('active');
    }
}

// Навигация главного меню
function switchNavTab(screenId) {
    document.querySelectorAll('.nav-tab').forEach(t => {
        if (t.getAttribute('data-tab') === screenId) t.classList.add('active');
        else t.classList.remove('active');
    });

    showScreen(screenId);

    // Загрузка данных для выбранного экрана
    if (screenId === 'screen-lobby') loadLobbyData();
    else if (screenId === 'screen-profile') loadProfileData();
    else if (screenId === 'screen-editor') loadEditorData();
    else if (screenId === 'screen-catch') loadCatchAltarData();
    else if (screenId === 'screen-leaderboard') loadLeaderboard();
    else if (screenId === 'screen-math') loadMathChallenge();
}

function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    const target = document.getElementById(screenId);
    if (target) target.classList.add('active');
}

function setQuickLogin(username, password) {
    document.getElementById('input-username').value = username;
    document.getElementById('input-password').value = password;
}

// =========================================================================
// АУТЕНТИФИКАЦИЯ И РЕГИСТРАЦИЯ
// =========================================================================
async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('input-username').value.trim();
    const password = document.getElementById('input-password').value.trim();
    const statusBox = document.getElementById('login-status-box');

    statusBox.className = 'status-box';
    statusBox.textContent = 'Подключение к Oracle DB и проверка роли GAME_PLAYER_ROLE...';
    statusBox.classList.remove('hidden');

    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await res.json();
        if (!res.ok || !data.success) {
            statusBox.className = 'status-box error';
            statusBox.textContent = data.message || data.detail || 'Ошибка аутентификации';
            return;
        }

        onAuthSuccess(data);
    } catch (err) {
        statusBox.className = 'status-box error';
        statusBox.textContent = 'Ошибка подключения: ' + err.message;
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('reg-username').value.trim();
    const displayName = document.getElementById('reg-display-name').value.trim();
    const password = document.getElementById('reg-password').value.trim();
    const starterId = parseInt(document.querySelector('input[name="starter_elem"]:checked').value);
    const statusBox = document.getElementById('login-status-box');

    statusBox.className = 'status-box';
    statusBox.textContent = 'Создание учетной записи в Oracle DB и назначение роли GAME_PLAYER_ROLE...';
    statusBox.classList.remove('hidden');

    try {
        const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username,
                password,
                display_name: displayName,
                starter_template_id: starterId
            })
        });
        const data = await res.json();
        if (!res.ok || !data.success) {
            statusBox.className = 'status-box error';
            statusBox.textContent = data.detail || data.message || 'Ошибка регистрации';
            return;
        }

        onAuthSuccess(data);
    } catch (err) {
        statusBox.className = 'status-box error';
        statusBox.textContent = 'Ошибка соединения: ' + err.message;
    }
}

function onAuthSuccess(userData) {
    state.user = userData;
    localStorage.setItem('pokemon_rpg_user', JSON.stringify(userData));
    updateHeaderUser();
    document.getElementById('main-nav').classList.remove('hidden');
    switchNavTab('screen-lobby');
}

function updateHeaderUser() {
    const headerInfo = document.getElementById('header-user-info');
    if (state.user) {
        document.getElementById('header-username').textContent = `${state.user.display_name} (${state.user.username})`;
        headerInfo.classList.remove('hidden');
        loadProfileSummary();
    } else {
        headerInfo.classList.add('hidden');
        document.getElementById('main-nav').classList.add('hidden');
    }
}

async function loadProfileSummary() {
    if (!state.user) return;
    try {
        const res = await fetch(`/api/player/${state.user.player_id}/profile`);
        if (!res.ok) return;
        const prof = await res.json();
        state.profile = prof;
        document.getElementById('header-coins').textContent = prof.coins;
        document.getElementById('header-elo').textContent = prof.elo_rating;
    } catch (e) {}
}

function handleLogout() {
    stopPolling();
    state.user = null;
    state.profile = null;
    state.battleId = null;
    localStorage.removeItem('pokemon_rpg_user');
    updateHeaderUser();
    showScreen('screen-login');
}

function checkStoredSession() {
    const saved = localStorage.getItem('pokemon_rpg_user');
    if (saved) {
        try {
            state.user = JSON.parse(saved);
            updateHeaderUser();
            document.getElementById('main-nav').classList.remove('hidden');
            switchNavTab('screen-lobby');
        } catch (e) {
            localStorage.removeItem('pokemon_rpg_user');
        }
    }
}

// =========================================================================
// ЭКРАН 1: ЛОББИ БОЕВ
// =========================================================================
async function loadLobbyData() {
    await Promise.all([
        loadMyTeam(),
        loadBattlesList()
    ]);
}

async function loadMyTeam() {
    if (!state.user) return;
    try {
        const res = await fetch(`/api/player/${state.user.player_id}/creatures`);
        const creatures = await res.json();
        const container = document.getElementById('my-team-container');

        const activeTeam = creatures.filter(c => c.is_in_team === 1 || c.is_in_team === true);
        if (!activeTeam || activeTeam.length === 0) {
            container.innerHTML = '<div class="empty-state">Нет существ в активной команде. Настройте их во вкладке «Редактор Команды»!</div>';
            return;
        }

        container.innerHTML = activeTeam.map(c => {
            const meta = ELEMENT_META[c.element_id] || { icon: '⚡', class: 'avatar-fire' };
            const icon = getCreatureIcon(c.nickname || c.template_name, c.element_id);
            return `
                <div class="creature-card">
                    <div class="creature-avatar ${meta.class}">
                        ${icon}
                    </div>
                    <div class="creature-info">
                        <div class="creature-title-row">
                            <span class="creature-name">${c.nickname || c.template_name}</span>
                            <span class="elem-badge ${c.element_id}">${c.element_id}</span>
                        </div>
                        <div class="creature-stats-row">
                            <span>Ур. ${c.level}</span>
                            <span>HP ${c.current_hp}/${c.max_hp}</span>
                            <span>⚔️ ${c.attack}</span>
                            <span>🛡️ ${c.defense}</span>
                            <span>⚡ ${c.speed}</span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    } catch (e) {
        console.error('Ошибка загрузки команды:', e);
    }
}

async function loadBattlesList() {
    try {
        const res = await fetch('/api/battles');
        const battles = await res.json();
        const container = document.getElementById('battles-list');

        if (!battles || battles.length === 0) {
            container.innerHTML = '<div class="empty-state">Нет открытых боев. Нажмите «Создать PvP-бой»!</div>';
            return;
        }

        container.innerHTML = battles.map(b => {
            const isMyBattle = state.user && (b.player1_id === state.user.player_id || b.player2_id === state.user.player_id);
            const canJoin = state.user && b.status === 'WAITING' && b.player1_id !== state.user.player_id;
            const statusClass = b.status === 'WAITING' ? 'WAITING' : 'IN_PROGRESS';
            const statusLabel = b.status === 'WAITING' ? 'Ожидание соперника' : 'Идет бой';

            let actionBtn = '';
            if (canJoin) {
                actionBtn = `<button class="btn-sm btn-primary" onclick="joinBattle(${b.battle_id})">Принять бой ⚔️</button>`;
            } else if (isMyBattle) {
                actionBtn = `<button class="btn-sm btn-outline" onclick="openBattle(${b.battle_id})">Войти в бой →</button>`;
            } else {
                actionBtn = `<span class="text-dim text-sm">Занят</span>`;
            }

            return `
                <div class="battle-row">
                    <div class="battle-row-info">
                        <strong>#${b.battle_id}</strong>
                        <span>Создатель: <b>${b.p1_name || 'Игрок'}</b></span>
                        <span class="status-pill ${statusClass}">${statusLabel}</span>
                    </div>
                    <div>${actionBtn}</div>
                </div>
            `;
        }).join('');
    } catch (e) {
        console.error('Ошибка списка боев:', e);
    }
}

async function createBattle() {
    if (!state.user) return;
    try {
        const res = await fetch('/api/battles/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player_id: state.user.player_id, battle_type: "PVP" })
        });
        const data = await res.json();
        openBattle(data.battle_id);
    } catch (e) {
        alert('Ошибка: ' + e.message);
    }
}

async function createBotBattle() {
    if (!state.user) return;
    try {
        const res = await fetch('/api/battles/bot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player_id: state.user.player_id })
        });
        const data = await res.json();
        openBattle(data.battle_id);
    } catch (e) {
        alert('Ошибка запуска PvE: ' + e.message);
    }
}

async function joinBattle(battleId) {
    if (!state.user) return;
    try {
        const res = await fetch(`/api/battles/${battleId}/join`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player_id: state.user.player_id })
        });
        const data = await res.json();
        if (!res.ok) {
            alert(data.detail || 'Не удалось присоединиться');
            return;
        }
        openBattle(battleId);
    } catch (e) {
        alert('Ошибка: ' + e.message);
    }
}

// =========================================================================
// ЭКРАН 2: ПРОФИЛЬ, ИНВЕНТАРЬ И ОТКРЫТЫЕ ГЕРОИ
// =========================================================================
async function loadProfileData() {
    if (!state.user) return;
    try {
        const [profRes, invRes, heroesRes] = await Promise.all([
            fetch(`/api/player/${state.user.player_id}/profile`),
            fetch(`/api/player/${state.user.player_id}/inventory`),
            fetch(`/api/creatures`)
        ]);

        const prof = await profRes.json();
        const inv = await invRes.json();
        const allHeroes = await heroesRes.json();
        state.profile = prof;

        // Заполняем данные тренера
        document.getElementById('prof-display-name').textContent = prof.display_name;
        document.getElementById('prof-level').textContent = prof.level;
        document.getElementById('prof-exp-text').textContent = `${prof.exp} / ${prof.exp_needed}`;
        document.getElementById('prof-exp-percent').textContent = `${prof.exp_percent}%`;
        document.getElementById('prof-exp-fill').style.width = `${prof.exp_percent}%`;

        document.getElementById('prof-elo').textContent = prof.elo_rating;
        document.getElementById('prof-coins').textContent = prof.coins;
        document.getElementById('prof-battles').textContent = `${prof.battles_won} / ${prof.battles_lost}`;
        document.getElementById('prof-winrate').textContent = `${prof.win_rate}%`;
        document.getElementById('prof-season-badge').textContent = prof.season_rank;
        document.getElementById('prof-unlocked-count').textContent = prof.unlocked_heroes_count;

        // Инвентарь
        const invContainer = document.getElementById('profile-inventory-list');
        if (!inv || inv.length === 0) {
            invContainer.innerHTML = '<div class="empty-state">Инвентарь пуст</div>';
        } else {
            invContainer.innerHTML = inv.map(it => `
                <div class="inventory-item">
                    <div>
                        <strong>${it.item_type === 'EVO_STONE' ? '💎' : '🧪'} ${it.name}</strong>
                        <div class="text-dim text-sm">${it.description}</div>
                    </div>
                    <span class="item-qty">x${it.quantity}</span>
                </div>
            `).join('');
        }

        // Древо разблокированных героев
        const heroesContainer = document.getElementById('unlocked-heroes-grid');
        heroesContainer.innerHTML = allHeroes.map(h => {
            const isUnlocked = prof.level >= h.unlock_level;
            const meta = ELEMENT_META[h.element_id] || { icon: '⚡', class: 'avatar-fire' };
            const icon = getCreatureIcon(h.name, h.element_id);

            return `
                <div class="hero-unlock-card ${isUnlocked ? '' : 'locked'}">
                    ${!isUnlocked ? `<span class="lock-badge">🔒 С ${h.unlock_level} ур.</span>` : ''}
                    <div class="creature-avatar ${meta.class}">
                        ${icon}
                    </div>
                    <div>
                        <strong>${h.name}</strong>
                        <div class="elem-badge ${h.element_id} text-sm">${h.element_id}</div>
                        <div class="text-dim text-sm mt-1">⚔️ ${h.base_attack} | HP ${h.base_hp}</div>
                    </div>
                </div>
            `;
        }).join('');

    } catch (e) {
        console.error('Ошибка профиля:', e);
    }
}

// =========================================================================
// ЭКРАН 3: РЕДАКТОР КОМАНДЫ И ЭВОЛЮЦИЯ
// =========================================================================
async function loadEditorData() {
    if (!state.user) return;
    try {
        const res = await fetch(`/api/player/${state.user.player_id}/creatures`);
        const creatures = await res.json();
        const container = document.getElementById('editor-creatures-grid');

        if (!creatures || creatures.length === 0) {
            container.innerHTML = '<div class="empty-state">У вас нет существ. Поймайте их на Алтаре Ловли!</div>';
            return;
        }

        container.innerHTML = creatures.map(c => {
            const meta = ELEMENT_META[c.element_id] || { icon: '⚡', class: 'avatar-fire' };
            const icon = getCreatureIcon(c.nickname || c.template_name, c.element_id);
            const inTeam = c.is_in_team === 1 || c.is_in_team === true;

            let evolveBlock = '';
            if (c.can_evolve) {
                evolveBlock = `
                    <button class="btn-evolve" onclick="evolveCreature(${c.creature_id})">
                        ✨ Эволюционировать в ${c.next_evolution_name || 'Высшую форму'}!
                    </button>
                `;
            } else if (c.evolution_level > 0) {
                evolveBlock = `<span class="text-dim text-sm">Эволюция доступна на ${c.evolution_level} ур. (текущий: ${c.level})</span>`;
            } else {
                evolveBlock = `<span class="text-dim text-sm">Максимальная ступень эволюции 👑</span>`;
            }

            return `
                <div class="editor-card ${inTeam ? 'in-team' : ''}">
                    <div class="editor-card-header">
                        <div class="creature-avatar ${meta.class}">
                            ${icon}
                        </div>
                        <div class="creature-info">
                            <div class="creature-title-row">
                                <strong>${c.template_name}</strong>
                                <span class="elem-badge ${c.element_id}">${c.element_id}</span>
                            </div>
                            <div class="text-dim text-sm">Уровень: <b>${c.level}</b> | HP: <b>${c.max_hp}</b> | ⚔️ ${c.attack} | 🛡️ ${c.defense}</div>
                        </div>
                    </div>

                    <!-- Редактор клички -->
                    <div class="nickname-edit-row">
                        <input type="text" id="nick-input-${c.creature_id}" class="nickname-input" value="${c.nickname || c.template_name}">
                        <button class="btn-sm btn-outline" onclick="saveCreatureNickname(${c.creature_id})">Сохранить кличку</button>
                    </div>

                    <!-- Управление боевым составом -->
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="text-sm">В боевом составе:</span>
                        <button class="btn-sm ${inTeam ? 'btn-outline' : 'btn-primary'}" onclick="toggleCreatureTeam(${c.creature_id}, ${!inTeam})">
                            ${inTeam ? '❌ Убрать в запас' : '⚔️ Взять в бой'}
                        </button>
                    </div>

                    <!-- Эволюция -->
                    ${evolveBlock}
                </div>
            `;
        }).join('');

    } catch (e) {
        console.error('Ошибка редактора:', e);
    }
}

async function saveCreatureNickname(creatureId) {
    const input = document.getElementById(`nick-input-${creatureId}`);
    if (!input) return;
    try {
        const res = await fetch(`/api/player/${state.user.player_id}/creatures/${creatureId}/update`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nickname: input.value.trim() })
        });
        const data = await res.json();
        if (!res.ok) alert(data.detail || 'Ошибка обновления');
        else {
            alert('Кличка успешно сохранена!');
            loadEditorData();
        }
    } catch (e) { alert(e.message); }
}

async function toggleCreatureTeam(creatureId, makeInTeam) {
    try {
        const res = await fetch(`/api/player/${state.user.player_id}/creatures/${creatureId}/update`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ is_in_team: makeInTeam })
        });
        const data = await res.json();
        if (!res.ok) alert(data.detail || data.message || 'Ошибка');
        else loadEditorData();
    } catch (e) { alert(e.message); }
}

async function evolveCreature(creatureId) {
    try {
        const res = await fetch(`/api/player/${state.user.player_id}/creatures/${creatureId}/evolve`, {
            method: 'POST'
        });
        const data = await res.json();
        if (!res.ok) alert(data.detail || data.message || 'Ошибка');
        else {
            alert(data.message);
            loadEditorData();
        }
    } catch (e) { alert(e.message); }
}

// =========================================================================
// ЭКРАН 4: АЛТАРЬ ЛОВЛИ
// =========================================================================
async function loadCatchAltarData() {
    await loadProfileSummary();
    if (state.profile) {
        document.getElementById('altar-user-coins').textContent = state.profile.coins;
    }
}

async function doCatchCreature() {
    const box = document.getElementById('catch-result-box');
    box.classList.add('hidden');
    try {
        const res = await fetch(`/api/player/${state.user.player_id}/creatures/catch`, {
            method: 'POST'
        });
        const data = await res.json();
        if (!res.ok) {
            alert(data.detail || data.message || 'Ошибка');
            return;
        }

        box.textContent = data.message;
        box.classList.remove('hidden');
        document.getElementById('altar-user-coins').textContent = data.remaining_coins;
        document.getElementById('header-coins').textContent = data.remaining_coins;
    } catch (e) { alert(e.message); }
}

// =========================================================================
// ЭКРАН 5: ПАСХАЛКА (ТАБЛИЦА УМНОЖЕНИЯ)
// =========================================================================
async function loadMathChallenge() {
    try {
        const res = await fetch('/api/training/math-challenge');
        const data = await res.json();
        state.mathNum1 = data.num1;
        state.mathNum2 = data.num2;
        document.getElementById('math-num1').textContent = data.num1;
        document.getElementById('math-num2').textContent = data.num2;
        document.getElementById('input-math-answer').value = '';
        document.getElementById('input-math-answer').focus();
    } catch (e) { console.error(e); }
}

async function handleMathSubmit(e) {
    e.preventDefault();
    const answer = parseInt(document.getElementById('input-math-answer').value);
    const feedback = document.getElementById('math-feedback');
    feedback.classList.add('hidden');

    try {
        const res = await fetch('/api/training/math-solve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                player_id: state.user.player_id,
                num1: state.mathNum1,
                num2: state.mathNum2,
                answer: answer
            })
        });
        const data = await res.json();

        if (data.correct) {
            state.mathStreak += 1;
            feedback.className = 'status-box success';
        } else {
            state.mathStreak = 0;
            feedback.className = 'status-box error';
        }

        document.getElementById('math-streak').textContent = `${state.mathStreak} 🔥`;
        feedback.textContent = data.message;
        feedback.classList.remove('hidden');

        // Обновляем статистику в шапке
        loadProfileSummary();

        // Загружаем следующий случайный пример через 1 секунду
        setTimeout(loadMathChallenge, 1200);

    } catch (e) { alert(e.message); }
}

// =========================================================================
// ЭКРАН 6: ТАБЛИЦА ЛИДЕРОВ (LEADERBOARD)
// =========================================================================
async function loadLeaderboard() {
    try {
        const res = await fetch('/api/leaderboard');
        const list = await res.json();
        const tbody = document.getElementById('leaderboard-tbody');

        tbody.innerHTML = list.map(item => {
            let rankClass = '';
            if (item.rank === 1) rankClass = 'rank-gold';
            else if (item.rank === 2) rankClass = 'rank-silver';
            else if (item.rank === 3) rankClass = 'rank-bronze';

            return `
                <tr>
                    <td class="${rankClass}">#${item.rank}</td>
                    <td><strong>${item.display_name}</strong> (${item.db_username})</td>
                    <td>Ур. ${item.level}</td>
                    <td><span class="league-pill league-${item.season_rank}">${item.season_rank}</span></td>
                    <td><b>${item.elo_rating}</b> 🛡️</td>
                    <td>${item.battles_won}W / ${item.battles_lost}L</td>
                    <td>${item.win_rate}%</td>
                </tr>
            `;
        }).join('');
    } catch (e) { console.error(e); }
}

// =========================================================================
// ЭКРАН 7: БОЕВАЯ АРЕНА (1 НА 1)
// =========================================================================
function openBattle(battleId) {
    state.battleId = battleId;
    state.selectedAttackerId = null;
    state.selectedTargetId = null;

    showScreen('screen-battle');
    document.getElementById('battle-display-id').textContent = battleId;

    pollBattleState();
    startPolling();
}

function leaveBattle() {
    stopPolling();
    state.battleId = null;
    state.selectedAttackerId = null;
    state.selectedTargetId = null;
    switchNavTab('screen-lobby');
}

function returnToLobby() {
    document.getElementById('modal-gameover').classList.add('hidden');
    leaveBattle();
}

function startPolling() {
    stopPolling();
    state.pollingTimer = setInterval(pollBattleState, 1500);
}

function stopPolling() {
    if (state.pollingTimer) {
        clearInterval(state.pollingTimer);
        state.pollingTimer = null;
    }
}

async function pollBattleState() {
    if (!state.battleId) return;
    try {
        const res = await fetch(`/api/battles/${state.battleId}`);
        if (!res.ok) return;
        const battle = await res.json();
        state.battleState = battle;
        renderBattleArena(battle);
    } catch (e) { console.error(e); }
}

function renderBattleArena(battle) {
    document.getElementById('battle-turn-num').textContent = battle.turn_number;

    const myPlayerId = state.user.player_id;
    const isP1 = (battle.player1.player_id === myPlayerId);

    const mySideCreatures = isP1 ? battle.player1_creatures : battle.player2_creatures;
    const enemySideCreatures = isP1 ? battle.player2_creatures : battle.player1_creatures;

    const myName = isP1 ? battle.player1.display_name : (battle.player2 ? battle.player2.display_name : 'Вы');
    const enemyName = isP1 ? (battle.player2 ? battle.player2.display_name : 'Ожидание соперника...') : battle.player1.display_name;

    document.getElementById('player-name').textContent = myName + ' (Ваша команда)';
    document.getElementById('opponent-name').textContent = enemyName;

    const turnIndicator = document.getElementById('battle-turn-indicator');
    const isMyTurn = (battle.current_turn_player_id === myPlayerId && battle.status === 'IN_PROGRESS');

    if (battle.status === 'WAITING') {
        turnIndicator.className = 'turn-indicator';
        turnIndicator.textContent = '⏳ Ожидание подключения второго игрока...';
    } else if (battle.status === 'FINISHED') {
        turnIndicator.className = 'turn-indicator';
        turnIndicator.textContent = '🏁 Битва завершена!';
    } else if (isMyTurn) {
        turnIndicator.className = 'turn-indicator my-turn';
        turnIndicator.textContent = '⚡ ВАШ ХОД! Выберите атакующего и цель';
    } else {
        turnIndicator.className = 'turn-indicator enemy-turn';
        turnIndicator.textContent = '🛡️ Ход соперника... Ожидайте';
    }

    renderCreaturesGrid('player-creatures-grid', mySideCreatures, true);
    renderCreaturesGrid('opponent-creatures-grid', enemySideCreatures, false);
    renderCombatLog(battle.turns);

    if (battle.status === 'FINISHED') {
        stopPolling();
        showGameOverModal(battle.winner_id === myPlayerId);
    }

    updateActionButtons(isMyTurn, mySideCreatures, enemySideCreatures);
}

function renderCreaturesGrid(elementId, creatures, isPlayerSide) {
    const container = document.getElementById(elementId);
    if (!creatures || creatures.length === 0) {
        container.innerHTML = `<div class="empty-state">${isPlayerSide ? 'Нет существ' : 'Ожидание соперника...'}</div>`;
        return;
    }

    container.innerHTML = creatures.map(c => {
        const isFainted = c.is_fainted === 1 || c.current_hp <= 0;
        const hpPercent = Math.max(0, Math.min(100, Math.round((c.current_hp / c.max_hp) * 100)));
        let hpClass = '';
        if (hpPercent <= 25) hpClass = 'hp-low';
        else if (hpPercent <= 50) hpClass = 'hp-mid';

        const isSelected = isPlayerSide 
            ? (state.selectedAttackerId === c.battle_creature_id)
            : (state.selectedTargetId === c.battle_creature_id);

        const selectClass = isSelected ? (isPlayerSide ? 'selected-attacker' : 'selected-target') : '';
        const faintedClass = isFainted ? 'fainted' : '';
        const meta = ELEMENT_META[c.element_id] || { icon: '⚡', class: 'avatar-fire' };
        const creatureIcon = getCreatureIcon(c.name, c.element_id);

        return `
            <div class="arena-card ${selectClass} ${faintedClass}" 
                 onclick="handleCreatureSelect(${c.battle_creature_id}, ${isPlayerSide}, ${isFainted})">
                ${isFainted ? '<div class="fainted-overlay">ПОВЕРЖЕН</div>' : ''}
                <div class="creature-avatar ${meta.class}">
                    ${creatureIcon}
                </div>
                <div class="arena-card-body">
                    <div class="arena-card-header">
                        <span class="arena-card-name">${c.name}</span>
                        <span class="elem-badge ${c.element_id}">${c.element_id}</span>
                    </div>
                    <div class="hp-bar-container">
                        <div class="hp-labels">
                            <span>HP</span>
                            <span>${c.current_hp} / ${c.max_hp} (${hpPercent}%)</span>
                        </div>
                        <div class="hp-track">
                            <div class="hp-fill ${hpClass}" style="width: ${hpPercent}%"></div>
                        </div>
                    </div>
                    <div class="creature-stats-row">
                        <span>⚔️ ${c.attack}</span>
                        <span>🛡️ ${c.defense}</span>
                        <span>⚡ ${c.speed}</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function handleCreatureSelect(creatureId, isPlayerSide, isFainted) {
    if (isFainted) return;
    if (isPlayerSide) state.selectedAttackerId = creatureId;
    else state.selectedTargetId = creatureId;

    if (state.battleState) renderBattleArena(state.battleState);
}

function updateActionButtons(isMyTurn, myCreatures, enemyCreatures) {
    const btnAttack = document.getElementById('btn-action-attack');
    const btnHeal = document.getElementById('btn-action-heal');
    const btnSurrenderAction = document.getElementById('btn-action-surrender');
    const hint = document.getElementById('selected-creatures-hint');
    const preview = document.getElementById('elem-preview-text');

    // Проверяем живы ли текущие выбранные существа, иначе автоматически переключаем
    let attacker = myCreatures?.find(c => c.battle_creature_id === state.selectedAttackerId);
    if (!attacker || attacker.is_fainted || attacker.current_hp <= 0) {
        const firstAlive = myCreatures?.find(c => !c.is_fainted && c.current_hp > 0);
        state.selectedAttackerId = firstAlive ? firstAlive.battle_creature_id : null;
        attacker = firstAlive;
    }

    let target = enemyCreatures?.find(c => c.battle_creature_id === state.selectedTargetId);
    if (!target || target.is_fainted || target.current_hp <= 0) {
        const firstEnemyAlive = enemyCreatures?.find(c => !c.is_fainted && c.current_hp > 0);
        state.selectedTargetId = firstEnemyAlive ? firstEnemyAlive.battle_creature_id : null;
        target = firstEnemyAlive;
    }

    if (attacker && target) {
        hint.textContent = `Атакующий: ${attacker.name} ➔ Цель: ${target.name}`;
        const mult = getPreviewMultiplier(attacker.element_id, target.element_id);
        if (mult >= 1.4) {
            preview.textContent = `Бонус стихии: x${mult} (Сверхэффективно!) 🔥`;
        } else if (mult <= 0.75) {
            preview.textContent = `Штраф стихии: x${mult} (Слабая атака) 🛡️`;
        } else {
            preview.textContent = `Стандартный урон: x${mult}`;
        }
    } else {
        hint.textContent = 'Выберите атакующее существо и цель для удара';
        preview.textContent = 'Урон с учётом стихий';
    }

    const canAttack = isMyTurn && attacker && target && !attacker.is_fainted && !target.is_fainted;
    btnAttack.disabled = !canAttack;
    btnHeal.disabled = !isMyTurn || !attacker;
    if (btnSurrenderAction) {
        btnSurrenderAction.disabled = (state.battleState?.status === 'FINISHED');
    }
}

function getPreviewMultiplier(atkElem, defElem) {
    const matrix = {
        FIRE: { GRASS: 1.5, WATER: 0.7, EARTH: 1.1, FIRE: 1.0 },
        GRASS: { WATER: 1.5, EARTH: 1.4, FIRE: 0.7, GRASS: 1.0 },
        WATER: { FIRE: 1.5, EARTH: 1.2, GRASS: 0.7, WATER: 1.0 },
        EARTH: { FIRE: 1.4, GRASS: 0.7, WATER: 1.0, EARTH: 1.0 }
    };
    return matrix[atkElem]?.[defElem] || 1.0;
}

function renderCombatLog(turns) {
    const container = document.getElementById('combat-log-content');
    if (!turns || turns.length === 0) {
        container.innerHTML = '<div class="log-entry system">Бой начался!</div>';
        return;
    }

    container.innerHTML = turns.map(t => {
        let entryClass = 'hit';
        if (!t.is_hit) entryClass = 'miss';
        else if (t.is_critical) entryClass = 'crit';

        return `
            <div class="log-entry ${entryClass}">
                <strong>[Ход ${t.turn_number}]</strong> ${t.message}
            </div>
        `;
    }).join('');
}

async function executeAttack() {
    if (!state.battleId || !state.selectedAttackerId || !state.selectedTargetId) return;
    const btnAttack = document.getElementById('btn-action-attack');
    btnAttack.disabled = true;

    try {
        const res = await fetch(`/api/battles/${state.battleId}/attack`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                actor_player_id: state.user.player_id,
                actor_creature_id: state.selectedAttackerId,
                target_creature_id: state.selectedTargetId,
                action_type: 'ELEMENTAL_ATTACK'
            })
        });

        const data = await res.json();
        if (!res.ok) {
            alert(data.detail || 'Не удалось совершить атаку');
            return;
        }

        await pollBattleState();
    } catch (e) { alert('Ошибка атаки: ' + e.message); }
}

async function useHealItem() {
    if (!state.battleId || !state.selectedAttackerId) return;

    try {
        const res = await fetch(`/api/battles/${state.battleId}/use_item`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                player_id: state.user.player_id,
                item_id: 1,
                target_creature_id: state.selectedAttackerId
            })
        });

        const data = await res.json();
        if (!res.ok) {
            alert(data.detail || 'Ошибка');
            return;
        }

        alert(data.message);
        await pollBattleState();
    } catch (e) { alert('Ошибка зелья: ' + e.message); }
}

async function surrenderBattle() {
    if (!state.battleId || !state.user) return;

    // Если бой в режиме ожидания (соперник ещё не зашёл)
    if (state.battleState && state.battleState.status === 'WAITING') {
        const confCancel = confirm('Соперник ещё не подключился. Отменить поиск боя?');
        if (!confCancel) return;
        try {
            await fetch(`/api/battles/${state.battleId}/surrender`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ player_id: state.user.player_id })
            });
            leaveBattle();
            return;
        } catch (e) {
            leaveBattle();
            return;
        }
    }

    const confirmed = confirm('Вы действительно хотите сдаться досрочно? Вам будет засчитано гарантированное поражение со снижением рейтинга Elo.');
    if (!confirmed) return;

    try {
        const res = await fetch(`/api/battles/${state.battleId}/surrender`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player_id: state.user.player_id })
        });
        const data = await res.json();
        if (!res.ok) {
            alert(data.detail || 'Не удалось сдаться');
            return;
        }

        stopPolling();
        await pollBattleState();
        showGameOverModal(false);
    } catch (e) {
        alert('Ошибка при сдаче боя: ' + e.message);
    }
}

function showGameOverModal(isWinner) {
    const modal = document.getElementById('modal-gameover');
    const title = document.getElementById('gameover-title');
    const icon = document.getElementById('gameover-icon');
    const desc = document.getElementById('gameover-desc');
    const stats = modal.querySelector('.modal-stats');

    if (isWinner) {
        icon.textContent = '🏆';
        title.textContent = 'Славная Победа!';
        title.style.color = '#34d399';
        desc.textContent = 'Все существа противника повержены! Результаты зафиксированы в БД Oracle.';
        if (stats) {
            stats.innerHTML = '<div>+120 EXP</div><div>+60 Монет 🪙</div><div>+25 Elo 🛡️</div>';
        }
    } else {
        icon.textContent = '💀';
        title.textContent = 'Поражение';
        title.style.color = '#f87171';
        desc.textContent = 'Бой завершился поражением. Тренируйтесь в Академии и возвращайтесь сильнее!';
        if (stats) {
            stats.innerHTML = '<div style="color: #94a3b8">+35 EXP</div><div style="color: #f87171">-25 Elo 🛡️</div>';
        }
    }

    modal.classList.remove('hidden');
}

