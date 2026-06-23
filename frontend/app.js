onst state = {
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